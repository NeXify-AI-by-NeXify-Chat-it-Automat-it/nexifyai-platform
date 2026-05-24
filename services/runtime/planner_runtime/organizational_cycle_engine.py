#!/usr/bin/env python3
"""org_cycle_engine.py -- Drives 5/15/30/60min organizational cycles as events."""
import logging, threading, time
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("org-cycle")

class OrgCycleEngine:
    def __init__(self): self._running = False; self.bus = get_bus()
    def start(self):
        self._running = True; threading.Thread(target=self._cycle_loop, daemon=True).start()
        log.info("Org cycle engine active")
    def _cycle_loop(self):
        while self._running:
            m = datetime.now(timezone.utc).minute
            if m % 5 == 0: publish("planner.cycle", {"type":"5min_operational"},"org-cycle")
            if m % 15 == 0: publish("planner.cycle", {"type":"15min_tactical"},"org-cycle")
            if m % 30 == 0: publish("planner.cycle", {"type":"30min_strategic"},"org-cycle")
            if m == 0: publish("planner.cycle", {"type":"60min_enterprise"},"org-cycle")
            time.sleep(60)
    def stop(self): self._running = False

ENG = None
def start_engine():
    global ENG
    if ENG is None: ENG = OrgCycleEngine(); ENG.start()
    return ENG

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_engine(); time.sleep(5)
