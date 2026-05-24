#!/usr/bin/env python3
"""capability_learning_engine.py -- Learns from MCP capability usage patterns."""
import json, logging, threading, uuid
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("cap-learning")

class CapabilityLearningEngine:
    def __init__(self):
        self._usage = {}; self._patterns = []; self.bus = get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke", self._on_invoke, "caplearn:invoke")
        log.info("Capability learning engine active")
    def _on_invoke(self, event):
        cap = event.get("payload",{}).get("cap","")
        agent = event.get("payload",{}).get("agent","")
        key = f"{agent}:{cap}"
        self._usage[key] = self._usage.get(key, 0) + 1
        if self._usage[key] >= 10:
            publish("learning.pattern", {"pattern":"frequent_usage","agent":agent,"cap":cap,"count":self._usage[key]},"cap-learning")
    def get_usage(self):
        return dict(self._usage)
    def stats(self):
        return {"patterns": len(self._patterns), "usages": len(self._usage)}

LEARN = CapabilityLearningEngine()
def start_learn(): LEARN.start(); return LEARN

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_learn()
