#!/usr/bin/env python3
"""enterprise_policy_runtime.py -- Runtime policy engine evaluating compliance with organizational policies."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("policy-rt")

POLICIES = {
    "deployment_policy": {"scope": "deployment.*", "requires": ["governance_pass","audit_enabled","recovery_plan"], "auto_remediate": True},
    "security_policy": {"scope": "security.*", "requires": ["audit_enabled","governance_pass"], "auto_remediate": True},
    "brain_policy": {"scope": "brain.*", "requires": ["governance_pass"], "auto_remediate": False},
    "default_policy": {"scope": "*", "requires": ["governance_pass"], "auto_remediate": False},
}

class EnterprisePolicyRuntime:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke", self._check, "policy:check")
        log.info("Enterprise policy runtime active")
    def _check(self, event):
        cap = event.get("payload",{}).get("cap","")
        for name, policy in POLICIES.items():
            scope = policy["scope"]
            if scope.endswith("*") and cap.startswith(scope[:-1]) or scope == cap or scope == "*":
                msg = f"Policy {name} applies to {cap}"
                log.info(msg)
                publish("policy.check", {"policy": name, "cap": cap, "requires": policy["requires"]}, "policy-rt")
                return
        publish("policy.check", {"policy": "default", "cap": cap}, "policy-rt")
    def policies(self): return POLICIES

POLICY_RT = EnterprisePolicyRuntime()
def start(): POLICY_RT.start(); return POLICY_RT

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
