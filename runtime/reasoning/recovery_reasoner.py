#!/usr/bin/env python3
"""recovery_reasoner.py — Reasons about optimal recovery strategy."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("recover-reasoner")

RECOVERY_STRATEGIES = {
    "system_error": {"strategy": "restart_and_verify", "tools": ["infra.service.restart","runtime.health"], "confidence": 0.9},
    "capability_failure": {"strategy": "retry_and_escalate", "tools": ["security.audit.log","runtime.health"], "confidence": 0.8},
    "governance_violation": {"strategy": "audit_and_correct", "tools": ["security.audit.log","governance"], "confidence": 0.7},
    "drift": {"strategy": "reconcile", "tools": ["brain.query","brain.store"], "confidence": 0.85},
}

class RecoveryReasoner:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("system.error", self._on_event, "recreason:error")
        self.bus.subscribe("incident.detected", self._on_event, "recreason:incident")
        log.info("Recovery reasoner active")
    def reason(self, incident_type):
        strategy = RECOVERY_STRATEGIES.get(incident_type, {"strategy": "monitor", "tools": [], "confidence": 0.3})
        publish("planner.cycle", {"recovery": strategy["strategy"], "reason": incident_type}, "recovery-reasoner")
        return strategy
    def _on_event(self, event):
        self.reason(event.get("payload",{}).get("severity","system_error"))

REASONER = RecoveryReasoner()
def start(): REASONER.start(); return REASONER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(REASONER.reason("drift")))
