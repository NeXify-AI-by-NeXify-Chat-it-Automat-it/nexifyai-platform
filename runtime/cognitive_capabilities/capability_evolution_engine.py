#!/usr/bin/env python3
"""capability_evolution_engine.py — Evolves the capability fabric based on usage and needs."""
import json, logging, uuid
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("cap-evolution")

class CapabilityEvolutionEngine:
    def __init__(self):
        self._discovered = {}; self.bus = get_bus()

    def start(self):
        self.bus.subscribe("learning.pattern", self._on_pattern, "evolution:pattern")
        self.bus.subscribe("org.escalation", self._on_escalation, "evolution:escalation")
        log.info("Capability evolution engine active")

    def _on_pattern(self, event):
        pattern = event.get("payload",{})
        if pattern.get("type") == "capability_frequency":
            for cap, count in pattern.get("patterns",{}).items():
                if count > 100 and cap not in self._discovered:
                    self._discovered[cap] = {"count": count, "ts": datetime.now(timezone.utc).isoformat()}
                    publish("planner.cycle", {"type": "capability_optimization", "cap": cap, "reason": "high_frequency"}, "cap-evolution")

    def _on_escalation(self, event):
        cap = event.get("payload",{}).get("cap","")
        if cap:
            publish("planner.cycle", {"type": "capability_update", "cap": cap, "reason": "escalation"}, "cap-evolution")
            log.info(f"Evolution trigger: {cap} due to escalation")

EVOLVE = CapabilityEvolutionEngine()
def start(): EVOLVE.start(); return EVOLVE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
