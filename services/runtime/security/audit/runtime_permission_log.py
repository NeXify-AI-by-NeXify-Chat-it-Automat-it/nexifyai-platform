#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone

LOG = "/services/runtime/security/audit/permission_log.json"

class PermissionLog:
    def log(self, worker_id, capability, resource, action, allowed=True, reason=""):
        entry = {"ts": datetime.now(timezone.utc).isoformat(),
                 "worker": worker_id, "capability": capability,
                 "resource": resource, "action": action,
                 "allowed": allowed, "reason": reason}
        log = []
        if os.path.exists(LOG):
            with open(LOG) as f: log = json.load(f)
        log.append(entry)
        if len(log) > 1000: log = log[-1000:]
        with open(LOG, "w") as f: json.dump(log, f, indent=2)
        return entry
    def check_permission(self, worker, resource, action):
        if not os.path.exists(LOG): return True
        with open(LOG) as f: log = json.load(f)
        # Last matching permission check wins
        relevant = [e for e in log if e["worker"]==worker and e["resource"]==resource]
        if not relevant: return True
        return relevant[-1]["allowed"]

if __name__ == "__main__":
    p = PermissionLog()
    p.log("test_worker", "read", "mongo", "access", True)
    print(json.dumps({"ok": True}))
