#!/usr/bin/env python3
"""planner_daemon.py -- Persistent planner runtime. No subprocess. Event-driven loop."""
import json, logging, os, sys, threading, time
from datetime import datetime, timezone
sys.path.insert(0, "/services/runtime/events")
from event_bus import get_bus, publish
log = logging.getLogger("planner-daemon")

class PlannerDaemon:
    def __init__(self):
        self.bus = get_bus()
        self._running = False
        self._cycle_count = 0
        self._latest_plan = {}
        self._lock = threading.Lock()

    def start(self):
        self._running = True
        self.bus.subscribe("watchdog.alert", self._on_trigger, "planner:alert")
        self.bus.subscribe("incident.detected", self._on_trigger, "planner:incident")
        self.bus.subscribe("governance.fail", self._on_trigger, "planner:govfail")
        self.bus.subscribe("system.error", self._on_trigger, "planner:syserr")
        log.info("Planner daemon started")
        t = threading.Thread(target=self._bg_loop, daemon=True)
        t.start()

    def stop(self):
        self._running = False

    def _on_trigger(self, event):
        log.info(f"Event trigger: {event['type']}")
        self._run_planning_cycle(event["type"])

    def _bg_loop(self):
        while self._running:
            time.sleep(60)
            self._run_planning_cycle("heartbeat")

    def _run_planning_cycle(self, trigger):
        with self._lock:
            self._cycle_count += 1
            cycle_id = f"plan-{self._cycle_count}"
        plan = {"id": cycle_id, "trigger": trigger, "ts": datetime.now(timezone.utc).isoformat(), "tasks": [], "status": "planned"}
        plan["tasks"].append({"type": "observe", "target": "all", "priority": "P0", "reason": "continuous"})
        plan["tasks"].append({"type": "reconcile", "target": "brain", "priority": "P1", "reason": "truth maintenance"})
        if trigger in ("incident.detected", "system.error"):
            plan["tasks"].append({"type": "recover", "target": "incident", "priority": "P0", "reason": trigger})
        if trigger == "governance.fail":
            plan["tasks"].append({"type": "govern", "target": "policy", "priority": "P1", "reason": "policy violation"})
        plan["tasks"].append({"type": "learn", "target": "brain", "priority": "P2", "reason": "continuous learning"})
        with self._lock:
            self._latest_plan = plan
        publish("planner.cycle", {"plan_id": cycle_id, "tasks": len(plan["tasks"]), "trigger": trigger}, "planner-daemon")
        log.info(f"Cycle {cycle_id}: {len(plan['tasks'])} tasks from {trigger}")
        return plan

    def get_latest_plan(self):
        with self._lock: return dict(self._latest_plan)

DAEMON = None
def start_daemon():
    global DAEMON
    if DAEMON is None: DAEMON = PlannerDaemon(); DAEMON.start()
    return DAEMON

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [planner-daemon] %(message)s")
    d = start_daemon()
    d._run_planning_cycle("startup")
    print(json.dumps(d.get_latest_plan(), indent=2))
