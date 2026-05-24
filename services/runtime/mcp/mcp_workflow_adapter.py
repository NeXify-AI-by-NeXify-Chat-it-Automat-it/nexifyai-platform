#!/usr/bin/env python3
"""mcp_workflow_adapter.py -- Adapts MCP capabilities to workflow execution."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-wf")

class MCPWorkflowAdapter:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("planner.workflow", self._on_workflow, "mcp-wf:wf")
        log.info("MCP workflow adapter active")
    def _on_workflow(self, event):
        payload = event.get("payload",{})
        steps = payload.get("steps", [])
        for step in steps:
            cap_id = step.get("capability","")
            if cap_id: publish("mcp.invoke", {"cap": cap_id, "params": step.get("params",{})}, "mcp-wf")

ADAPTER = MCPWorkflowAdapter()
def start_wf(): ADAPTER.start(); return ADAPTER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_wf()
