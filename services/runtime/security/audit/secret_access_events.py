#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone

class AccessEventBus:
    def __init__(self):
        self.log = "/services/runtime/security/audit/events.log"
        os.makedirs(os.path.dirname(self.log), exist_ok=True)
    def emit(self, secret, worker, action="access", detail=""):
        ev = {"ts": datetime.now(timezone.utc).isoformat(), "type": action,
              "secret": secret, "worker": worker, "detail": detail}
        with open(self.log, "a") as f:
            f.write(json.dumps(ev) + "\n")
        return ev
    def recent(self, n=20):
        if not os.path.exists(self.log): return []
        with open(self.log) as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:]]

if __name__ == "__main__":
    b = AccessEventBus()
    b.emit("test_secret", "test_worker", "test_event")
    print(json.dumps({"events": len(b.recent(5))}))
