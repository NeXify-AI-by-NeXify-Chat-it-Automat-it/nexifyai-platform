#!/usr/bin/env python3
"""escalation_reasoner.py — Reasons whether an escalation is warranted and what level."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("escalation-reasoner")

class EscalationReasoner:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("system.error", self._on_error, "escalation:error")
        self.bus.subscribe("org.escalation", self._on_escalation, "escalation:org")
        log.info("Escalation reasoner active")
    def reason(self, situation_type, data=None):
        if situation_type == "system_error":
            return {"level": "P0", "message": "System error requires immediate recovery", "action": "activate_incident_workflow"}
        elif situation_type == "capability_failure":
            failures = (data or {}).get("failures", 0)
            return {"level": "P1" if failures > 5 else "P2", "message": f"Capability failed {failures} times", "action": "reassign_or_retry"}
        return {"level": "P3", "message": "Monitor", "action": "log"}
    def _on_error(self, event): self.reason("system_error")
    def _on_escalation(self, event): self.reason("capability_failure", event.get("payload",{}))

REASONER = EscalationReasoner()
def start(): REASONER.start(); return REASONER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(REASONER.reason("system_error")))
