#!/usr/bin/env python3
"""mcp_context_router.py -- Routes MCP invocation context to relevant subsystems."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-ctx")

class MCPContextRouter:
    def __init__(self):
        self.bus = get_bus(); self._contexts = {}

    def start(self):
        self.bus.subscribe("mcp.invoke", self._route, "ctx:route")
        log.info("MCP context router active")

    def _route(self, event):
        cap = event.get("payload",{}).get("cap","")
        agent = event.get("payload",{}).get("agent","")
        if cap.startswith("github."): publish("delivery.pr_created", {"cap": cap, "agent": agent}, "mcp-ctx")
        elif cap.startswith("brain."): publish("brain.sync", {"cap": cap}, "mcp-ctx")
        elif cap.startswith("deployment."): publish("delivery.deploy", {"cap": cap}, "mcp-ctx")

ROUTER = MCPContextRouter()
def start_ctx(): ROUTER.start(); return ROUTER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_ctx()
