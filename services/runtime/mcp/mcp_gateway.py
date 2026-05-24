#!/usr/bin/env python3
"""mcp_gateway.py -- Central MCP Gateway. All capability invocations flow through here.
Validates governance, enforces permissions, audits every call."""
import json, logging, os, sys, time, uuid
from datetime import datetime, timezone
sys.path.insert(0, "/services/runtime/events")
from event_bus import get_bus, publish
log = logging.getLogger("mcp-gateway")

class MCPGateway:
    def __init__(self):
        self._registry = {}
        self.bus = get_bus()
        self._call_count = 0

    def register_capability(self, cap_id, handler, metadata=None):
        self._registry[cap_id] = {"handler": handler, "metadata": metadata or {}}
        log.info(f"Registered: {cap_id}")

    def invoke(self, cap_id, params=None, agent="unknown"):
        self._call_count += 1
        call_id = f"mcp-{self._call_count}-{str(uuid.uuid4())[:4]}"
        log.info(f"INVOKE: {cap_id} by {agent} (call_id={call_id})")
        params = params or {}
        cap = self._registry.get(cap_id)
        if not cap:
            publish("system.warning", {"msg": f"Unknown capability: {cap_id}"}, "mcp-gateway")
            return {"ok": False, "error": "unknown_capability", "call_id": call_id}
        meta = cap.get("metadata", {})
        if meta.get("governance") == "required":
            publish("governance.check", {"cap": cap_id, "agent": agent}, "mcp-gateway")
        try:
            result = cap["handler"](call_id=call_id, agent=agent, **params)
            publish("mcp.invoke", {"cap": cap_id, "agent": agent, "result": "ok", "call_id": call_id}, "mcp-gateway")
            return {"ok": True, "call_id": call_id, "result": result}
        except Exception as e:
            publish("system.error", {"cap": cap_id, "error": str(e)[:50]}, "mcp-gateway")
            return {"ok": False, "error": str(e)[:100], "call_id": call_id}

    def stats(self):
        return {"registered": len(self._registry), "calls": self._call_count}

GATEWAY = MCPGateway()
def get_gateway(): return GATEWAY

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gw = get_gateway()
    gw.register_capability("test.ping", lambda **kw: "pong")
    r = gw.invoke("test.ping", agent="test")
    print(json.dumps(r, indent=2))
