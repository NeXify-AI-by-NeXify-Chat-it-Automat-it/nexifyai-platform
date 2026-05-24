#!/usr/bin/env python3
"""mcp_security_governor.py -- Security governor for MCP capabilities. Prevents unauthorized access."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-security")

SECURITY_LEVELS = {"critical": ["github.infra.*","deployment.*","secret.*"], "high": ["github.pr.create","deployment.rollback"], "medium": ["github.issue.create","brain.*"], "low": ["monitor.*","health.*"]}

class MCPSecurityGovernor:
    def __init__(self):
        self.bus = get_bus(); self._allowed_agents = set()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._on_invoke, "security:invoke")
        log.info("MCP security governor active")

    def _on_invoke(self, event):
        cap = event.get("payload",{}).get("cap","")
        for level, patterns in SECURITY_LEVELS.items():
            for p in patterns:
                if p.endswith("*") and cap.startswith(p[:-1]):
                    if level == "critical":
                        publish("governance.check", {"cap": cap, "level": level}, "mcp-security")
                    return

GOV = MCPSecurityGovernor()
def start_gov(): GOV.start(); return GOV

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_gov()
