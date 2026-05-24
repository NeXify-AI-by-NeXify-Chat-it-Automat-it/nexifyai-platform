#!/usr/bin/env python3
"""capability_recovery_engine.py — Recovers from failed capability invocations."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("cap-recovery")

RECOVERY_ACTIONS = {
    "github.pr.create": {"type": "retry", "max_retries": 3, "cooldown": 5},
    "infra.service.restart": {"type": "escalate", "escalation_target": "recovery_team"},
    "brain.store": {"type": "retry", "max_retries": 2, "cooldown": 2},
}

class CapabilityRecoveryEngine:
    def __init__(self):
        self._retries = {}; self.bus = get_bus()

    def start(self):
        self.bus.subscribe("system.error", self._on_fail, "caprecovery:fail")
        log.info("Capability recovery engine active")

    def _on_fail(self, event):
        cap = event.get("payload",{}).get("cap","")
        action = RECOVERY_ACTIONS.get(cap, {"type":"log"})
        call_id = event.get("payload",{}).get("call_id","")
        if action["type"] == "retry":
            key = f"{cap}:{call_id}"
            self._retries[key] = self._retries.get(key, 0) + 1
            if self._retries[key] <= action.get("max_retries", 1):
                publish("mcp.invoke", {"cap": cap, "retry": True, "call_id": f"{call_id}-retry-{self._retries[key]}"}, "cap-recovery")
                log.info(f"Retry {self._retries[key]}/{action['max_retries']} for {cap}")
        elif action["type"] == "escalate":
            publish("org.escalation", {"cap": cap, "action": "recovery_required"}, "cap-recovery")

ENGINE = CapabilityRecoveryEngine()
def start(): ENGINE.start(); return ENGINE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
