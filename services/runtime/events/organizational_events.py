#!/usr/bin/env python3
from event_bus import get_bus, publish
import logging
log = logging.getLogger("org-events")

class OrgEventDriver:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.task", self._on_task, "org:task")
        self.bus.subscribe("system.warning", self._on_warn, "org:warn")
        log.info("Org events active")
    def _on_task(self, ev):
        publish("org.team_assembled", {"task":ev.get("payload",{}).get("task_id","")}, "org-events")
    def _on_warn(self, ev): pass

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = OrgEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
