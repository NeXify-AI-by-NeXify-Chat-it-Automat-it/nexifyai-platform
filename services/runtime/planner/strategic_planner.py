#!/usr/bin/env python3
"""
DEPRECATED: Wird durch services/planner_workflow.py ersetzt.
            Nutze run_planning_cycle() oder run_strategic_cycle().
            Migration: from services.planner_workflow import run_strategic_cycle
            Entfernung geplant: 2026-06-21
"""

"""strategic_planner.py — Analyzes system state, identifies gaps, generates plans."""
import json, logging, os, requests, sys, uuid
from datetime import datetime, timezone
log = logging.getLogger("strategic-planner")
BACKEND = "http://localhost:8001"; QDRANT = "http://localhost:6333"

def analyze_system_state() -> dict:
    health, services, issues = "unknown", {}, []
    try:
        r = requests.get(f"{BACKEND}/api/health", timeout=10)
        if r.status_code == 200:
            health = "healthy"
            services = r.json().get("services", {})
            unhealthy = [k for k,v in services.items() if v.get("status") != "ok"]
            if unhealthy: issues.append({"type": "unhealthy_services", "detail": unhealthy})
    except Exception as e: health = "unreachable"; issues.append({"type": "backend_down", "detail": str(e)})
    return {"health": health, "services": services, "issues": issues}

def generate_strategic_plan(state: dict) -> dict:
    priorities = []
    if state.get("health") != "healthy":
        priorities.append({"priority": "P0", "objective": "Restore system health", "detail": state.get("issues", [])})
    priorities.append({"priority": "P1", "objective": "Run reconciliation cycle", "detail": "All 11 reconciler modules"})
    priorities.append({"priority": "P1", "objective": "Validate convergence", "detail": "Post-deploy checks must pass >= 4/5"})
    priorities.append({"priority": "P2", "objective": "Sync GitHub Projects", "detail": "Push state to enterprise projects"})
    return {"generated": datetime.now(timezone.utc).isoformat(), "priorities": priorities}

def main():
    state = analyze_system_state(); plan = generate_strategic_plan(state)
    r = {**plan, "system_state": state.get("health")}
    print(json.dumps(r, indent=2))
    try:
        point = {"id": str(uuid.uuid4()), "vector": [0.0]*4, "payload": {"category": "strategic_plan", "source": "strategic_planner", **r}}
        requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points": [point]})
    except: pass
    return 0 if state.get("health") == "healthy" else 1
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
