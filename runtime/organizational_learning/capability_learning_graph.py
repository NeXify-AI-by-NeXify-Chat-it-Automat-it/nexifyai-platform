#!/usr/bin/env python3
"""cap_learning_graph.py -- Graphs capability usage patterns over time."""
import json,logging
from collections import defaultdict
log=logging.getLogger("cap-learn-graph")

class CapabilityLearningGraph:
    def __init__(self):self._graph=defaultdict(list)
    def record(self,cap,outcome):
        self._graph[cap].append(outcome)
    def success_rate(self,cap):
        results=self._graph.get(cap,[])
        if not results:return 0
        return sum(1 for r in results if r.get("success"))/len(results)
    def stats(self):
        return {"tracked":len(self._graph),"total_events":sum(len(v) for v in self._graph.values())}

CAP_LEARN_GRAPH=CapabilityLearningGraph()
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    CAP_LEARN_GRAPH.record("github.pr.create",{"success":True});print(json.dumps(CAP_LEARN_GRAPH.stats()))
