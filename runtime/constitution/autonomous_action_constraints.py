#!/usr/bin/env python3
"""autonomous_action_constraints.py -- Constraint engine for autonomous actions."""
import json, logging
log = logging.getLogger("constraints")

CONSTRAINTS = {
    "never_execute": ["rm -rf /", "shutdown", "reboot", "poweroff"],
    "require_verification": ["systemctl stop", "docker rm", "kill", "chmod -R"],
    "max_duration_seconds": 300,
    "require_audit": ["deployment", "rollback", "restart", "modify"],
}

class AutonomousActionConstraints:
    def check(self, action):
        cmd = action.get("command", action.get("action", ""))
        for pattern in CONSTRAINTS["never_execute"]:
            if pattern in cmd: return {"blocked": True, "reason": f"Action contains blocked pattern: {pattern}"}
        for pattern in CONSTRAINTS["require_verification"]:
            if pattern in cmd: return {"blocked": False, "requires_verification": True, "reason": f"Requires verification: {pattern}"}
        return {"blocked": False}

CONSTRAINTS_ENG = AutonomousActionConstraints()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(CONSTRAINTS_ENG.check({"command":"systemctl stop nginx"})))
