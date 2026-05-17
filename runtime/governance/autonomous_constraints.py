#!/usr/bin/env python3
"""autonomous_constraints.py — Hard constraints on autonomous execution."""
import json, logging, os, sys
log = logging.getLogger("auto-constraints")

HARD_BLOCKS = ["rm -rf /","rm -rf /*","mkfs","dd if=","format",
               ":(){ :|:& };:","shutdown","reboot","poweroff","halt",
               "iptables -F","iptables -X","iptables -P INPUT DROP"]

GOVERNANCE_GATED = ["systemctl stop","systemctl disable","systemctl mask",
                    "docker rm","docker rmi","docker system prune",
                    "chmod -R","chown -R","usermod","groupmod",
                    "ufw disable","ufw reset"]

class AutonomousConstraints:
    def check(self, action: dict) -> dict:
        cmd = action.get("command", action.get("action", ""))
        for b in HARD_BLOCKS:
            if b in cmd:
                return {"blocked":True,"reason":f"HARD BLOCK: {b}","fatal":True}
        for g in GOVERNANCE_GATED:
            if g in cmd and not action.get("governance_approved"):
                return {"blocked":True,"reason":f"Governance gated: {g}","fatal":False}
        return {"blocked":False,"reason":"ok"}
    def is_irreversible(self, action: dict) -> bool:
        return action.get("risk_score",0) >= 8 or action.get("type") in ["deployment","destructive"]

CONSTRAINTS = AutonomousConstraints()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tests = [{"command":"rm -rf /"},{"command":"systemctl stop nginx"},{"command":"npm install"}]
    for t in tests:
        r = CONSTRAINTS.check(t)
        print(f"{t['command']:40s} -> {'BLOCKED' if r['blocked'] else 'ALLOWED'}: {r['reason']}")