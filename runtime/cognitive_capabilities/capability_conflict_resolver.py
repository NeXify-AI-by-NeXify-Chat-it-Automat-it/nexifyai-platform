#!/usr/bin/env python3
"""capability_conflict_resolver.py — Resolves conflicts between competing capability invocations."""
import json, logging, time
from collections import defaultdict
from event_bus import get_bus, publish
log = logging.getLogger("cap-conflict")

LOCKS = defaultdict(lambda: {"holder": None, "timeout": 0})

class CapabilityConflictResolver:
    def __init__(self):
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._check, "conflict:check")
        log.info("Capability conflict resolver active")

    def acquire(self, lock_key, holder, ttl=10):
        now = time.time()
        if LOCKS[lock_key]["holder"] and LOCKS[lock_key]["holder"] != holder and LOCKS[lock_key]["timeout"] > now:
            publish("system.warning", {"msg": f"Conflict on {lock_key}: held by {LOCKS[lock_key]['holder']}"}, "cap-conflict")
            return False
        LOCKS[lock_key] = {"holder": holder, "timeout": now + ttl}
        return True

    def release(self, lock_key):
        LOCKS[lock_key] = {"holder": None, "timeout": 0}

    def _check(self, event):
        cap = event.get("payload",{}).get("cap","")
        agent = event.get("payload",{}).get("agent","")
        if cap.startswith("infra."):
            self.acquire(cap, agent, 15)

RESOLVER = CapabilityConflictResolver()
def start(): RESOLVER.start(); return RESOLVER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start()
    print(f"Acquire infra.restart: {RESOLVER.acquire('infra.restart','test',10)}")
