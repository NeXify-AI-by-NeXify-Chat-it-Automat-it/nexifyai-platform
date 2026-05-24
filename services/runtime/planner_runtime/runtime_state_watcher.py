#!/usr/bin/env python3
"""runtime_state_watcher.py -- Watches runtime state, publishes events on changes."""
import logging, threading, time, requests
from event_bus import get_bus, publish
log = logging.getLogger("state-watcher")

class RuntimeStateWatcher:
    def __init__(self):
        self._running = False; self._last_state = {}; self.bus = get_bus()
    def start(self):
        self._running = True; threading.Thread(target=self._watch_loop, daemon=True).start(); log.info("Runtime state watcher active")
    def _watch_loop(self):
        while self._running:
            try:
                r = requests.get("http://localhost:6333/collections/nexifyai_brain", timeout=5)
                if r.status_code == 200:
                    brain = r.json().get("result",{}).get("points_count",0)
                    if self._last_state.get("brain") != brain:
                        publish("brain.sync", {"vectors": brain, "changed": True}, "state-watcher")
                        self._last_state["brain"] = brain
            except: pass
            publish("runtime.health", {"status": "ok"}, "state-watcher")
            time.sleep(15)
    def stop(self): self._running = False

WATCHER = None
def start_watcher():
    global WATCHER
    if WATCHER is None: WATCHER = RuntimeStateWatcher(); WATCHER.start()
    return WATCHER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_watcher(); time.sleep(5)
