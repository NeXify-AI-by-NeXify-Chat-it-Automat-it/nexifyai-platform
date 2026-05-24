#!/usr/bin/env python3
"""capability_escalation_engine.py — Escalates capability invocations that fail or exceed thresholds."""
import json, logging, threading, time
from collections import defaultdict
from event_bus import get_bus, publish
log = logging.getLogger("cap-escalation")

class CapabilityEscalationEngine:
    def __init__(self):
        self._failures = defaultdict(int); self.bus = get_bus()

    def start(self):
        self.bus.subscribe("system.error", self._on_error, "escalation:error")
        self.bus.subscribe("mcp.invoke", self._on_invoke, "escalation:invoke")
        log.info("Capability escalation engine active")

    def _on_error(self, event):
        cap = event.get("payload",{}).get("cap","")
        self._failures[cap] += 1
        if self._failures[cap] >= 3:
            publish("org.escalation", {"cap": cap, "failures": self._failures[cap], "severity": "critical"}, "escalation-engine")
            log.warning(f"ESCALATION: {cap} failed {self._failures[cap]} times")

    def _on_invoke(self, event):
        cap = event.get("payload",{}).get("cap","")
        self._failures[cap] = max(0, self._failures.get(cap, 0) - 1)

ENG = CapabilityEscalationEngine()
def start(): ENG.start(); return ENG

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
