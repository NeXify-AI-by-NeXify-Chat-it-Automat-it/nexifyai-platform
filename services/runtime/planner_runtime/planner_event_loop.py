#!/usr/bin/env python3
"""planner_event_loop.py -- Event loop connecting planner daemon to runtime events."""
import logging, threading, time
from planner_daemon import start_daemon
from event_bus import get_bus
log = logging.getLogger("planner-loop")

class PlannerEventLoop:
    def __init__(self):
        self.daemon = start_daemon(); self.bus = get_bus(); self._running = False
    def start(self):
        self._running = True; threading.Thread(target=self._loop, daemon=True).start(); log.info("Planner event loop active")
    def _loop(self):
        while self._running: time.sleep(5)
    def stop(self): self._running = False; self.daemon.stop()

LOOP = None
def start_loop():
    global LOOP
    if LOOP is None: LOOP = PlannerEventLoop(); LOOP.start()
    return LOOP

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_loop(); print("Event loop active")
