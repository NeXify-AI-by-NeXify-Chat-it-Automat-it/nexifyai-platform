#!/usr/bin/env python3
"""taskgraph_runtime.py -- Live task graph of all active organizational work."""
import json, logging, threading, time, uuid
from datetime import datetime, timezone
from event_bus import get_bus
log = logging.getLogger("taskgraph")

class TaskGraphRuntime:
    def __init__(self):
        self._tasks = {}; self._lock = threading.Lock(); self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.cycle", self._on_plan, "taskgraph:plan")
        self.bus.subscribe("org.team_assembled", self._on_team, "taskgraph:team")
        log.info("TaskGraph runtime active")
    def _on_plan(self, event):
        tasks = event.get("payload", {}).get("tasks", [])
        with self._lock:
            for t in tasks if isinstance(tasks, list) else []:
                tid = str(uuid.uuid4())[:8]; self._tasks[tid] = {"id":tid,"type":t.get("type"),"status":"planned","ts":datetime.now(timezone.utc).isoformat()}
    def _on_team(self, event): pass
    def stats(self): return {"total": len(self._tasks)}

GRAPH = None
def start_graph():
    global GRAPH
    if GRAPH is None: GRAPH = TaskGraphRuntime(); GRAPH.start()
    return GRAPH

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_graph(); print(json.dumps(GRAPH.stats()))
