#!/usr/bin/env python3
"""org_reasoning_engine.py — Central reasoning engine. Given situation, recommends organizational action."""
import json, logging, uuid
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("org-reasoning")

REASONING_PATTERNS = {
    "incident": {"action": "activate_incident_workflow", "capabilities_needed": ["observe","recover","govern"], "priority": "P0"},
    "drift": {"action": "reconcile", "capabilities_needed": ["observe","reconcile"], "priority": "P1"},
    "governance_violation": {"action": "audit_and_fix", "capabilities_needed": ["govern","audit"], "priority": "P1"},
    "deployment": {"action": "execute_deployment_workflow", "capabilities_needed": ["govern","deliver","converge"], "priority": "P2"},
    "optimization": {"action": "recommend_improvement", "capabilities_needed": ["observe","learn"], "priority": "P3"},
}

class OrganizationalReasoningEngine:
    def __init__(self):
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("incident.detected", lambda e: self.reason("incident", e), "reason:incident")
        self.bus.subscribe("watchdog.drift", lambda e: self.reason("drift", e), "reason:drift")
        self.bus.subscribe("governance.fail", lambda e: self.reason("governance_violation", e), "reason:govfail")
        log.info("Organizational reasoning engine active")

    def reason(self, situation, event=None):
        pattern = REASONING_PATTERNS.get(situation)
        if not pattern: return {"situation": situation, "action": "unknown", "confidence": 0}
        result = {"reasoning_id": str(uuid.uuid4())[:8], "situation": situation, "action": pattern["action"], "capabilities": pattern["capabilities_needed"], "priority": pattern["priority"], "ts": datetime.now(timezone.utc).isoformat(), "confidence": 0.85}
        publish("planner.cycle", {"reasoning": situation, "action": pattern["action"]}, "org-reasoning")
        return result

ENG = OrganizationalReasoningEngine()
def start(): ENG.start(); return ENG

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(ENG.reason("drift"), indent=2))
