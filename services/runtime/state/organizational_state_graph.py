#!/usr/bin/env python3
"""org_state_graph.py -- Live graph of all organizational state: teams, tasks, systems."""
import json, logging, threading, time, uuid
from datetime import datetime, timezone
from collections import defaultdict
from event_bus import get_bus
log = logging.getLogger("org-state-graph")

class OrganizationalStateGraph:
    def __init__(self):
        self._nodes = {}; self._edges = []; self._lock = threading.Lock()
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.cycle", self._on_event, "state:plan")
        self.bus.subscribe("org.team_assembled", self._on_event, "state:team")
        self.bus.subscribe("governance.pass", self._on_event, "state:govpass")
        self.bus.subscribe("governance.fail", self._on_event, "state:govfail")
        log.info("Organizational state graph active")
    def _on_event(self, event):
        with self._lock:
            self._nodes[event["id"]] = {"type":event["type"],"payload":event.get("payload",{}),"ts":event["ts"]}
    def get_graph(self):
        with self._lock: return {"nodes": dict(self._nodes), "total": len(self._nodes)}
    def stats(self):
        with self._lock: return {"nodes": len(self._nodes), "edges": len(self._edges)}

GRAPH = None
def start_graph():
    global GRAPH
    if GRAPH is None: GRAPH = OrganizationalStateGraph(); GRAPH.start()
    return GRAPH

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_graph(); print(json.dumps(GRAPH.stats()))
