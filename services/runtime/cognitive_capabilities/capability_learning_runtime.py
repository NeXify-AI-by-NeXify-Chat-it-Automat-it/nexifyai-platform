#!/usr/bin/env python3
"""capability_learning_runtime.py — Learns optimal capability sequences from execution history."""
import json, logging, threading
from collections import defaultdict
from event_bus import get_bus, publish
log = logging.getLogger("cap-learning-rt")

class CapabilityLearningRuntime:
    def __init__(self):
        self._sequences = defaultdict(list); self._optimal = {}; self.bus = get_bus()

    def start(self):
        self.bus.subscribe("planner.workflow", self._on_workflow, "caplearn:wf")
        log.info("Capability learning runtime active")

    def _on_workflow(self, event):
        steps = event.get("payload",{}).get("steps",[])
        for s in steps if isinstance(steps, list) else []:
            self._sequences[s].append(event.get("payload",{}).get("workflow_id",""))
        if len(self._sequences) > 10:
            publish("learning.pattern", {"type":"capability_frequency","patterns":{k:len(v) for k,v in self._sequences.items()}},"cap-learning-rt")

LEARN = CapabilityLearningRuntime()
def start(): LEARN.start(); return LEARN

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
