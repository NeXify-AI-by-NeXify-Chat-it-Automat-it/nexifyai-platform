#!/usr/bin/env python3
"""mcp_audit_engine.py -- Audits every MCP capability invocation for compliance."""
import json, logging, threading, uuid
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("mcp-audit")

class MCPAuditEngine:
    def __init__(self):
        self._audit_log = []; self._lock = threading.Lock(); self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._audit, "audit:invoke")
        log.info("MCP audit engine active")

    def _audit(self, event):
        entry = {"id": str(uuid.uuid4())[:8], "type": event["type"], "payload": event.get("payload",{}), "ts": event.get("ts", datetime.now(timezone.utc).isoformat())}
        with self._lock:
            self._audit_log.append(entry)
            if len(self._audit_log) > 1000: self._audit_log = self._audit_log[-500:]

    def get_log(self, limit=50):
        with self._lock: return list(self._audit_log[-limit:])

    def stats(self):
        with self._lock: return {"total_audited": len(self._audit_log)}

ENG = MCPAuditEngine()
def start_audit(): ENG.start(); return ENG

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_audit()
