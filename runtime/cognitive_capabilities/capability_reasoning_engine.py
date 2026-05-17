#!/usr/bin/env python3
"""capability_reasoning_engine.py — Given a goal, recommends the best capability composition."""
import json, logging
from semantic_capability_graph import GRAPH
from event_bus import get_bus, publish
log = logging.getLogger("cap-reasoning")

class CapabilityReasoningEngine:
    def reason(self, goal, context=None):
        caps = GRAPH.find_by_goal(goal)
        if not caps: return {"goal": goal, "found": False, "recommendations": []}
        related = {}
        for c in caps:
            rels = GRAPH.get_related(c)
            related[c] = rels
        publish("planner.cycle", {"reasoning": goal, "candidates": len(caps)}, "cap-reasoning")
        return {"goal": goal, "found": True, "capabilities": caps, "relations": dict(related)}

REASONER = CapabilityReasoningEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(REASONER.reason("delivery"), indent=2))
