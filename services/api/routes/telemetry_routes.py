"""NeXifyAI — Telemetry Event Receiver

Receives system-internal telemetry events from @nexifyai/telemetry client.
Events: deploy, cron, health, security, incident, task.
Stores in MongoDB telemetry_events collection for dashboard consumption.
"""

import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from routes.shared import S

logger = logging.getLogger(__name__)
router = APIRouter(tags=["telemetry"])

VALID_EVENTS = {
    "deploy_started", "deploy_completed", "deploy_failed",
    "cron_executed", "cron_failed",
    "health_score_changed",
    "security_scan_completed", "vulnerability_found",
    "incident_created", "incident_resolved",
    "task_created", "task_started", "task_completed", "task_failed",
}


@router.post("/api/telemetry/event")
async def receive_telemetry_event(request: Request):
    """Receive and store a telemetry event from the frontend/CI/automation."""
    try:
        body = await request.json()
    except Exception:
        return {"ok": False, "error": "Invalid JSON"}

    event_type = body.get("event")
    if event_type not in VALID_EVENTS:
        return {"ok": False, "error": f"Unknown event: {event_type}"}

    doc = {
        **body,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "source_ip": request.client.host if request.client else "unknown",
    }

    try:
        await S.db["telemetry_events"].insert_one(doc)
        logger.info("Telemetry event stored: %s", event_type)
    except Exception as e:
        logger.warning("Telemetry store failed, logging only: %s: %s", type(e).__name__, e)
        # Still return ok — telemetry is fire-and-forget, non-critical

    return {"ok": True}


@router.get("/api/telemetry/events")
async def list_telemetry_events(limit: int = 50, event: str = None):
    """List recent telemetry events (admin use)."""
    try:
        query = {}
        if event:
            query["event"] = event
        cursor = S.db["telemetry_events"].find(query).sort("received_at", -1).limit(limit)
        events = []
        async for doc in cursor:
            doc.pop("_id", None)
            events.append(doc)
        return {"ok": True, "events": events, "count": len(events)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
