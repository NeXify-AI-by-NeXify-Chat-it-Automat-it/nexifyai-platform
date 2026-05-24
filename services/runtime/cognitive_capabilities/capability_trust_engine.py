#!/usr/bin/env python3
"""capability_trust_engine.py — Tracks trust scores per capability based on execution history."""
import json, logging, threading
from collections import defaultdict
from event_bus import get_bus
log = logging.getLogger("cap-trust")

class CapabilityTrustEngine:
    def __init__(self):
        self._scores = defaultdict(lambda: 0.5); self._counts = defaultdict(int); self._lock = threading.Lock()
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._on_result, "trust:invoke")
        log.info("Capability trust engine active")

    def _on_result(self, event):
        cap = event.get("payload",{}).get("cap","")
        ok = event.get("payload",{}).get("result","") == "ok"
        with self._lock:
            self._counts[cap] += 1
            if ok: self._scores[cap] = min(1.0, self._scores[cap] + 0.05)
            else: self._scores[cap] = max(0.0, self._scores[cap] - 0.1)

    def score(self, cap_id):
        with self._lock: return {"cap": cap_id, "trust_score": round(self._scores.get(cap_id, 0.5), 3), "invocations": self._counts.get(cap_id, 0)}

TRUST = CapabilityTrustEngine()
def start(): TRUST.start(); return TRUST

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(TRUST.score("github.pr.create")))
