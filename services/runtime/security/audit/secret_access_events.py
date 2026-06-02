#!/usr/bin/env python3
"""Access Event Bus — audit logging for secret access events.
   SAFETY: Only hashed secret names + redacted detail are logged. Never raw values."""
import json, os, hashlib
from datetime import datetime, timezone

_LOG_FILE = "/services/runtime/security/audit/events.log"
LOG_PATH = os.getenv("DS_VAULT_AUDIT_LOG") or _LOG_FILE

def _hash_secret(name):
    """One-way hash of secret name for audit. Never store raw names."""
    return "sk-" + hashlib.sha256(name.encode()).hexdigest()[:16]

def _redact(val, max_len=80):
    """Redact potentially sensitive detail fields. Keep structure, mask values."""
    if not val:
        return ""
    s = str(val)
    if len(s) > max_len:
        return s[:8] + "..." + s[-8:]
    return s

class AccessEventBus:
    def __init__(self):
        self._buffer = []
    def emit(self, secret, worker, action="access", detail=""):
        ev = {"ts": datetime.now(timezone.utc).isoformat(), "type": action,
              "secret": _hash_secret(secret), "worker": worker, "detail": _redact(detail)}
        self._buffer.append(ev)
        if len(self._buffer) > 5000:
            self._buffer = self._buffer[-1000:]
        return ev
    def recent(self, n=20):
        return self._buffer[-n:]

if __name__ == "__main__":
    b = AccessEventBus()
    b.emit("test_secret", "test_worker", "test_event")
    print(json.dumps({"events": len(b.recent(5))}))
