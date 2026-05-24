#!/usr/bin/env python3
"""planner_events.py -- Event-driven planner driver. Subscribes to runtime events."""
import logging, subprocess, threading, time
from event_bus import get_bus, publish
log = logging.getLogger("planner-events")

class PlannerEventDriver:
    def __init__(self):
        self.bus = get_bus()
        self._cooldowns = {}

    def start(self):
        self.bus.subscribe("watchdog.alert", self._on_alert, "planner:alert")
        self.bus.subscribe("incident.detected", self._on_event, "planner:incident")
        self.bus.subscribe("governance.fail", self._on_event, "planner:govfail")
        self.bus.subscribe("delivery.rollback", self._on_event, "planner:rollback")
        log.info("Planner event driver active")

    def _trigger(self, reason):
        now = time.time()
        if now - self._cooldowns.get(reason, 0) < 30: return
        self._cooldowns[reason] = now
        log.info(f"Triggering planning: {reason}")
        def _run():
            try:
                r = subprocess.run(["python3","/services/runtime/planner/autonomous_program_manager.py"], capture_output=True, text=True, timeout=60)
                publish("planner.cycle", {"trigger": reason, "rc": r.returncode}, "planner-events")
            except: log.error(f"Planner trigger failed: {reason}")
        threading.Thread(target=_run, daemon=True).start()

    def _on_alert(self, ev): self._trigger("alert")
    def _on_event(self, ev): self._trigger(ev["type"])

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = PlannerEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Planner events running")
