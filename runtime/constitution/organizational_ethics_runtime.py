#!/usr/bin/env python3
"""org_ethics_runtime.py -- Runtime ethics layer preventing harmful autonomous behavior."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("ethics")

ETHICAL_RULES = {
    "no_system_degradation": {"check": lambda a: a.get("type") != "system_degradation", "violation": "System degradation not permitted"},
    "no_data_loss": {"check": lambda a: "delete" not in str(a.get("action","")).lower(), "violation": "Data destruction prohibited"},
    "no_service_isolation": {"check": lambda a: a.get("target") != "last_recovery_endpoint", "violation": "Cannot isolate last recovery route"},
}

class OrgEthicsRuntime:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.action", self._check, "ethics:check")
        log.info("Organizational ethics runtime active")
    def _check(self, event):
        action = event.get("payload",{})
        for name, rule in ETHICAL_RULES.items():
            if not rule["check"](action):
                publish("governance.fail", {"ethics_violation": name, "detail": rule["violation"]}, "ethics-runtime")
                log.warning(f"ETHICS: {rule['violation']}")

ETHICS = OrgEthicsRuntime()
def start(): ETHICS.start(); return ETHICS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
