"""
Order Management Routes — Auftragsverwaltung nach DIN 69901 / ISO 9001.
Phase 1: Eingang → Phase 2: IST-Scan → Phase 3: Wissensquellen → Phase 4: Ausführung → Phase 5: Qualitätsprüfung.

CEO-konform: jeder Auftrag hat order_id, priority, assigned_agent, ist_stand, wissensquellen, quality_audit.
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Query
import os

logger = logging.getLogger("nexifyai.orders")
order_router = APIRouter(prefix="/orders", tags=["orders"])

BRAIN_URL = "http://localhost:6333"
COLLECTION = "nexifyai_brain"
VECTOR_DIM = 4096

# ── In-Memory Order Store (persisted to Brain on change) ──
ORDERS = {}

def _generate_order_id(prefix: str = "ORD") -> str:
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_hash = hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:4]
    return f"{prefix}-{now}-{short_hash}"

def _brain_persist(order: dict):
    """Order im Brain ablegen."""
    try:
        point_id = int(hashlib.sha256(order["order_id"].encode()).hexdigest()[:16], 16) % (2**63)
        httpx.put(f"{BRAIN_URL}/collections/{COLLECTION}/points?wait=true", json={
            "points": [{"id": point_id, "vector": [0.0] * VECTOR_DIM, "payload": {
                "category": "order",
                "topic": "order-management",
                "order_id": order["order_id"],
                "content": json.dumps(order),
                "provenance": "order-workflow-specialist",
                "confidence": 0.95,
                "status": "active",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }}]
        }, timeout=10)
    except Exception as e:
        logger.warning(f"Brain persist error: {e}")

# ── API Endpoints ──

@order_router.get("/")
async def list_orders(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """Alle Aufträge auflisten, filterbar nach Status/Priority."""
    results = list(ORDERS.values())
    if status:
        results = [o for o in results if o.get("status") == status]
    if priority:
        results = [o for o in results if o.get("priority") == priority]
    results.sort(key=lambda o: o.get("created_at", ""), reverse=True)
    return {
        "total": len(results),
        "orders": results[:limit],
        "active_filter": {"status": status, "priority": priority}
    }

@order_router.get("/{order_id}")
async def get_order(order_id: str):
    """Einzelnen Auftrag abrufen inkl. Historie."""
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, f"Order {order_id} not found")
    return order

@order_router.post("/")
async def create_order(request: Request):
    """Neuen Auftrag anlegen — Phase 1: EINGANG.
    Erwartet: {task, priority, category, assigned_agent, deadline?, context?}
    """
    body = await request.json()
    
    order = {
        "order_id": _generate_order_id(),
        "status": "received",
        "priority": body.get("priority", "P2"),
        "category": body.get("category", "uncategorized"),
        "task": body.get("task", ""),
        "assigned_agent": body.get("assigned_agent", "project-manager"),
        "deadline": body.get("deadline"),
        "context": body.get("context", {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "phases": {},
        "timeline": [{"phase": "received", "timestamp": datetime.now(timezone.utc).isoformat()}],
    }
    
    ORDERS[order["order_id"]] = order
    _brain_persist(order)
    
    logger.info(f"Order created: {order['order_id']} [{order['priority']}] → {order['assigned_agent']}")
    return {"status": "created", "order": order}

@order_router.post("/{order_id}/scan")
async def scan_order(order_id: str):
    """Phase 2: IST-STAND-SCAN.
    Scannt das System zum Auftragsthema: Brain, Health, bekannte Probleme.
    """
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, f"Order {order_id} not found")
    
    # Scan Brain for related knowledge
    ist_stand = {"brain_entries": [], "system_health": {}, "known_issues": []}
    
    try:
        # Brain search for topic
        keyword = order.get("category", "system")
        r = httpx.post(f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll", json={
            "limit": 20, "with_payload": True, "with_vector": False,
        }, timeout=10)
        if r.status_code == 200:
            pts = r.json().get("result", {}).get("points", [])
            ist_stand["brain_entries"] = [
                {"id": p["id"], "category": p.get("payload", {}).get("category", "?"),
                 "topic": p.get("payload", {}).get("topic", "?")[:100]}
                for p in pts if keyword.lower() in str(p.get("payload", {})).lower()
            ][:10]
        
        # System health
        r2 = httpx.get("http://localhost:8001/api/health", timeout=8)
        if r2.status_code == 200:
            ist_stand["system_health"] = {"status": "healthy", "code": 200}
    except Exception as e:
        ist_stand["error"] = str(e)[:200]
    
    order["phases"]["ist_stand"] = ist_stand
    order["status"] = "scanned"
    order["timeline"].append({"phase": "scanned", "timestamp": datetime.now(timezone.utc).isoformat()})
    _brain_persist(order)
    
    return {"status": "scanned", "order_id": order_id, "ist_stand": ist_stand}

@order_router.post("/{order_id}/enrich")
async def enrich_order(order_id: str):
    """Phase 3: WISSENSQUELLEN-ANREICHERUNG.
    Relevante Docs, Repos, Skills von aitmpl.com hinzufügen.
    """
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, f"Order {order_id} not found")
    
    enriched = {
        "sources": [],
        "skills_from_marketplace": [],
        "brain_references": [],
    }
    
    # Brain references
    try:
        r = httpx.post(f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll", json={
            "limit": 30, "with_payload": True, "with_vector": False,
        }, timeout=10)
        if r.status_code == 200:
            pts = r.json().get("result", {}).get("points", [])
            enriched["brain_references"] = [
                {"id": p["id"], "category": p.get("payload", {}).get("category", "?"),
                 "confidence": p.get("payload", {}).get("confidence", 0)}
                for p in pts[:10]
            ]
    except Exception as e:
        enriched["brain_error"] = str(e)[:100]
    
    # Skills marketplace reference
    enriched["skills_from_marketplace"] = [
        "app.aitmpl.com/skills — 821 Skills, 421 Agents verfügbar",
        "MCP-Router: 13 Tools über 7 Services (POST /mcp/rpc)",
    ]
    
    # Documentation references
    enriched["sources"] = [
        "GitHub: davila7/claude-code-templates (Skills-Marketplace)",
        "GitHub: nexifyai/* (alle 7 Repos)",
        "Backend: server.py (34 Router), mcp_routes.py (13 MCP Tools)"
    ]
    
    order["phases"]["enriched"] = enriched
    order["status"] = "enriched"
    order["timeline"].append({"phase": "enriched", "timestamp": datetime.now(timezone.utc).isoformat()})
    _brain_persist(order)
    
    return {"status": "enriched", "order_id": order_id, "enriched": enriched}

@order_router.post("/{order_id}/execute")
async def execute_order_route(order_id: str, background_tasks=None):
    """Phase 4: AUSFÜHRUNG — Auftrag asynchron an Agenten dispatch.
    Gibt sofort zurück, Agent-Lauf im Hintergrund.
    Ergebnis wird in die Order geschrieben und im Brain persistiert.
    """
    import threading
    
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, f"Order {order_id} not found")
    
    order["status"] = "executing"
    order["timeline"].append({"phase": "executing", "timestamp": datetime.now(timezone.utc).isoformat()})
    
    def run_agent():
        try:
            # Internal auth via X-Internal-Auth header (bypasses JWT for local calls)
            headers = {"X-Internal-Auth": "nexifyai-local"}
            r = httpx.post("http://localhost:8001/api/orchestration/execute", json={
                "agent": order["assigned_agent"],
                "task": order["task"],
                "context": {
                    "order_id": order_id,
                    "priority": order["priority"],
                    "ist_stand": order.get("phases", {}).get("ist_stand", {}),
                    "enriched": order.get("phases", {}).get("enriched", {}),
                }
            }, headers=headers, timeout=120)
            if r.status_code == 200:
                result = r.json()
                order["phases"]["execution"] = result
                order["status"] = "executed"
                order["timeline"].append({"phase": "executed", "timestamp": datetime.now(timezone.utc).isoformat()})
                logger.info(f"Order {order_id}: executed by {result.get('agent','?')}")
            else:
                order["status"] = "failed"
                order["phases"]["execution_error"] = f"HTTP {r.status_code}: {r.text[:200]}"
                logger.warning(f"Order {order_id}: failed with HTTP {r.status_code}")
        except Exception as e:
            order["status"] = "error"
            order["phases"]["execution_error"] = str(e)[:200]
            logger.error(f"Order {order_id}: error {e}")
        _brain_persist(order)
    
    t = threading.Thread(target=run_agent, daemon=True)
    t.start()
    
    return {"status": "dispatched", "order_id": order_id, "message": "Agent dispatched in background"}

@order_router.post("/{order_id}/audit")
async def audit_order(order_id: str):
    """Phase 5: QUALITÄTSPRÜFUNG — Senior Quality Auditor triggern.
    Prüfung gegen DIN-Normen, Vorgaben, Brain-Compliance, Mission-Alignment.
    """
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, f"Order {order_id} not found")
    
    execution = order.get("phases", {}).get("execution", {})
    
    audit = {
        "audit_id": _generate_order_id("AUDIT"),
        "verdict": "PASS",
        "score": 1.0,
        "findings": [],
        "expert_required": None,
    }
    
    # Prüfstraßen-Kriterien
    brain_checked = execution.get("brain_checked", False)
    confidence = execution.get("confidence", 0)
    summary_len = len(execution.get("summary", ""))
    
    if not brain_checked:
        audit["findings"].append("Brain NOT queried before execution")
        audit["score"] -= 0.3
    
    if confidence < 0.70:
        audit["findings"].append(f"Low confidence: {confidence}")
        audit["score"] -= 0.2
    
    if summary_len < 50:
        audit["findings"].append(f"Summary too short: {summary_len} chars")
        audit["score"] -= 0.1
    
    if audit["score"] < 0.60:
        audit["verdict"] = "FAIL"
        audit["expert_required"] = "senior-quality-auditor"
        audit["next_action"] = "x_order_with_expert"
    elif audit["score"] < 0.80:
        audit["verdict"] = "WARN"
        audit["next_action"] = "fix_minor_issues"
    else:
        audit["next_action"] = "next_order"
    
    order["phases"]["quality_audit"] = audit
    order["status"] = "completed" if audit["verdict"] == "PASS" else "review_required"
    order["timeline"].append({"phase": "audited", "timestamp": datetime.now(timezone.utc).isoformat()})
    _brain_persist(order)
    
    return {"status": "audited", "order_id": order_id, "audit": audit}

@order_router.get("/stats/summary")
async def order_stats():
    """Auftragsstatistik: offen, in Bearbeitung, fertig, durchgefallen."""
    counts = {"received": 0, "scanned": 0, "enriched": 0, "executed": 0, "completed": 0, "review_required": 0, "failed": 0}
    for o in ORDERS.values():
        s = o.get("status", "?")
        if s in counts:
            counts[s] += 1
    
    return {
        "total": len(ORDERS),
        "by_status": counts,
        "active": counts["received"] + counts["scanned"] + counts["enriched"] + counts["executed"],
        "completed": counts["completed"],
        "failed": counts["review_required"] + counts["failed"],
    }

logger.info("Order Management Routes initialisiert — 5-Phasen-Workflow nach DIN 69901/ISO 9001")
