#!/usr/bin/env python3
"""priority_runtime.py -- Priority queue for planner tasks with cooldown + dependency resolution."""
import json, logging, threading, time
from collections import defaultdict
from event_bus import get_bus, publish
log = logging.getLogger("priority-rt")
PRIO = {"P0":0,"P1":1,"P2":2,"P3":3}

class PriorityRuntime:
    def __init__(self):
        self._queues = defaultdict(list); self._lock = threading.Lock(); self._running = False; self.bus = get_bus()
    def start(self):
        self._running = True
        self.bus.subscribe("planner.cycle", self._on_plan, "priority:plan")
        threading.Thread(target=self._dispatch_loop, daemon=True).start()
        log.info("Priority runtime active")
    def _on_plan(self, event):
        tasks = event.get("payload",{}).get("tasks",[])
        with self._lock:
            for t in tasks if isinstance(tasks, list) else []:
                p = PRIO.get(t.get("priority","P3"),3); self._queues[p].append(t)
    def _dispatch_loop(self):
        while self._running:
            with self._lock:
                for p in sorted(self._queues.keys()):
                    if self._queues[p]:
                        task = self._queues[p].pop(0); publish("planner.task", task, "priority-rt"); break
            time.sleep(2)

RT = None
def start_priority():
    global RT
    if RT is None: RT = PriorityRuntime(); RT.start()
    return RT

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_priority(); time.sleep(5)
