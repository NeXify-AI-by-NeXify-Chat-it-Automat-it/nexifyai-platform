#!/usr/bin/env python3
"""planner_memory_sync.py -- Syncs planner state to Brain for persistence."""
import json, logging, requests, threading, time, uuid
from datetime import datetime, timezone
from event_bus import get_bus
log = logging.getLogger("planner-memory")
QDRANT = "http://localhost:6333"

class PlannerMemorySync:
    def __init__(self): self._running = False; self.bus = get_bus()
    def start(self):
        self._running = True
        self.bus.subscribe("planner.cycle", self._on_plan, "memory:plan")
        threading.Thread(target=self._sync_loop, daemon=True).start()
        log.info("Planner memory sync active")
    def _on_plan(self, event):
        try:
            point = {"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":"planner_cycle","source":"planner_memory_sync","event":event,"ts":datetime.now(timezone.utc).isoformat()}}
            requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[point]}, timeout=10)
        except: pass
    def _sync_loop(self):
        while self._running: time.sleep(120)

MEM = None
def start_memory():
    global MEM
    if MEM is None: MEM = PlannerMemorySync(); MEM.start()
    return MEM

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_memory(); time.sleep(5)
