#!/usr/bin/env python3
"""mcp_recovery_adapter.py -- Recovery adapter. Rolls back MCP capability invocations on failure."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-recovery")

ROLLBACK_MAP = {
    "github.pr.create": "github.pr.close",
    "deployment.run": "deployment.rollback",
    "infra.restart": "infra.start",
}

class MCPRecoveryAdapter:
    def __init__(self):
        self.bus = get_bus(); self._history = {}

    def start(self):
        self.bus.subscribe("system.error", self._on_error, "recovery:error")
        self.bus.subscribe("mcp.invoke", self._track, "recovery:track")
        log.info("MCP recovery adapter active")

    def _track(self, event):
        cap = event.get("payload",{}).get("cap","")
        call_id = event.get("payload",{}).get("call_id","")
        if cap in ROLLBACK_MAP: self._history[call_id] = cap

    def _on_error(self, event):
        cap = event.get("payload",{}).get("cap","")
        rollback = ROLLBACK_MAP.get(cap)
        if rollback:
            publish("delivery.rollback", {"cap": cap, "rollback_to": rollback}, "mcp-recovery")
            log.info(f"Recovery: {cap} -> {rollback}")

ADAPTER = MCPRecoveryAdapter()
def start_adapter(): ADAPTER.start(); return ADAPTER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_adapter()
