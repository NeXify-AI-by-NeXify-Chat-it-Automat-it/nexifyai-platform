#!/usr/bin/env python3
"""live_runtime_topology.py -- Live topological view of all runtime systems and connections."""
import json, logging, os, threading, time
from datetime import datetime, timezone
from event_bus import get_bus
log = logging.getLogger("live-topo")

class LiveRuntimeTopology:
    def __init__(self):
        self._topology = {}; self._lock = threading.Lock(); self.bus = get_bus()
    def start(self):
        self._scan()
        self.bus.subscribe("runtime.health", self._on_health, "topo:health")
        threading.Thread(target=self._scan_loop, daemon=True).start()
        log.info("Live runtime topology active")
    def _scan(self):
        systems = [d for d in ["/runtime","/brain","/opt/nexifyai-platform/runtime"] if os.path.exists(d)]
        topo = {}
        for base in systems:
            for root, dirs, files in os.walk(base):
                py_count = len([f for f in files if f.endswith('.py')])
                if py_count > 0:
                    rel = root.replace(base,"")
                    topo[f"{os.path.basename(base)}{rel}"] = {"path":root,"modules":py_count,"type":"runtime"}
        with self._lock: self._topology = topo
    def _scan_loop(self):
        while True: time.sleep(300)
    def _on_health(self, event): pass
    def get_topo(self):
        with self._lock: return dict(self._topology)

TOPO = None
def start_topo():
    global TOPO
    if TOPO is None: TOPO = LiveRuntimeTopology(); TOPO.start()
    return TOPO

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_topo()
    print(json.dumps(TOPO.get_topo(), indent=2)[:500])
