#!/usr/bin/env python3
from event_bus import get_bus, publish
import logging
log = logging.getLogger("drift-events")

class DriftEventDriver:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("brain.sync", self._on_sync, "drift:brain")
        log.info("Drift events active")
    def _on_sync(self, ev):
        publish("watchdog.drift", {"source":"reconciliation"}, "drift-events")

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = DriftEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
