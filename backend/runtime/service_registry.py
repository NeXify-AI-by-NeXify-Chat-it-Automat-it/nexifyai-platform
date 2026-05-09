"""
NeXifyAI — Canonical Service Registry (E2.1)
Single source of truth for all runtime components.

Every service is a ServiceNode with:
- Canonical endpoint (how to verify it's actually running)
- Internal/external endpoints (per observer position)
- Dependencies (what must be up first)
- Health projections (what each observer currently reports)
- Recovery paths (how to restore reachability)
- Source of truth (which check definitively answers "is it running?")
- Validation method (how to verify truth)

NO implicit localhost assumptions. Every endpoint is explicitly qualified.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ObserverPosition(Enum):
    HERMES_CONTAINER = "hermes-container"
    VPS_HOST = "vps-host"
    EXTERNAL = "external"


class EndpointType(Enum):
    CANONICAL = "canonical"       # The definitive check: docker ps / systemctl
    INTERNAL = "internal"         # Within Docker network
    HOST_LOCAL = "host-local"     # localhost on VPS
    EXTERNAL = "external"         # Internet-reachable
    CONTAINER_LOCAL = "container-local"  # localhost within container


@dataclass
class ServiceEndpoint:
    """A single endpoint for a service, qualified by observer position."""
    url: str
    type: EndpointType
    observer: ObserverPosition
    protocol: str  # "http", "https", "tcp", "systemctl", "docker-exec"
    expected_response: str = ""  # What indicates "healthy" (e.g., "200", "PONG", "active")
    is_reachable: Optional[bool] = None  # Last probe result
    last_probed: float = 0.0
    error: Optional[str] = None


@dataclass
class ServiceNode:
    """A runtime component registered in the canonical service registry."""
    id: str
    service_type: str  # "vector-db", "cache", "backend", "database", "proxy", "agent", "notebook", "crm"
    
    # Canonical truth source
    source_of_truth: str  # systemctl is-active / docker ps filter / curl health
    source_of_truth_command: str  # The exact command to verify
    
    # Endpoints (qualified by observer)
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Service IDs that must be up first
    
    # Health projections (what each observer sees)
    health_projections: Dict[str, str] = field(default_factory=dict)  # observer → "healthy"/"degraded"/"down"/"unknown"
    
    # Recovery
    recovery_command: str = ""
    recovery_validation: str = ""
    
    # Metadata
    container_name: str = ""
    docker_network: str = ""
    host_port: str = ""
    systemd_unit: str = ""
    runtime: str = ""  # "docker", "systemd", "both"
    
    # State
    is_canonically_running: Optional[bool] = None
    last_canonical_check: float = 0.0
    
    def canonical_endpoint(self) -> Optional[ServiceEndpoint]:
        for ep in self.endpoints:
            if ep.type == EndpointType.CANONICAL:
                return ep
        return None
    
    def reachable_from(self, observer: ObserverPosition) -> List[ServiceEndpoint]:
        return [ep for ep in self.endpoints if ep.observer == observer and ep.is_reachable]
    
    def unreachable_from(self, observer: ObserverPosition) -> List[ServiceEndpoint]:
        return [ep for ep in self.endpoints if ep.observer == observer and ep.is_reachable is False]


# ══════════════════════════════════════════════
# CANONICAL SERVICE REGISTRY (hard data from E1)
# ══════════════════════════════════════════════

CANONICAL_REGISTRY: Dict[str, ServiceNode] = {
    "qdrant-primary": ServiceNode(
        id="qdrant-primary",
        service_type="vector-db",
        source_of_truth="docker ps",
        source_of_truth_command="docker ps --filter name=nexifyai-qdrant --format '{{.Status}}' | grep Up",
        container_name="nexifyai-qdrant",
        docker_network="bridge + supabase_default",
        host_port="127.0.0.1:6333-6334 ⚠️ HOST-LOCAL ONLY",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker ps --filter name=nexifyai-qdrant", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "Up"),
            ServiceEndpoint("http://localhost:6333/collections", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "http", "200"),
            ServiceEndpoint("http://qdrant-vjfp-qdrant-1:6333/collections", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "http", "200"),
            ServiceEndpoint("http://72.62.152.47:32769/collections", EndpointType.EXTERNAL, ObserverPosition.EXTERNAL, "http", "200"),
        ],
        depends_on=[],
        health_projections={
            "vps-host": "healthy",
            "hermes-container": "unreachable (container DNS → host-local port not routable)",
            "health-v2": "down (False-Positive durch Netzwerk-Isolation)",
        },
        recovery_command="docker restart nexifyai-qdrant",
        recovery_validation="curl -sf http://localhost:6333/collections",
    ),
    "qdrant-vjfp": ServiceNode(
        id="qdrant-vjfp",
        service_type="vector-db",
        source_of_truth="docker ps",
        source_of_truth_command="docker ps --filter name=qdrant-vjfp-qdrant-1 --format '{{.Status}}' | grep Up",
        container_name="qdrant-vjfp-qdrant-1",
        docker_network="qdrant-vjfp_default",
        host_port="0.0.0.0:32769→6333",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker ps --filter name=qdrant-vjfp-qdrant-1", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "Up"),
            ServiceEndpoint("http://localhost:32769/collections", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "http", "200"),
            ServiceEndpoint("http://qdrant-vjfp-qdrant-1:6333/collections", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "http", "200 (⚠️ returns 401)"),
            ServiceEndpoint("http://72.62.152.47:32769/collections", EndpointType.EXTERNAL, ObserverPosition.EXTERNAL, "http", "200"),
        ],
        depends_on=[],
        health_projections={
            "vps-host": "healthy (but 401)",
            "hermes-container": "reachable (but 401 — auth required)",
        },
        recovery_command="docker restart qdrant-vjfp-qdrant-1",
        recovery_validation="curl -sf http://localhost:32769/collections",
    ),
    "redis": ServiceNode(
        id="redis",
        service_type="cache",
        source_of_truth="docker exec",
        source_of_truth_command="docker exec honcho-redis-1 redis-cli PING",
        container_name="honcho-redis-1",
        docker_network="honcho_honcho-network ONLY ⚠️ NO HOST PORT MAPPING",
        host_port="6379 (intern, kein -p)",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker exec honcho-redis-1 redis-cli PING", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "PONG"),
            ServiceEndpoint("tcp://honcho-redis-1:6379", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "tcp", "connected"),
            ServiceEndpoint("tcp://localhost:6379", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "tcp", "⚠️ unreachable (no port mapping)"),
        ],
        depends_on=[],
        health_projections={
            "vps-host": "unreachable (kein Host-Port-Mapping)",
            "hermes-container": "healthy (gleiches honcho-Netzwerk)",
        },
        recovery_command="docker restart honcho-redis-1",
        recovery_validation="docker exec honcho-redis-1 redis-cli PING",
    ),
    "backend": ServiceNode(
        id="backend",
        service_type="backend",
        source_of_truth="systemctl",
        source_of_truth_command="systemctl is-active nexifyai-backend",
        systemd_unit="nexifyai-backend.service",
        host_port="8001 (systemd, kein Docker)",
        runtime="systemd",
        endpoints=[
            ServiceEndpoint("systemctl is-active nexifyai-backend", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "systemctl", "active"),
            ServiceEndpoint("http://localhost:8001/api/health/live", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "http", "200"),
            ServiceEndpoint("http://172.17.0.1:8001/api/health/live", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "http", "200 (⚠️ returns 404 — endpoint path)"),
            ServiceEndpoint("https://www.nexify-automate.com/api/health/live", EndpointType.EXTERNAL, ObserverPosition.EXTERNAL, "https", "200"),
        ],
        depends_on=["redis", "supabase-db"],
        health_projections={
            "vps-host": "healthy",
            "hermes-container": "reachable but 404 (health v2 endpoint not deployed at /api/health/live)",
        },
        recovery_command="systemctl restart nexifyai-backend",
        recovery_validation="curl -sf http://localhost:8001/api/health/v2",
    ),
    "supabase-db": ServiceNode(
        id="supabase-db",
        service_type="database",
        source_of_truth="docker exec",
        source_of_truth_command="docker exec supabase-db pg_isready -U postgres",
        container_name="supabase-db",
        docker_network="supabase_default",
        host_port="5432 (intern) — Pooler: 0.0.0.0:6543, 127.0.0.1:5435",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker exec supabase-db pg_isready -U postgres", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "accepting connections"),
            ServiceEndpoint("tcp://supabase-db:5432", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "tcp", "connected (⚠️ container refused)"),
            ServiceEndpoint("http://localhost:6543", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "http", "200"),
        ],
        depends_on=[],
        health_projections={
            "vps-host": "healthy (pooler:6543 erreichbar)",
            "hermes-container": "unreachable (supabase-db:5432 connection refused)",
        },
        recovery_command="docker restart supabase-db",
        recovery_validation="docker exec supabase-db pg_isready -U postgres",
    ),
    "traefik": ServiceNode(
        id="traefik",
        service_type="proxy",
        source_of_truth="docker ps",
        source_of_truth_command="docker ps --filter name=traefik-tcja-traefik-1 --format '{{.Status}}' | grep Up",
        container_name="traefik-tcja-traefik-1",
        docker_network="host",
        host_port="80/443 (host network)",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker ps --filter name=traefik-tcja-traefik-1", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "Up"),
            ServiceEndpoint("https://www.nexify-automate.com", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "https", "200"),
            ServiceEndpoint("https://www.nexify-automate.com", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "https", "200"),
            ServiceEndpoint("https://www.nexify-automate.com", EndpointType.EXTERNAL, ObserverPosition.EXTERNAL, "https", "200"),
        ],
        depends_on=["backend"],
        health_projections={
            "all": "healthy (62ms, external URL works from all observers)",
        },
        recovery_command="docker restart traefik-tcja-traefik-1",
        recovery_validation="curl -sf https://www.nexify-automate.com",
    ),
    "paperclip": ServiceNode(
        id="paperclip",
        service_type="crm",
        source_of_truth="docker ps",
        source_of_truth_command="docker ps --filter name=paperclip-etdf-paperclip-1 --format '{{.Status}}' | grep Up",
        container_name="paperclip-etdf-paperclip-1",
        docker_network="hermes-mem0-integrated_mem0-network + paperclip-etdf_default",
        host_port="0.0.0.0:47967→3100",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker ps --filter name=paperclip-etdf-paperclip-1", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "Up"),
            ServiceEndpoint("http://localhost:47967", EndpointType.HOST_LOCAL, ObserverPosition.VPS_HOST, "http", "200"),
            ServiceEndpoint("http://paperclip-etdf-paperclip-1:3100", EndpointType.INTERNAL, ObserverPosition.HERMES_CONTAINER, "http", "200"),
            ServiceEndpoint("http://72.62.152.47:47967", EndpointType.EXTERNAL, ObserverPosition.EXTERNAL, "http", "200"),
        ],
        depends_on=[],
        health_projections={
            "all": "healthy (3ms from container)",
        },
        recovery_command="docker restart paperclip-etdf-paperclip-1",
        recovery_validation="curl -sf http://localhost:47967",
    ),
    "hermes-agent": ServiceNode(
        id="hermes-agent",
        service_type="agent",
        source_of_truth="docker ps",
        source_of_truth_command="docker ps --filter name=hermes-agent-ofbh-hermes-agent-1 --format '{{.Status}}' | grep Up",
        container_name="hermes-agent-ofbh-hermes-agent-1",
        docker_network="6 networks: openmemory, qdrant-vjfp, supabase, mem0-integrated, honcho, mem0-stack",
        host_port="— (kein Host-Port, interne Agent-Runtime)",
        runtime="docker",
        endpoints=[
            ServiceEndpoint("docker ps --filter name=hermes-agent-ofbh-hermes-agent-1", EndpointType.CANONICAL, ObserverPosition.VPS_HOST, "docker-exec", "Up"),
        ],
        depends_on=["redis", "qdrant-primary", "qdrant-vjfp", "supabase-db", "backend"],
        health_projections={
            "vps-host": "healthy (19+ containers visible)",
        },
        recovery_command="docker restart hermes-agent-ofbh-hermes-agent-1",
        recovery_validation="docker ps --filter name=hermes-agent",
    ),
}


def get_registry() -> Dict[str, ServiceNode]:
    """Return the canonical service registry."""
    return CANONICAL_REGISTRY


def get_service(service_id: str) -> Optional[ServiceNode]:
    """Get a single service by ID."""
    return CANONICAL_REGISTRY.get(service_id)


def get_services_by_type(service_type: str) -> List[ServiceNode]:
    return [s for s in CANONICAL_REGISTRY.values() if s.service_type == service_type]


def get_running_services() -> List[str]:
    """Return IDs of services that are canonically running."""
    return [s.id for s in CANONICAL_REGISTRY.values() if s.is_canonically_running]
