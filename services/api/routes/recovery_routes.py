"""Recovery Routes — DLQ, Circuit Breaker, Worker Rebalancing API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter(prefix="/api/recovery", tags=["recovery"])


# === DLQ Endpoints ===

@router.get("/dlq")
async def get_dlq(count: int = 50, unresolved_only: bool = True):
    """List dead letter queue entries."""
    from dlq import get_dlq_entries
    entries = get_dlq_entries(count=count, unresolved_only=unresolved_only)
    return {"entries": entries, "count": len(entries)}


@router.get("/dlq/stats")
async def dlq_stats():
    """Get DLQ statistics."""
    from dlq import get_dlq_stats
    return get_dlq_stats()


class DLQResolveRequest(BaseModel):
    entry_id: str


@router.post("/dlq/resolve")
async def resolve_dlq(req: DLQResolveRequest):
    """Mark a DLQ entry as resolved."""
    from dlq import mark_resolved
    ok = mark_resolved(req.entry_id)
    if not ok:
        raise HTTPException(404, "Entry not found")
    return {"status": "resolved", "entry_id": req.entry_id}


@router.post("/dlq/push")
async def push_to_dlq_endpoint(
    workflow_id: str,
    source: str = "manual",
    error: str = "",
    task_id: str = "",
    severity: str = "warning",
):
    """Manually push an entry to the DLQ (for testing)."""
    from dlq import push_to_dlq
    entry_id = await push_to_dlq(
        workflow_id=workflow_id,
        task_id=task_id,
        source=source,
        error=error,
        severity=severity,
    )
    return {"entry_id": entry_id}


# === Circuit Breaker Endpoints ===

@router.get("/circuit-breakers")
async def get_circuit_breakers():
    """Get status of all circuit breakers."""
    from circuit_breaker import all_breaker_statuses
    return {"breakers": all_breaker_statuses()}


class CBResetRequest(BaseModel):
    name: str


@router.post("/circuit-breakers/reset")
async def reset_circuit_breaker(req: CBResetRequest):
    """Manually reset a circuit breaker."""
    from circuit_breaker import get_breaker
    cb = get_breaker(req.name)
    cb.reset()
    return {"status": "reset", "name": req.name, "state": cb.state}


# === Worker Rebalancing Endpoints ===

@router.get("/workers")
async def list_workers():
    """List known Temporal workers and their health."""
    from metrics import WORKER_HEALTH
    # Read worker health from metrics (set by workers on activity execution)
    # Also check systemd
    import subprocess
    r = subprocess.run(
        "systemctl list-units --type=service --state=running | grep temporal || true",
        shell=True, capture_output=True, text=True, timeout=10
    )
    systemd_workers = [l.strip() for l in r.stdout.split('\n') if l.strip()]
    
    # Fetch from Temporal Web UI API
    import httpx
    try:
        wr = httpx.get("http://localhost:8234/api/v1/namespaces/default/workflows", timeout=5)
        workflows_info = wr.json() if wr.status_code == 200 else {"error": wr.status_code}
    except Exception as e:
        workflows_info = {"fetch_error": "fetch failed"}
    
    return {
        "systemd": systemd_workers,
        "workflow_count": len(workflows_info.get("executions", [])) if isinstance(workflows_info, dict) else 0,
    }


@router.post("/workers/rebalance")
async def rebalance_workers():
    """Force restart temporal workers to rebalance loads."""
    import subprocess
    results = {}
    for svc in ["nexifyai-temporal-main", "nexifyai-temporal-analysis", "nexifyai-temporal-engineering"]:
        r = subprocess.run(f"systemctl restart {svc}", shell=True, capture_output=True, text=True, timeout=30)
        results[svc] = "restarted" if r.returncode == 0 else f"failed: {r.stderr[:100]}"
    return {"results": results}


@router.get("/health")
async def recovery_health():
    """Overall recovery infrastructure health check."""
    from dlq import get_dlq_stats
    from circuit_breaker import all_breaker_statuses
    
    dlq = get_dlq_stats()
    breakers = all_breaker_statuses()
    open_breakers = [n for n, s in breakers.items() if s["state"] == "open"]
    
    return {
        "status": "healthy" if not open_breakers else "degraded",
        "dlq": {"total": dlq.get("total", 0), "unresolved": dlq.get("unresolved", 0)},
        "circuit_breakers": {
            "total": len(breakers),
            "open": len(open_breakers),
            "open_breakers": open_breakers,
        },
    }
