#!/usr/bin/env python3
"""mcp_agent_permissions.py -- Agent permission matrix. Which agents can call which capabilities."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-perms")

# Agent -> allowed capability patterns
PERMISSIONS = {
    "executive": ["*"],
    "orchestration": ["planner.*", "github.*", "brain.*", "runtime.*"],
    "governance": ["governance.*", "audit.*", "policy.*"],
    "reconciliation": ["brain.*", "reconciliation.*"],
    "watchdog": ["monitor.*", "watchdog.*", "runtime.health"],
    "delivery": ["github.pr.create", "deployment.*", "docker.*"],
    "recovery": ["deployment.rollback", "infra.restart", "runtime.shell"],
    "security": ["secret.*", "audit.*", "policy.*"],
    "infrastructure": ["docker.*", "runtime.*", "infra.*"],
}

class MCPAgentPermissions:
    def __init__(self):
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("mcp.invoke", self._check, "perm:check")
        log.info("MCP agent permissions active")

    def allowed(self, agent, cap_id):
        perms = PERMISSIONS.get(agent, [])
        for p in perms:
            if p == "*": return True
            if p.endswith("*") and cap_id.startswith(p[:-1]): return True
            if p == cap_id: return True
        return False

    def _check(self, event):
        cap = event.get("payload",{}).get("cap","")
        agent = event.get("payload",{}).get("agent","unknown")
        if not self.allowed(agent, cap):
            publish("governance.fail", {"cap": cap, "agent": agent, "reason": "not_authorized"}, "mcp-perms")

PERMS = MCPAgentPermissions()
def start_perms(): PERMS.start(); return PERMS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_perms()
    print(f"Delivery can create PR: {PERMS.allowed('delivery','github.pr.create')}")
