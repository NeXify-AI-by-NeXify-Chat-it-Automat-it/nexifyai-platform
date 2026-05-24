#!/usr/bin/env python3
"""governance_reasoner.py — Reasons about governance decisions."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("gov-reasoner")

class GovernanceReasoner:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("governance.fail", self._on_fail, "govreason:fail")
        self.bus.subscribe("governance.pass", self._on_pass, "govreason:pass")
        log.info("Governance reasoner active")
    def reason(self, check_type, context=None):
        if check_type == "fail":
            return {"decision": "block", "reason": "Policy violation detected", "suggested_action": "audit and fix"}
        return {"decision": "allow", "reason": "All checks passed"}
    def _on_fail(self, event): self.reason("fail", event.get("payload",{}))
    def _on_pass(self, event): self.reason("pass", event.get("payload",{}))

REASONER = GovernanceReasoner()
def start(): REASONER.start(); return REASONER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(REASONER.reason("fail")))
