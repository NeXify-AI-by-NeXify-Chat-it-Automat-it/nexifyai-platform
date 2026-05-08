"""
NeXifyAI — Topology-Aware Multi-Perspective Health Probe (E1.2)
Probes services from MULTIPLE observer positions, not just localhost.

Usage:
    from backend.diagnostics.topology_probe import probe_all
    results = probe_all()
    # Returns: list of ProbeResult with observer, target, canonical, observed, layer, diagnosis, recovery
"""

import os
import time
import socket
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ObserverPosition(Enum):
    """Which network position is the observer in?"""
    HERMES_CONTAINER = "hermes-container"
    VPS_HOST = "vps-host"
    EXTERNAL = "external"


class TopologyLayer(Enum):
    """Which topology layer is responsible for the failure?"""
    SERVICE = "service"               # Service not running
    NETWORK = "docker-network"        # Network isolation
    PORT_BINDING = "port-binding"     # Port not mapped to host
    DNS = "dns"                       # DNS resolution
    FIREWALL = "firewall"             # Firewall blocking
    REVERSE_PROXY = "reverse-proxy"   # Proxy misconfiguration
    OK = "ok"                         # All good


@dataclass
class ProbeResult:
    observer: ObserverPosition
    target: str
    canonical_endpoint: str
    observed_endpoint: str
    reachable: bool
    latency_ms: float
    layer: TopologyLayer
    diagnosis: str
    recovery: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ══════════════════════════════════════════════
# SERVICE CATALOG (canonical endpoints per observer)
# ══════════════════════════════════════════════

SERVICE_CATALOG = {
    "backend": {
        "canonical": "systemctl is-active nexifyai-backend",
        "endpoints": {
            ObserverPosition.VPS_HOST: "http://localhost:8001/api/health/live",
            ObserverPosition.HERMES_CONTAINER: "http://172.17.0.1:8001/api/health/live",  # host.docker.internal
            ObserverPosition.EXTERNAL: "https://www.nexify-automate.com/api/health/live",
        },
        "recovery": "systemctl restart nexifyai-backend",
    },
    "qdrant": {
        "canonical": "docker ps --filter name=nexifyai-qdrant --format '{{.Status}}'",
        "endpoints": {
            ObserverPosition.VPS_HOST: "http://localhost:6333/collections",
            ObserverPosition.HERMES_CONTAINER: "http://qdrant-vjfp-qdrant-1:6333/collections",
            ObserverPosition.EXTERNAL: "http://72.62.152.47:32769/collections",
        },
        "recovery": "docker restart nexifyai-qdrant",
    },
    "redis": {
        "canonical": "docker exec honcho-redis-1 redis-cli PING",
        "endpoints": {
            ObserverPosition.VPS_HOST: "tcp://localhost:6379",           # Fails — no port mapping
            ObserverPosition.HERMES_CONTAINER: "tcp://honcho-redis-1:6379",  # Works — same network
            ObserverPosition.EXTERNAL: None,                             # Not exposed
        },
        "recovery": "docker restart honcho-redis-1",
    },
    "supabase": {
        "canonical": "docker exec supabase-db pg_isready -U postgres",
        "endpoints": {
            ObserverPosition.VPS_HOST: "http://localhost:6543",           # Pooler
            ObserverPosition.HERMES_CONTAINER: "tcp://supabase-db:5432", # Internal network
            ObserverPosition.EXTERNAL: "https://72.62.152.47:6543",
        },
        "recovery": "docker restart supabase-db",
    },
    "open_notebook": {
        "canonical": "docker ps --filter name=notebook-open_notebook-1 --format '{{.Status}}'",
        "endpoints": {
            ObserverPosition.VPS_HOST: "http://localhost:32770/api/sources",
            ObserverPosition.HERMES_CONTAINER: "http://localhost:32770/api/sources",
            ObserverPosition.EXTERNAL: "http://72.62.152.47:32770/api/sources",
        },
        "recovery": "docker restart notebook-open_notebook-1",
    },
    "paperclip": {
        "canonical": "docker ps --filter name=paperclip-etdf-paperclip-1 --format '{{.Status}}'",
        "endpoints": {
            ObserverPosition.VPS_HOST: "http://localhost:47967",
            ObserverPosition.HERMES_CONTAINER: "http://paperclip-etdf-paperclip-1:3100",
            ObserverPosition.EXTERNAL: "http://72.62.152.47:47967",
        },
        "recovery": "docker restart paperclip-etdf-paperclip-1",
    },
    "traefik": {
        "canonical": "curl -sf https://www.nexify-automate.com",
        "endpoints": {
            ObserverPosition.VPS_HOST: "https://www.nexify-automate.com",
            ObserverPosition.HERMES_CONTAINER: "https://www.nexify-automate.com",
            ObserverPosition.EXTERNAL: "https://www.nexify-automate.com",
        },
        "recovery": "docker restart traefik-tcja-traefik-1",
    },
}


# ══════════════════════════════════════════════
# PROBE ENGINE
# ══════════════════════════════════════════════

def probe_all(
    observers: List[ObserverPosition] = None,
    services: List[str] = None,
) -> List[ProbeResult]:
    """
    Probe all services from all observer positions.
    Returns list of ProbeResult with topology-aware diagnosis.
    """
    if observers is None:
        observers = [ObserverPosition.HERMES_CONTAINER]
    if services is None:
        services = list(SERVICE_CATALOG.keys())

    results = []

    for service_name in services:
        catalog = SERVICE_CATALOG.get(service_name)
        if not catalog:
            continue

        for observer in observers:
            endpoint = catalog["endpoints"].get(observer)
            if endpoint is None:
                results.append(ProbeResult(
                    observer=observer,
                    target=service_name,
                    canonical_endpoint=catalog["canonical"],
                    observed_endpoint="N/A (not exposed at this layer)",
                    reachable=False,
                    latency_ms=0,
                    layer=TopologyLayer.PORT_BINDING,
                    diagnosis=f"{service_name} not exposed for observer {observer.value}",
                    recovery=f"Add port mapping or use different observer position",
                ))
                continue

            result = _probe_endpoint(observer, service_name, endpoint, catalog)
            results.append(result)

    return results


def _probe_endpoint(
    observer: ObserverPosition,
    service_name: str,
    endpoint: str,
    catalog: dict,
) -> ProbeResult:
    """Probe a single endpoint and diagnose failures."""
    start = time.time()

    try:
        if endpoint.startswith("tcp://"):
            reachable, error, layer = _probe_tcp(endpoint.replace("tcp://", ""))
        elif endpoint.startswith("http"):
            reachable, error, layer = _probe_http(endpoint)
        elif endpoint.startswith("https"):
            reachable, error, layer = _probe_https(endpoint)
        else:
            reachable, error, layer = False, f"Unknown protocol: {endpoint[:20]}", TopologyLayer.SERVICE
    except Exception as e:
        reachable, error, layer = False, str(e), TopologyLayer.SERVICE

    latency = (time.time() - start) * 1000

    # Diagnose topology layer
    if not reachable and layer == TopologyLayer.OK:
        layer = _diagnose_layer(observer, service_name, endpoint, error)

    return ProbeResult(
        observer=observer,
        target=service_name,
        canonical_endpoint=catalog["canonical"],
        observed_endpoint=endpoint,
        reachable=reachable,
        latency_ms=round(latency, 1),
        layer=layer,
        diagnosis=_build_diagnosis(observer, service_name, endpoint, reachable, error, layer),
        recovery=catalog.get("recovery", "manual investigation required"),
        error=error,
    )


def _probe_tcp(host_port: str) -> tuple:
    """Probe TCP connectivity. Returns (reachable, error, layer)."""
    try:
        host, port_str = host_port.rsplit(":", 1)
        port = int(port_str)
    except ValueError:
        return False, f"Invalid host:port: {host_port}", TopologyLayer.SERVICE

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return True, None, TopologyLayer.OK
        elif result in (111, 61):  # Connection refused
            return False, f"TCP connection refused ({host}:{port})", TopologyLayer.NETWORK
        elif result in (110, 60):  # Timeout
            return False, f"TCP timeout ({host}:{port})", TopologyLayer.NETWORK
        else:
            return False, f"TCP error {result} ({host}:{port})", TopologyLayer.NETWORK
    except socket.gaierror:
        return False, f"DNS resolution failed for {host}", TopologyLayer.DNS
    except Exception as e:
        return False, str(e), TopologyLayer.NETWORK


def _probe_http(url: str) -> tuple:
    """Probe HTTP endpoint."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status < 500, None, TopologyLayer.OK
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}", TopologyLayer.SERVICE
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "refused" in reason.lower():
            return False, reason, TopologyLayer.NETWORK
        elif "timeout" in reason.lower():
            return False, reason, TopologyLayer.NETWORK
        elif "resolve" in reason.lower():
            return False, reason, TopologyLayer.DNS
        return False, reason, TopologyLayer.NETWORK
    except Exception as e:
        return False, str(e), TopologyLayer.NETWORK


def _probe_https(url: str) -> tuple:
    """Probe HTTPS endpoint."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        ctx = None
        try:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        except Exception:
            pass
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            return resp.status < 500, None, TopologyLayer.OK
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "refused" in reason.lower():
            return False, reason, TopologyLayer.NETWORK
        elif "timeout" in reason.lower():
            return False, reason, TopologyLayer.NETWORK
        return False, reason, TopologyLayer.REVERSE_PROXY
    except Exception as e:
        return False, str(e), TopologyLayer.REVERSE_PROXY


def _diagnose_layer(observer: ObserverPosition, service: str, endpoint: str, error: str) -> TopologyLayer:
    """Diagnose which topology layer caused the failure."""
    error_lower = (error or "").lower()

    if "refused" in error_lower:
        if observer == ObserverPosition.HERMES_CONTAINER and "localhost" in endpoint:
            return TopologyLayer.NETWORK  # Container can't reach host localhost
        return TopologyLayer.PORT_BINDING

    if "timeout" in error_lower:
        return TopologyLayer.NETWORK

    if "resolve" in error_lower or "dns" in error_lower or "getaddrinfo" in error_lower:
        return TopologyLayer.DNS

    if "certificate" in error_lower or "ssl" in error_lower:
        return TopologyLayer.REVERSE_PROXY

    return TopologyLayer.NETWORK


def _build_diagnosis(
    observer: ObserverPosition,
    service: str,
    endpoint: str,
    reachable: bool,
    error: Optional[str],
    layer: TopologyLayer,
) -> str:
    """Build human-readable diagnosis."""
    if reachable:
        return f"{service} reachable from {observer.value} via {endpoint}"

    diagnoses = {
        TopologyLayer.NETWORK: f"{service} NOT reachable from {observer.value}. Network isolation: {observer.value} cannot reach {endpoint}. Service IS running but unreachable from this observer position.",
        TopologyLayer.PORT_BINDING: f"{service} port not mapped for {observer.value}. Service IS running but port is bound to different interface.",
        TopologyLayer.DNS: f"{service} DNS resolution failed for {observer.value}. Check /etc/hosts or Docker DNS.",
        TopologyLayer.FIREWALL: f"{service} blocked by firewall for {observer.value}.",
        TopologyLayer.REVERSE_PROXY: f"{service} reverse proxy misconfigured. Backend may be up but proxy not routing.",
        TopologyLayer.SERVICE: f"{service} service appears DOWN. Check systemctl or docker ps.",
        TopologyLayer.OK: f"{service} OK.",
    }

    base = diagnoses.get(layer, f"{service}: {error}")
    if error:
        base += f" Error: {error}"
    return base


# ══════════════════════════════════════════════
# CONVENIENCE: Probe from all positions via SSH
# ══════════════════════════════════════════════

def probe_from_vps_ssh() -> List[ProbeResult]:
    """Run probes from VPS host perspective via SSH."""
    results = []

    for service_name, catalog in SERVICE_CATALOG.items():
        endpoint = catalog["endpoints"].get(ObserverPosition.VPS_HOST)
        if not endpoint:
            continue

        if endpoint.startswith("tcp://"):
            cmd = f"timeout 3 bash -c 'cat < /dev/null > /dev/tcp/{endpoint.replace('tcp://', '').replace(':', '/')}' 2>&1"
        else:
            cmd = f"curl -sf -o /dev/null -w '%{{http_code}}' --max-time 5 {endpoint} 2>&1"

        try:
            import subprocess
            r = subprocess.run(
                ["sshpass", "-p", os.getenv("VPS_PASSWORD", ""),
                 "ssh", "-o", "StrictHostKeyChecking=no", "root@72.62.152.47", cmd],
                capture_output=True, text=True, timeout=10
            )
            reachable = "200" in r.stdout or "OK" in r.stdout or r.returncode == 0
            results.append(ProbeResult(
                observer=ObserverPosition.VPS_HOST,
                target=service_name,
                canonical_endpoint=catalog["canonical"],
                observed_endpoint=endpoint,
                reachable=reachable,
                latency_ms=0,
                layer=TopologyLayer.OK if reachable else TopologyLayer.NETWORK,
                diagnosis=f"{service_name} {'reachable' if reachable else 'UNREACHABLE'} from VPS host",
                recovery=catalog.get("recovery", ""),
            ))
        except Exception as e:
            results.append(ProbeResult(
                observer=ObserverPosition.VPS_HOST,
                target=service_name,
                canonical_endpoint=catalog["canonical"],
                observed_endpoint=endpoint,
                reachable=False,
                latency_ms=0,
                layer=TopologyLayer.NETWORK,
                diagnosis=f"SSH probe failed: {e}",
                recovery="Check SSH connectivity",
            ))

    return results
