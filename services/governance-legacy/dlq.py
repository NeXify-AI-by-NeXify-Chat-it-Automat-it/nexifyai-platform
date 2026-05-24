"""Dead Letter Queue — persistent storage for failed activities and workflows.

Stores failures in Redis with structured metadata for replay, analysis, and alerting.
Each entry has: id, timestamp, source, workflow_id, task_id, error, context, retry_count.
"""

import json, uuid, logging, time
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.dlq")

# Redis connection — fall back gracefully if unavailable
REDIS_HOST = "localhost"
REDIS_PORT = 6379
DLQ_KEY = "nexifyai:dlq"
DLQ_MAX_AGE = 86400 * 7  # 7 days retention

_redis = None


def _get_redis():
    """Lazy-init Redis connection."""
    global _redis
    if _redis is None:
        try:
            import redis as _redis_mod
            _redis = _redis_mod.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=3)
            _redis.ping()
        except Exception as e:
            logger.warning(f"DLQ Redis unavailable: {e}")
            _redis = None
    return _redis


async def push_to_dlq(
    workflow_id: str,
    task_id: str = "",
    source: str = "activity",
    error: str = "",
    context: dict = None,
    severity: str = "error",
) -> str:
    """Push a failed item to the dead letter queue."""
    entry_id = str(uuid.uuid4())[:12]
    entry = {
        "id": entry_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "workflow_id": workflow_id,
        "task_id": task_id,
        "error": str(error)[:500],
        "context": context or {},
        "severity": severity,
        "retry_count": 0,
        "replayed": False,
        "resolved": False,
    }
    
    r = _get_redis()
    if r:
        try:
            r.xadd(DLQ_KEY, entry, maxlen=1000)
            r.expire(DLQ_KEY, DLQ_MAX_AGE)
            logger.info(f"DLQ: pushed {entry_id} ({source}/{task_id})")
        except Exception as e:
            logger.error(f"DLQ write failed: {e}")
    else:
        # Fallback: log it so it's not lost silently
        logger.error(f"DLQ (no-redis): {entry_id} {source} {error[:100]}")
    
    return entry_id


def get_dlq_entries(count: int = 50, unresolved_only: bool = True) -> list:
    """Retrieve recent DLQ entries."""
    r = _get_redis()
    if not r:
        return []
    
    try:
        entries = r.xrevrange(DLQ_KEY, max="+", min="-", count=count)
        results = []
        for entry_id, data in entries:
            data["_id"] = entry_id
            data["resolved"] = data.get("resolved", "False") == "True" or data.get("resolved") == True
            # Handle bool vs string
            if isinstance(data.get("resolved"), str):
                data["resolved"] = data["resolved"].lower() == "true"
            if unresolved_only and data.get("resolved", False):
                continue
            results.append(data)
        return results
    except Exception as e:
        logger.warning(f"DLQ read failed: {e}")
        return []


def mark_resolved(entry_id: str) -> bool:
    """Mark a DLQ entry as resolved (replayed or fixed)."""
    r = _get_redis()
    if not r:
        return False
    try:
        # Get the entry
        entries = r.xrevrange(DLQ_KEY, max="+", min="-", count=100)
        target = None
        for eid, data in entries:
            if data.get("id") == entry_id or eid == entry_id:
                target = data
                break
        if target:
            target["resolved"] = "True"
            target["resolved_at"] = datetime.now(timezone.utc).isoformat()
            r.xadd(f"{DLQ_KEY}:resolved", target, maxlen=1000)
            return True
        return False
    except Exception as e:
        logger.warning(f"DLQ resolve failed: {e}")
        return False


def get_dlq_stats() -> dict:
    """Get DLQ statistics."""
    r = _get_redis()
    if not r:
        return {"total": 0, "unresolved": 0, "by_source": {}}
    
    try:
        total = r.xlen(DLQ_KEY)
        entries = r.xrevrange(DLQ_KEY, max="+", min="-", count=100)
        unresolved = 0
        by_source = {}
        for _, data in entries:
            resolved = data.get("resolved", "False")
            if isinstance(resolved, str):
                resolved = resolved.lower() == "true"
            if not resolved:
                unresolved += 1
            src = data.get("source", "unknown")
            by_source[src] = by_source.get(src, 0) + 1
        return {
            "total": total,
            "unresolved": unresolved,
            "by_source": by_source,
        }
    except Exception as e:
        return {"total": 0, "unresolved": 0, "by_source": {}, "error": str(e)}
