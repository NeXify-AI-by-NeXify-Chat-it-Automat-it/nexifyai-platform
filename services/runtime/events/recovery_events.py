#!/usr/bin/env python3
from event_bus import get_bus, publish
import logging
log = logging.getLogger("recovery-events")

class RecoveryEventDriver:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("watchdog.alert", self._on_alert, "recovery:alert")
        log.info("Recovery events active")
    def _on_alert(self, ev):
        sev = ev.get("payload",{}).get("severity","info")
        if sev == "critical":
            publish("incident.detected", {"source":"watchdog","detail":ev.get("payload",{}).get("detail","")}, "recovery-events")

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = RecoveryEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
