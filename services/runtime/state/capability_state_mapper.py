#!/usr/bin/env python3
"""capability_state_mapper.py -- Maps current state of each capability/team in the organization."""
import json, logging, threading, time
from collections import defaultdict
from event_bus import get_bus
log = logging.getLogger("cap-state")

CAPABILITIES = {"reconciliation":"active","watchdog":"active","governance":"active","delivery":"active","recovery":"active","learning":"active","planner":"active","infrastructure":"active","security":"active","observability":"active"}

class CapabilityStateMapper:
    def __init__(self):
        self._states = dict(CAPABILITIES); self._lock = threading.Lock(); self.bus = get_bus()
    def start(self):
        self.bus.subscribe("system.error", self._on_error, "capstate:error")
        log.info("Capability state mapper active")
    def _on_error(self, event):
        pass  # mark affected capability as degraded
    def get_state(self, team=None):
        with self._lock:
            if team: return {team: self._states.get(team,"unknown")}
            return dict(self._states)
    def set_state(self, team, state):
        with self._lock: self._states[team] = state

MAP = None
def start_mapper():
    global MAP
    if MAP is None: MAP = CapabilityStateMapper(); MAP.start()
    return MAP

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_mapper(); print(json.dumps(MAP.get_state()))
