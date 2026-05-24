#!/usr/bin/env python3
from event_bus import get_bus
import logging
log = logging.getLogger("delivery-events")

class DeliveryEventDriver:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.cycle", self._on_cycle, "delivery:plan")
        self.bus.subscribe("governance.pass", self._on_gov, "delivery:gov")
        log.info("Delivery events active")
    def _on_cycle(self, ev): pass
    def _on_gov(self, ev): pass

DRIVER = None
def start():
    global DRIVER
    if DRIVER is None: DRIVER = DeliveryEventDriver(); DRIVER.start()
    return DRIVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
