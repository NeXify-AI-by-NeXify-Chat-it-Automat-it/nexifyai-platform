"""
NeXifyAI — Health API v2 Routes
Kubernetes-style health endpoints backed by EnterpriseHealth.

Endpoints:
  GET /api/health/live    — Process alive (always 200 if running)
  GET /api/health/ready   — Dependencies reachable (sqlite, qdrant, redis)
  GET /api/health/v2      — Full 10-component EnterpriseHealth JSON
  GET /api/health/metrics  — Prometheus metrics endpoint (future)

Architecture: NO new logic. All data from EnterpriseHealth.refresh_from_system().
Thread-safety: TTL cache (5s) prevents parallel refresh storms and request blocking.
"""

import os
import time
import threading
import sqlite3
from fastapi import APIRouter, Response
from backend.health.enterprise_health import EnterpriseHealth, HealthStatus

router = APIRouter(prefix="/api/health", tags=["health"])

# Cache with TTL to prevent parallel refresh storms
#
# ESCALATION PATH (single-worker → multi-worker):
#   Current:  threading.Lock() — works for 1 Uvicorn worker (shared memory)
#   Step 1:   asyncio.Lock() — needed for async handlers (avoids blocking event loop)
#   Step 2:   Redis cache — cross-process, cross-container (SETEX health:v2 5 ...)
#   Step 3:   Background refresh task — fully decoupled, writes to Redis every N seconds
#
# When moving to multi-worker (gunicorn -w 4), replace this with Redis or a
# dedicated background thread that refreshes on a timer, not on request.
_CACHE_TTL = 5  # seconds
_cache: dict = {
    "data": None,
    "timestamp": 0,
    "lock": threading.Lock(),
}


def _get_health():
    """Thread-safe cached health refresh. Max 1 refresh per _CACHE_TTL seconds."""
    now = time.time()
    
    # Fast path: cache valid
    if _cache["data"] is not None and (now - _cache["timestamp"]) < _CACHE_TTL:
        return _cache["data"]
    
    # Slow path: refresh under lock
    with _cache["lock"]:
        # Double-check: another thread might have refreshed while we waited
        if _cache["data"] is not None and (now - _cache["timestamp"]) < _CACHE_TTL:
            return _cache["data"]
        
        health = EnterpriseHealth()
        health.refresh_from_system()
        _cache["data"] = health
        _cache["timestamp"] = time.time()
        return health


# ══════════════════════════════════════════════
# GET /api/health/live — Liveness Probe
# ══════════════════════════════════════════════

@router.get("/live")
async def health_live():
    """
    Kubernetes liveness probe.
    Returns 200 if the process is running. No dependency checks.
    """
    return {
        "status": "alive",
        "timestamp": int(time.time()),
    }


# ══════════════════════════════════════════════
# GET /api/health/ready — Readiness Probe
# ══════════════════════════════════════════════

@router.get("/ready")
async def health_ready():
    """
    Kubernetes readiness probe.
    Checks if critical dependencies are reachable.
    Returns 200 if ready, 503 if not.
    """
    dependencies = _check_dependencies()
    all_ready = all(v == "up" for v in dependencies.values())

    status_code = 200 if all_ready else 503
    return Response(
        content=_json({
            "status": "ready" if all_ready else "not_ready",
            "timestamp": int(time.time()),
            "dependencies": dependencies,
        }),
        status_code=status_code,
        media_type="application/json",
    )


# ══════════════════════════════════════════════
# GET /api/health/v2 — Full Enterprise Health
# ══════════════════════════════════════════════

@router.get("/v2")
async def health_v2():
    """
    Full 10-component Enterprise Health diagnostic.
    Backed by EnterpriseHealth.refresh_from_system() with 5s TTL cache.
    """
    health = _get_health()
    score = health.compute_score()
    status = health.get_status(score)

    components = {}
    for name, comp in health.components.items():
        components[name] = {
            "score": round(comp.score, 1),
            "status": comp.status.value,
            "weight": round(comp.weight, 2),
            "metrics": comp.metrics,
        }

    dependencies = _check_dependencies()

    # Collect meta from real sources
    meta = _collect_meta()

    body = {
        "status": status.value,
        "score": round(score, 1),
        "timestamp": int(time.time()),
        "components": components,
        "dependencies": dependencies,
        "meta": meta,
    }

    return body


# ══════════════════════════════════════════════
# GET /api/health/metrics — Prometheus (future)
# ══════════════════════════════════════════════

@router.get("/metrics")
async def health_metrics():
    """
    Prometheus metrics endpoint placeholder.
    Will expose nexifyai_health_score, nexifyai_* gauges.
    """
    try:
        from backend.monitoring.metrics import get_metrics, get_metrics_content_type
        return Response(
            content=get_metrics(),
            media_type=get_metrics_content_type(),
        )
    except ImportError:
        return Response(
            content="# Prometheus metrics not configured\n",
            media_type="text/plain",
            status_code=503,
        )


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════

def _check_dependencies() -> dict:
    """Check critical dependency reachability."""
    deps = {}

    # SQLite brain.db
    brain_db = "/opt/data/brain/brain.db"
    if os.path.exists(brain_db):
        try:
            conn = sqlite3.connect(brain_db)
            conn.execute("SELECT 1")
            conn.close()
            deps["sqlite"] = "up"
        except Exception:
            deps["sqlite"] = "down"
    else:
        deps["sqlite"] = "down"

    # Qdrant (port 6333)
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:6333/collections")
        with urllib.request.urlopen(req, timeout=2):
            deps["qdrant"] = "up"
    except Exception:
        deps["qdrant"] = "down"

    # Redis (port 6379)
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("localhost", 6379))
        s.close()
        deps["redis"] = "up" if result == 0 else "down"
    except Exception:
        deps["redis"] = "down"

    # Supabase (check if psql or Docker available)
    try:
        import subprocess
        r = subprocess.run(
            ["docker", "exec", "supabase-db", "pg_isready", "-U", "postgres"],
            capture_output=True, timeout=5
        )
        deps["supabase"] = "up" if r.returncode == 0 else "down"
    except Exception:
        deps["supabase"] = "down"

    # OpenRouter API
    try:
        import urllib.request
        req = urllib.request.Request("https://openrouter.ai/api/v1/models")
        with urllib.request.urlopen(req, timeout=3):
            deps["openrouter"] = "up"
    except Exception:
        deps["openrouter"] = "down"

    return deps


def _collect_meta() -> dict:
    """Collect metadata from real system sources."""
    meta = {}

    # brain.db stats
    brain_db = "/opt/data/brain/brain.db"
    if os.path.exists(brain_db):
        try:
            conn = sqlite3.connect(brain_db)
            meta["brain_memories"] = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            meta["brain_skills"] = conn.execute("SELECT COUNT(*) FROM skills_cache").fetchone()[0]
            meta["brain_sessions"] = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            conn.close()
        except Exception:
            pass

    # TODO count
    try:
        import subprocess
        r = subprocess.run(
            ["grep", "-r", "TODO", "--include=*.py", "--include=*.ts",
             "/opt/nexifyai-platform"],
            capture_output=True, text=True, timeout=10
        )
        meta["todo_count"] = len([l for l in r.stdout.split("\n") if l.strip()])
    except Exception:
        meta["todo_count"] = -1

    # Test file count
    try:
        test_dir = "/opt/nexifyai-platform/services/api/tests"
        count = 0
        if os.path.exists(test_dir):
            for _, _, files in os.walk(test_dir):
                count += sum(1 for f in files if f.startswith("test_"))
        meta["test_files"] = count
    except Exception:
        meta["test_files"] = -1

    # ADR count
    try:
        adr_dir = "/opt/nexifyai-platform/docs/adrs"
        if os.path.exists(adr_dir):
            meta["adr_count"] = len([f for f in os.listdir(adr_dir) if f.startswith("ADR-")])
    except Exception:
        meta["adr_count"] = -1

    return meta


def _json(obj: dict) -> str:
    import json
    return json.dumps(obj, default=str)
