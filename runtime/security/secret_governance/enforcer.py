#!/usr/bin/env python3
"""Policy Enforcer -- checks secret compliance before deployments."""
import os, json, sys
sys.path.insert(0, "/runtime/security/rotation")
sys.path.insert(0, "/runtime/security/vault")
sys.path.insert(0, "/runtime/security/policy")

class PolicyEnforcer:
    def check_pre_deployment(self):
        issues = []
        # Gate check
        from secret_gate import check_secret_health
        health = check_secret_health()
        if health["status"] != "healthy":
            issues.append("SEC-006: Secret health check failed")
        # Rotation check
        from rotation_engine import RotationEngine
        eng = RotationEngine()
        due = eng.check_due()
        if due:
            issues.append(f"SEC-005: {len(due)} credentials due for rotation")
        # Expiry check
        from expiry_monitor import ExpiryMonitor
        em = ExpiryMonitor()
        exp = em.check()
        if exp.get("expired"):
            issues.append(f"SEC-003: {len(exp['expired'])} expired credentials")
        return {"pass": len(issues)==0, "issues": issues}
    def block_if_unhealthy(self):
        result = self.check_pre_deployment()
        if not result["pass"]:
            print("DEPLOYMENT BLOCKED by Secret Governance Policy", file=sys.stderr)
            for i in result["issues"]:
                print(f"  - {i}", file=sys.stderr)
            sys.exit(1)
        print("Secret Governance: PASS")
        sys.exit(0)

if __name__ == "__main__":
    e = PolicyEnforcer()
    e.block_if_unhealthy()
