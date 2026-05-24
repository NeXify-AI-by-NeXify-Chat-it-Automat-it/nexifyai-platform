#!/usr/bin/env python3
"""capability_usage_analytics.py — Analytics dashboard for capability usage, frequency, trends."""
import json, logging, threading, time
from collections import defaultdict
from datetime import datetime, timezone
from event_bus import get_bus
log = logging.getLogger("cap-analytics")

class CapabilityUsageAnalytics:
    def __init__(self):
        self._usage = defaultdict(int); self._hourly = defaultdict(lambda: defaultdict(int)); self._lock = threading.Lock()
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._track, "analytics:invoke")
        log.info("Capability usage analytics active")

    def _track(self, event):
        cap = event.get("payload",{}).get("cap","")
        hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
        with self._lock:
            self._usage[cap] += 1
            self._hourly[hour][cap] += 1

    def report(self):
        with self._lock:
            return {"total_invocations": sum(self._usage.values()), "by_capability": dict(sorted(self._usage.items(), key=lambda x: -x[1])[:20]), "hours_tracked": len(self._hourly)}

ANALYTICS = CapabilityUsageAnalytics()
def start(): ANALYTICS.start(); return ANALYTICS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(ANALYTICS.report(), indent=2))
