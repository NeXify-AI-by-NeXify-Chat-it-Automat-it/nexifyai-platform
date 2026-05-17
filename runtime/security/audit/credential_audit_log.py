#!/usr/bin/env python3
"""Credential Audit Log — tracks every secret access event."""
import json, os
from datetime import datetime, timezone

class AuditLog:
    def __init__(self):
        self.log_path = "/runtime/security/audit/events.log"
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
    def log(self, event_type, secret, worker, detail=""):
        entry = {"ts": datetime.now(timezone.utc).isoformat(), "type": event_type, "secret": secret, "worker": worker, "detail": detail}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry)+"\n")
    def recent(self, n=20):
        if not os.path.exists(self.log_path): return []
        with open(self.log_path) as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:]]
    def anomalies(self):
        events = self.recent(200)
        # Simple anomaly: same secret accessed >10 times in last 200 events
        counts = {}
        for e in events:
            counts[e["secret"]] = counts.get(e["secret"], 0) + 1
        return {s: c for s, c in counts.items() if c > 10}

if __name__ == "__main__":
    audit = AuditLog()
    print(json.dumps({"events_logged": len(audit.recent()) if os.path.exists(audit.log_path) else 0, "anomalies": audit.anomalies()}, indent=2))
