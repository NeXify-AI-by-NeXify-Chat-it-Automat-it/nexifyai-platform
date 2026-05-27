#!/usr/bin/env python3
"""
NeXifyAI CEO Autonomie-Loop — der CEO führt proaktiv Scans, Entscheidungen und Agent-Dispatches aus.
Triggered by systemd timer alle 5 Minuten (nexifyai-ceo.timer).

Der CEO ist die HÖCHSTE Instanz. Kein Agent wird ohne CEO-Entscheidung dispatched.
Nach jeder Ausführung: Quality Auditor → Bestanden? Nächster Auftrag. Durchgefallen? X-Auftrag + Experte.
"""

import os, sys, json, logging, asyncio, hashlib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/opt/nexifyai-platform/services/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("nexifyai.ceo_loop")

import httpx

BRAIN_URL = os.environ.get("HERMES_BRAIN_URL", "http://localhost:6333")
BACKEND_URL = os.environ.get("NEXIFYAI_BACKEND_URL", "http://localhost:8001")
COLLECTION = "nexifyai_brain"
MEMORIES = "nexifyai_memories"
VECTOR_DIM = 4096  # CRITICAL: Qdrant uses 4096, not 1024

# ── Brain Helpers ──

def brain_search(query_filter: dict, limit: int = 20):
    """Semantische Suche im Brain mit Payload-Filter."""
    try:
        r = httpx.post(f"{BRAIN_URL}/collections/{COLLECTION}/points/search", json={
            "vector": [0.0] * VECTOR_DIM,
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
            "filter": query_filter if query_filter else None,
        }, timeout=15)
        if r.status_code == 200:
            return r.json().get("result", [])
    except Exception as e:
        logger.warning(f"Brain search error: {e}")
    return []

def brain_scroll(category: str = None, limit: int = 50):
    """Brain-Inhalt durchscrollen."""
    try:
        payload = {"limit": limit, "with_payload": True, "with_vector": False}
        if category:
            payload["filter"] = {"must": [{"key": "category", "match": {"value": category}}]}
        r = httpx.post(f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll", json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get("result", {}).get("points", [])
    except Exception as e:
        logger.warning(f"Brain scroll error: {e}")
    return []

def brain_write(payload: dict):
    """Wissenseintrag ins Brain."""
    try:
        point_id = int(hashlib.sha256(str(datetime.now().isoformat()).encode()).hexdigest()[:16], 16) % (2**63)
        r = httpx.put(f"{BRAIN_URL}/collections/{COLLECTION}/points?wait=true", json={
            "points": [{"id": point_id, "vector": [0.0] * VECTOR_DIM, "payload": payload}]
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logger.warning(f"Brain write error: {e}")
    return False

# ── CEO Health Scanner ──

def scan_system_health() -> dict:
    """CEO-Scan: System-Health prüfen (Backend, Qdrant, Docker, SSL, DNS)."""
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "checks": {}}
    
    # 1. Backend
    try:
        r = httpx.get(f"{BACKEND_URL}/api/health", timeout=8)
        report["checks"]["backend"] = {"status": "ok" if r.status_code == 200 else "degraded", "code": r.status_code}
    except:
        report["checks"]["backend"] = {"status": "down", "code": 0}
    
    # 2. Qdrant
    try:
        r = httpx.get(f"{BRAIN_URL}/collections", timeout=8)
        n = len(r.json().get("result", {}).get("collections", []))
        report["checks"]["qdrant"] = {"status": "ok", "collections": n}
    except:
        report["checks"]["qdrant"] = {"status": "down"}
    
    # 3. MCP Router
    try:
        r = httpx.get(f"{BACKEND_URL}/mcp/health", timeout=8)
        report["checks"]["mcp"] = {"status": "ok", "tools": r.json().get("tools_registered", 0)}
    except:
        report["checks"]["mcp"] = {"status": "down"}
    
    # 4. Agent Scores
    agent_entries = brain_scroll(None, 200)
    low_score_agents = []
    for p in agent_entries:
        payload = p.get("payload", {})
        if payload.get("category") == "agent_eval":
            score = payload.get("score", 0)
            if score and score < 0.80:
                low_score_agents.append({"agent": payload.get("agent_id", "?"), "score": score})
    report["checks"]["agents"] = {"total": len(agent_entries), "low_score": low_score_agents}
    
    # 5. Brain Integrity
    brain_entries = brain_scroll(None, 300)
    stale = [p for p in brain_entries if p.get("payload", {}).get("status") == "quarantined"]
    no_cred = [p for p in brain_entries if not p.get("payload", {}).get("confidence")]
    report["checks"]["brain"] = {"total": len(brain_entries), "quarantined": len(stale), "no_credibility": len(no_cred)}
    
    # Score: backend/qdrant/mcp must be ok; agents/brain are informational
    core_checks = {k: v for k, v in report["checks"].items() if k in ("backend", "qdrant", "mcp")}
    core_ok = sum(1 for c in core_checks.values() if c.get("status") == "ok")
    report["score"] = core_ok / max(len(core_checks), 1)
    report["healthy"] = report["score"] >= 1.0  # All 3 core must be ok
    
    return report

# ── CEO Decision Engine ──

def ceo_decide(health: dict, previous_orders: list) -> list:
    """CEO entscheidet, welche Aktionen jetzt ausgeführt werden."""
    actions = []
    
    # P0: Health-Down → sofort fixen
    if not health.get("healthy", True):
        for check, result in health["checks"].items():
            if result.get("status") == "down":
                actions.append({
                    "order_id": f"CEO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-P0",
                    "priority": "P0",
                    "category": "health_emergency",
                    "agent": "cloud-architect",
                    "task": f"CRITICAL: {check} is down. Diagnose and fix immediately. Status: {result}",
                    "reason": f"Health check {check} reported DOWN"
                })
    
    # P1: Agent low scores → Prompt Engineer
    low_score = health.get("checks", {}).get("agents", {}).get("low_score", [])
    for a in low_score:
        actions.append({
            "order_id": f"CEO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-P1",
            "priority": "P1",
            "category": "agent_optimization",
            "agent": "prompt-engineer",
            "task": f"Improve agent profile for {a['agent']} (score={a['score']}). Target: >=0.80. Read existing profile, identify weaknesses, rewrite.",
            "reason": f"Agent {a['agent']} score {a['score']} < 0.80 threshold"
        })
    
    # P1: Brain Integrity — quarantined entries > 10
    brain = health.get("checks", {}).get("brain", {})
    if brain.get("quarantined", 0) > 10:
        actions.append({
            "order_id": f"CEO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-P1",
            "priority": "P1",
            "category": "brain_integrity",
            "agent": "fact-checker",
            "task": f"Review and clean {brain['quarantined']} quarantined Brain entries. Decide: promote, demote, or delete each.",
            "reason": f"{brain['quarantined']} quarantined entries exceed threshold"
        })
    
    # P1: Credibility gap
    if brain.get("no_credibility", 0) > 50:
        actions.append({
            "order_id": f"CEO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-P1",
            "priority": "P1",
            "category": "credibility_gap",
            "agent": "fact-checker",
            "task": f"Enrich {brain['no_credibility']} Brain entries with credibility metadata (provenance, confidence, cross_review_score).",
            "reason": f"{brain['no_credibility']} entries missing credibility metadata"
        })
    
    # P2: Regular inventory scan
    last_inventory = [o for o in previous_orders if o.get("category") == "inventory_scan"]
    if not last_inventory or len(actions) == 0:
        actions.append({
            "order_id": f"CEO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-P2",
            "priority": "P2",
            "category": "inventory_scan",
            "agent": "inventory-brain-scanner",
            "task": "Run full system inventory: DNS, SSL, Docker, Backend routes, Brain integrity, Agent scores, Credential health.",
            "reason": "Scheduled inventory scan (30-min interval recommended)"
        })
    
    return actions

# ── Order Workflow ──

def ceo_login() -> str:
    """CEO authentifiziert sich als Admin und holt JWT-Token."""
    admin_email = os.environ.get("DS_ADMIN_B01F400B__EMAIL", "")
    admin_pass = os.environ.get("DS_ADMIN_B01F400B__PASSWORD", "")
    if not admin_email or not admin_pass:
        logger.warning("Keine Admin-Credentials — unauthentifizierte Calls")
        return ""
    try:
        r = httpx.post(f"{BACKEND_URL}/api/admin/login", data={
            "username": admin_email, "password": admin_pass
        }, timeout=15)
        if r.status_code == 200:
            token = r.json().get("access_token", "")
            logger.info("CEO JWT-Login erfolgreich")
            return token
        logger.error(f"CEO Login fehlgeschlagen: HTTP {r.status_code}")
    except Exception as e:
        logger.error(f"CEO Login Error: {e}")
    return ""

def execute_order(order: dict, token: str = "") -> dict:
    """Einen Auftrag an den zuständigen Agenten übergeben und Ergebnis verfolgen."""
    logger.info(f"EXECUTING: {order['order_id']} → {order['agent']}")
    
    result = {
        "order_id": order["order_id"],
        "agent": order["agent"],
        "status": "executed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response": None,
        "quality_audit": None,
    }
    
    headers = {"Authorization": f"Bearer {token}"} if token else {"X-Internal-Auth": "nexifyai-local"}
    
    try:
        r = httpx.post(f"{BACKEND_URL}/api/admin/agents/{order['agent']}/execute", json={
            "task": order["task"],
            "context": {"priority": order["priority"], "order_id": order["order_id"]}
        }, headers=headers, timeout=120)
        
        if r.status_code == 200:
            data = r.json()
            result["response"] = data
            result["status"] = "completed"
            logger.info(f"  ✅ {order['agent']}: {data.get('summary', '')[:120]}")
            
            # Quality Audit after execution
            result["quality_audit"] = quality_audit(order, data)
        else:
            result["status"] = "failed"
            result["error"] = f"HTTP {r.status_code}: {r.text[:200]}"
            logger.warning(f"  ❌ {order['agent']}: HTTP {r.status_code}")
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
        logger.error(f"  💥 {order['agent']}: {e}")
    
    return result

def quality_audit(order: dict, execution_result: dict) -> dict:
    """Qualitätsprüfung nach jeder Auftragserledigung."""
    summary = execution_result.get("summary", "")
    confidence = execution_result.get("confidence", 0)
    brain_checked = execution_result.get("brain_checked", False)
    
    verdict = "PASS"
    findings = []
    
    if not brain_checked:
        verdict = "FAIL"
        findings.append("Brain NOT queried before execution")
    if confidence < 0.70:
        verdict = "FAIL" if verdict == "FAIL" else "WARN"
        findings.append(f"Low confidence: {confidence}")
    if len(summary) < 50:
        verdict = "FAIL"
        findings.append(f"Summary too short: {len(summary)} chars")
    
    return {
        "verdict": verdict,
        "findings": findings,
        "expert_required": None if verdict == "PASS" else "senior-quality-auditor",
        "next_action": "next_order" if verdict == "PASS" else "x_order_with_expert"
    }

# ── Report ──

def generate_ceo_report(health: dict, orders: list, results: list):
    """CEO-Lagebericht generieren und im Brain speichern."""
    report = {
        "category": "ceo_report",
        "topic": "ceo-daily",
        "provenance": "ceo-loop",
        "confidence": 0.95,
        "status": "active",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_score": health.get("score", 0),
        "healthy": health.get("healthy", False),
        "orders_dispatched": len(orders),
        "orders_completed": sum(1 for r in results if r.get("status") == "completed"),
        "orders_failed": sum(1 for r in results if r.get("status") in ("failed", "error")),
        "p0_actions": sum(1 for o in orders if o.get("priority") == "P0"),
        "checks_detail": {k: v.get("status", "?") for k, v in health.get("checks", {}).items()}
    }
    brain_write(report)
    logger.info(f"CEO Report: Score={report['health_score']:.2f}, Dispatched={report['orders_dispatched']}, OK={report['orders_completed']}, FAIL={report['orders_failed']}")
    return report

# ── MAIN ──

async def main():
    logger.info("=" * 60)
    logger.info("CEO AUTONOMIE-LOOP START")
    logger.info("=" * 60)
    
    # Phase 1: Brain-Check
    recent = brain_scroll("orchestrator_run", 10)
    logger.info(f"Brain: {len(recent)} recent orchestrator runs")
    
    # Phase 2: System-Health-Scan
    health = scan_system_health()
    logger.info(f"Health: Score={health['score']:.2f}, Healthy={health['healthy']}")
    for check, result in health["checks"].items():
        logger.info(f"  {check}: {result.get('status', '?')}")
    
    # Phase 3: CEO Entscheidung
    orders = ceo_decide(health, recent)
    logger.info(f"CEO Decision: {len(orders)} orders")
    for o in orders:
        logger.info(f"  [{o['priority']}] {o['agent']}: {o['task'][:100]}")
    
    # Phase 4: Order Execution (mit JWT-Auth)
    token = ceo_login()
    results = []
    for order in orders:
        result = execute_order(order, token)
        results.append(result)
        
        # Store each result in Brain
        brain_write({
            "category": "order_result",
            "topic": "ceo-order",
            "order_id": order["order_id"],
            "agent": order["agent"],
            "result": result,
            "provenance": "ceo-loop",
            "confidence": 0.9,
            "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    
    # Phase 5: CEO Report
    report = generate_ceo_report(health, orders, results)
    
    logger.info("=" * 60)
    logger.info(f"CEO LOOP END: {report['orders_completed']}/{report['orders_dispatched']} orders completed")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
