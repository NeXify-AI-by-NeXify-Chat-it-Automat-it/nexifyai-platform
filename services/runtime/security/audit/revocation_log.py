#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone

LOG = "/services/runtime/security/audit/revocation_log.json"

class RevocationLog:
    def log(self, secret, reason, operator="auto", layers=None):
        entry = {"ts": datetime.now(timezone.utc).isoformat(),
                 "secret": secret, "reason": reason,
                 "operator": operator, "layers": layers or []}
        log = []
        if os.path.exists(LOG):
            with open(LOG) as f: log = json.load(f)
        log.append(entry)
        if len(log) > 1000: log = log[-1000:]
        with open(LOG, "w") as f: json.dump(log, f, indent=2)
        return entry
    def recent(self, n=10):
        if not os.path.exists(LOG): return []
        with open(LOG) as f:
            log = json.load(f)
        return log[-n:]

if __name__ == "__main__":
    r = RevocationLog()
    r.log("test_secret", "test")
    print(json.dumps({"ok": True, "recent": len(r.recent())}))
