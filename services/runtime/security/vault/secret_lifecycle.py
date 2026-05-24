#!/usr/bin/env python3
"""Secret Lifecycle — manages creation to revocation flow."""
import json, os
from datetime import datetime, timezone

def scan_env():
    secrets = {}
    for k, v in os.environ.items():
        if k.startswith("DS_"):
            group = k.split("__")[0].lower()
            field = k.split("__")[1].lower() if "__" in k else "value"
            secrets.setdefault(group, {"fields": [], "total_len": 0})
            secrets[group]["fields"].append(field)
            secrets[group]["total_len"] += len(v) if v else 0
    return secrets

def check_health():
    issues = []
    env = scan_env()
    for group in env:
        for field in env[group]["fields"]:
            base_name = group.upper().split("__")[0] if "__" in group.upper() else group.upper()
            env_name = f"DS_{base_name}__{field}"
            val = os.environ.get(env_name)
            if not val or len(val) < 3:
                issues.append(f"{env_name}: missing or too short")
    return issues

if __name__ == "__main__":
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "groups": len(scan_env()), "health_issues": check_health(), "status": "degraded" if check_health() else "healthy"}
    print(json.dumps(report, indent=2))
