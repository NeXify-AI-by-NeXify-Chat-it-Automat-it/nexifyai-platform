#!/usr/bin/env python3
"""mcp_governance_engine.py -- Governance engine for all MCP capability invocations."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("mcp-gov")

class MCPGovernanceEngine:
    def __init__(self):
        self.bus = get_bus(); self._policies = {}

    def start(self):
        self.bus.subscribe("governance.check", self._on_check, "gov:check")
        self.bus.subscribe("mcp.invoke", self._on_invoke, "gov:invoke")
        log.info("MCP governance engine active")

    def add_policy(self, cap_pattern, policy):
        self._policies[cap_pattern] = policy

    def _on_check(self, event):
        cap = event.get("payload",{}).get("cap","")
        for pattern, policy in self._policies.items():
            if pattern.endswith("*") and cap.startswith(pattern[:-1]) or pattern == cap:
                if policy.get("requires_approval"):
                    publish("governance.fail", {"cap": cap, "reason": "requires_approval","policy": policy.get("name","")}, "mcp-gov")
                else:
                    publish("governance.pass", {"cap": cap, "policy": policy.get("name","")}, "mcp-gov")
                return
        publish("governance.pass", {"cap": cap, "policy": "default"}, "mcp-gov")

    def _on_invoke(self, event):
        pass

GOV = MCPGovernanceEngine()
def start_gov(): GOV.start(); return GOV

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_gov()
    GOV.add_policy("deployment.*", {"name":"deploy_policy","requires_approval":True})
    print("Governance engine active")
