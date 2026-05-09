"""
NeXifyAI — Runtime Connectivity (Oracle Core: /core/runtime)

NOT: isolated services pinging themselves
BUT:  governed service mesh with health, readiness, dependency contracts

THE CRITICAL LAYER: Without this, Hermes runs isolated. No Enterprise Runtime.

Components:
  - Service Registry (what runs where)
  - Health Checks (per-service, multi-observer)
  - Dependency Map (what needs what)
  - Readiness Gates (all deps healthy → green)
  - Circuit Breaker (downstream failure → stop)
  - Event Federation (Cognitive Bus — ALL systems publish events)
"""
import json
import time
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPED = "stopped"

class CheckType(Enum):
    HTTP = "http"
    TCP = "tcp"
    DOCKER = "docker"
    PROCESS = "process"
    INTERNAL = "internal"

@dataclass
class ServiceEndpoint:
    """How to reach a service."""
    name: str
    url: str = ""
    host: str = "localhost"
    port: int = 0
    check_type: CheckType = CheckType.HTTP
    check_path: str = "/health"
    timeout_ms: int = 5000
    required: bool = True
    tags: List[str] = field(default_factory=list)

@dataclass
class ServiceNode:
    """A registered service in the runtime."""
    service_id: str
    name: str
    description: str = ""
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # service_ids
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: float = 0.0
    check_count: int = 0
    fail_count: int = 0
    consecutive_failures: int = 0
    circuit_open: bool = False
    circuit_opened_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def health_score(self) -> float:
        if self.check_count == 0:
            return 0.0
        return (self.check_count - self.fail_count) / self.check_count


# ═══════════════════════════════════════════════════
# SERVICE REGISTRY
# ═══════════════════════════════════════════════════

class ServiceRegistry:
    """
    Central service registry — what runs where, what depends on what.

    Every service in the NeXifyAI runtime is registered here.
    """

    def __init__(self):
        self.services: Dict[str, ServiceNode] = {}
        self._register_standard_services()

    def _register_standard_services(self):
        """Register all known NeXifyAI services."""
        services = [
            ServiceNode("backend", "Backend API",
                "FastAPI backend on VPS port 8001",
                endpoints=[
                    ServiceEndpoint("backend-health", url="http://localhost:8001", port=8001,
                                   check_path="/api/health", tags=["api", "critical"]),
                ],
                dependencies=["supabase", "redis"],
            ),
            ServiceNode("frontend", "Frontend SPA",
                "React SPA on Vercel",
                endpoints=[
                    ServiceEndpoint("frontend-vercel", url="https://www.nexify-automate.com",
                                   check_path="/", check_type=CheckType.HTTP, tags=["web", "critical"]),
                ],
                dependencies=["backend"],
            ),
            ServiceNode("supabase", "Supabase Database",
                "Self-hosted Supabase (PostgreSQL + PostgREST + Auth)",
                endpoints=[
                    ServiceEndpoint("supabase-api", url="http://localhost:8002",
                                   check_path="/rest/v1/", tags=["database", "critical"]),
                    ServiceEndpoint("supabase-db", host="localhost", port=5433,
                                   check_type=CheckType.TCP, tags=["database", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("qdrant", "Qdrant Vector Store",
                "Vector embeddings + semantic search",
                endpoints=[
                    ServiceEndpoint("qdrant-api", url="http://localhost:6333",
                                   check_path="/health", tags=["brain", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("redis", "Redis Cache",
                "Session cache + pub/sub",
                endpoints=[
                    ServiceEndpoint("redis-tcp", host="localhost", port=6379,
                                   check_type=CheckType.TCP, tags=["cache"]),
                ],
                dependencies=[],
            ),
            ServiceNode("brain", "Brain DB",
                "SQLite Brain (local) — source of truth",
                endpoints=[
                    ServiceEndpoint("brain-db", url="file:///opt/data/brain/brain.db",
                                   check_type=CheckType.INTERNAL, tags=["brain", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("hermes-agent", "Hermes Agent",
                "AI Agent runtime (CLI + Gateway)",
                endpoints=[
                    ServiceEndpoint("hermes-gateway", host="localhost", port=2226,
                                   check_type=CheckType.TCP, tags=["agent", "critical"]),
                ],
                dependencies=["brain", "openrouter"],
            ),
            ServiceNode("openrouter", "OpenRouter API",
                "LLM API gateway (DeepSeek)",
                endpoints=[
                    ServiceEndpoint("openrouter-api", url="https://openrouter.ai/api/v1",
                                   check_path="/models", check_type=CheckType.HTTP, tags=["ai", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("vercel", "Vercel Platform",
                "Frontend hosting + deployment",
                endpoints=[
                    ServiceEndpoint("vercel-api", url="https://api.vercel.com",
                                   check_path="/v9/projects", check_type=CheckType.HTTP, tags=["deploy", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("github", "GitHub Platform",
                "Code hosting + CI/CD",
                endpoints=[
                    ServiceEndpoint("github-api", url="https://api.github.com",
                                   check_type=CheckType.HTTP, tags=["code", "critical"]),
                ],
                dependencies=[],
            ),
            ServiceNode("open-notebook", "Open Notebook",
                "Enterprise Oracle + Knowledge Base",
                endpoints=[
                    ServiceEndpoint("open-notebook-api", url="http://localhost:32770",
                                   check_path="/api/sources", check_type=CheckType.HTTP, tags=["knowledge"]),
                ],
                dependencies=["qdrant"],
            ),
            ServiceNode("paperclip", "Paperclip Agent Hub",
                "Agent management + skills",
                endpoints=[
                    ServiceEndpoint("paperclip-api", url="https://srv1243952.hstgr.cloud",
                                   check_path="/api/health", check_type=CheckType.HTTP, tags=["agent"]),
                ],
                dependencies=[],
            ),
            ServiceNode("slack", "Slack Communication",
                "Team communication + alerts",
                endpoints=[
                    ServiceEndpoint("slack-api", url="https://slack.com/api",
                                   check_path="/auth.test", check_type=CheckType.HTTP, tags=["communication"]),
                ],
                dependencies=[],
            ),
            ServiceNode("traefik", "Traefik Proxy",
                "Reverse proxy + SSL termination",
                endpoints=[
                    ServiceEndpoint("traefik-api", host="localhost", port=8080,
                                   check_type=CheckType.TCP, tags=["infra"]),
                ],
                dependencies=[],
            ),
            ServiceNode("umami", "Umami Analytics",
                "Web analytics",
                endpoints=[
                    ServiceEndpoint("umami-api", url="http://localhost:3001",
                                   check_type=CheckType.HTTP, tags=["analytics"]),
                ],
                dependencies=["supabase"],
            ),
        ]

        for svc in services:
            self.services[svc.service_id] = svc

    def get_dependency_chain(self, service_id: str) -> List[str]:
        """Get the full dependency chain for a service (recursive)."""
        chain = []
        visited = set()

        def traverse(sid):
            if sid in visited:
                return
            visited.add(sid)
            svc = self.services.get(sid)
            if svc:
                chain.append(sid)
                for dep in svc.dependencies:
                    traverse(dep)

        traverse(service_id)
        return chain

    def get_dependents(self, service_id: str) -> List[str]:
        """Get all services that depend on this one."""
        return [
            sid for sid, svc in self.services.items()
            if service_id in svc.dependencies
        ]

    def get_critical_services(self) -> List[ServiceNode]:
        """Get all services tagged as critical."""
        return [
            svc for svc in self.services.values()
            if any("critical" in ep.tags for ep in svc.endpoints)
        ]


# ═══════════════════════════════════════════════════
# HEALTH CHECK ENGINE
# ═══════════════════════════════════════════════════

class HealthCheckEngine:
    """
    Multi-observer health checking.

    Each service can be checked from multiple observation points.
    Health is a projection, not reality — but this is the most accurate
    projection we can get without being in the service itself.
    """

    def __init__(self, registry: ServiceRegistry = None):
        self.registry = registry or ServiceRegistry()
        self.check_history: List[Dict[str, Any]] = []
        self._circuit_breaker_threshold = 5  # Consecutive failures before open

    def check_service(self, service_id: str) -> Dict[str, Any]:
        """Run health checks on a single service."""
        svc = self.registry.services.get(service_id)
        if not svc:
            return {"service": service_id, "status": "unknown", "error": "Not registered"}

        results = []
        for ep in svc.endpoints:
            try:
                result = self._check_endpoint(ep)
                results.append({"endpoint": ep.name, **result})
            except Exception as e:
                results.append({"endpoint": ep.name, "healthy": False, "error": str(e)})

        all_healthy = all(r.get("healthy", False) for r in results)
        svc.check_count += 1

        if all_healthy:
            svc.status = ServiceStatus.HEALTHY
            svc.fail_count = max(0, svc.fail_count - 1)
            svc.consecutive_failures = 0
        else:
            svc.fail_count += 1
            svc.consecutive_failures += 1
            if svc.consecutive_failures >= self._circuit_breaker_threshold:
                svc.status = ServiceStatus.UNHEALTHY
                if not svc.circuit_open:
                    svc.circuit_open = True
                    svc.circuit_opened_at = time.time()
            else:
                svc.status = ServiceStatus.DEGRADED

        svc.last_check = time.time()

        entry = {
            "service": service_id,
            "status": svc.status.value,
            "health_score": svc.health_score,
            "circuit_open": svc.circuit_open,
            "endpoints": results,
            "timestamp": time.time(),
        }
        self.check_history.append(entry)
        return entry

    def check_all(self) -> Dict[str, Any]:
        """Run health checks on all registered services."""
        results = {}
        for sid in self.registry.services:
            results[sid] = self.check_service(sid)

        healthy = sum(1 for r in results.values() if r["status"] == "healthy")
        total = len(results)
        score = (healthy / total * 100) if total > 0 else 0

        return {
            "timestamp": time.time(),
            "score": round(score, 1),
            "healthy": healthy,
            "total": total,
            "services": results,
        }

    def check_readiness(self, service_id: str) -> Dict[str, Any]:
        """
        Check if a service is READY — all dependencies healthy.
        This is the Readiness Gate for CI/CD.
        """
        svc = self.registry.services.get(service_id)
        if not svc:
            return {"ready": False, "error": "Not registered"}

        # Check self
        self.check_service(service_id)

        # Check all dependencies
        dep_status = {}
        for dep_id in svc.dependencies:
            self.check_service(dep_id)
            dep_svc = self.registry.services.get(dep_id)
            dep_status[dep_id] = dep_svc.status.value if dep_svc else "unknown"

        deps_healthy = all(
            s == ServiceStatus.HEALTHY.value for s in dep_status.values()
        )

        return {
            "service": service_id,
            "ready": svc.status == ServiceStatus.HEALTHY and deps_healthy,
            "self_status": svc.status.value,
            "dependencies": dep_status,
            "all_deps_healthy": deps_healthy,
            "circuit_open": svc.circuit_open,
        }

    def _check_endpoint(self, ep: ServiceEndpoint) -> Dict[str, Any]:
        """Check a single endpoint."""
        if ep.check_type == CheckType.HTTP:
            return self._http_check(ep)
        elif ep.check_type == CheckType.TCP:
            return self._tcp_check(ep)
        elif ep.check_type == CheckType.INTERNAL:
            return self._internal_check(ep)
        return {"healthy": False, "error": f"Unknown check type: {ep.check_type}"}

    def _http_check(self, ep: ServiceEndpoint) -> Dict[str, Any]:
        """HTTP health check."""
        try:
            url = f"{ep.url}{ep.check_path}" if ep.url.startswith("http") else f"http://{ep.host}:{ep.port}{ep.check_path}"
            req = urllib.request.Request(url, headers={"User-Agent": "NeXifyAI-HealthCheck/1.0"})
            resp = urllib.request.urlopen(req, timeout=ep.timeout_ms / 1000)
            return {"healthy": resp.status == 200, "status_code": resp.status,
                    "latency_ms": 0, "url": url}
        except Exception as e:
            return {"healthy": False, "error": str(e)[:100]}

    def _tcp_check(self, ep: ServiceEndpoint) -> Dict[str, Any]:
        """TCP port check."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(ep.timeout_ms / 1000)
            result = sock.connect_ex((ep.host, ep.port))
            sock.close()
            return {"healthy": result == 0, "host": ep.host, "port": ep.port}
        except Exception as e:
            return {"healthy": False, "error": str(e)[:100]}

    def _internal_check(self, ep: ServiceEndpoint) -> Dict[str, Any]:
        """Internal file/process check."""
        path = ep.url.replace("file://", "")
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        return {"healthy": exists and size > 0, "path": path, "size_bytes": size}


# ═══════════════════════════════════════════════════
# RUNTIME CONNECTIVITY ORCHESTRATOR
# ═══════════════════════════════════════════════════

class RuntimeOrchestrator:
    """
    Central runtime connectivity orchestrator.

    Combines: Service Registry + Health Checks + Dependency Map + Circuit Breakers
    Provides: Ready Gates, Health Dashboard, Dependency Validation
    """

    def __init__(self):
        self.registry = ServiceRegistry()
        self.health = HealthCheckEngine(self.registry)

    def ready_gate(self, service_id: str) -> Dict[str, Any]:
        """
        Full readiness check — service + all transitive dependencies.

        This is the gate that CI/CD should use before proceeding.
        """
        # Get full dependency chain
        chain = self.registry.get_dependency_chain(service_id)

        # Check each service in the chain
        results = {}
        for sid in chain:
            results[sid] = self.health.check_readiness(sid)

        all_ready = all(r["ready"] for r in results.values())

        return {
            "target": service_id,
            "all_ready": all_ready,
            "dependency_chain": chain,
            "services": results,
            "timestamp": time.time(),
        }

    def health_dashboard(self) -> Dict[str, Any]:
        """Full system health dashboard."""
        health = self.health.check_all()
        critical = self.registry.get_critical_services()

        return {
            "timestamp": health["timestamp"],
            "overall_score": health["score"],
            "healthy_count": health["healthy"],
            "total_count": health["total"],
            "critical_services_healthy": sum(
                1 for s in critical if s.status == ServiceStatus.HEALTHY
            ),
            "critical_services_total": len(critical),
            "circuits_open": sum(
                1 for s in self.registry.services.values() if s.circuit_open
            ),
            "services": {
                sid: {
                    "status": svc.status.value,
                    "health_score": svc.health_score,
                    "dependencies": svc.dependencies,
                    "dependents": self.registry.get_dependents(sid),
                    "circuit_open": svc.circuit_open,
                }
                for sid, svc in self.registry.services.items()
            },
        }


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_orchestrator: Optional[RuntimeOrchestrator] = None

def get_orchestrator() -> RuntimeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RuntimeOrchestrator()
    return _orchestrator
