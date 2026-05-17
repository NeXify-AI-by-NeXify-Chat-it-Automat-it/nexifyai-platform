#!/usr/bin/env python3
"""mcp_event_bridge.py -- Bridges MCP invocations to Event Bus events for audit + routing."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-event-bridge")

class MCPEventBridge:
    def __init__(self):
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._on_invoke, "bridge:invoke")
        self.bus.subscribe("mcp.result", self._on_result, "bridge:result")
        log.info("MCP event bridge active")

    def _on_invoke(self, event):
        cap = event.get("payload",{}).get("cap","")
        agent = event.get("payload",{}).get("agent","")
        publish("brain.sync", {"type":"mcp_invoke", "cap": cap, "agent": agent}, "mcp-event-bridge")

    def _on_result(self, event):
        pass

BRIDGE = MCPEventBridge()
def start_bridge(): BRIDGE.start(); return BRIDGE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_bridge()
