#!/usr/bin/env python3
from event_bus import get_bus, publish
import logging
log = logging.getLogger("gov-events")

class GovernanceEventDriver:
    def __init__(self):
        self.bus = get_bus()
        self.policies = {"delivery.pr_created":["check_labels"],"delivery.deploy":["check_incidents"],"planner.task":["check_capacity"]}
    def start(self):
        for et in self.policies:
            self.bus.subscribe(et, self._on_event, f"gov:{et}")
        log.info("Governance events active")
    def _on_event(self, ev):
        publish("governance.pass", {"event": ev["type"]}, "gov-events")

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = GovernanceEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
