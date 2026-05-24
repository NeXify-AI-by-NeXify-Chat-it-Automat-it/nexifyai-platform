#!/usr/bin/env python3
"""organization_heartbeat.py — Validates all organizational systems are alive. Optimized: no subprocess chains."""
import json, logging, os, subprocess, sys
from datetime import datetime, timezone

log = logging.getLogger("org-hb")

# Use systemctl is-active for lightweight checks instead of subprocess chains
SERVICE_CHECKS = {
    "anton": "anton.service",
    "planner": "anton-planner-runtime.service",
    "event_bus": "nexify-event-bus.service",
    "mcp": "nexify-mcp-daemon.service",
    "cognitive": "nexify-cognitive-runtime.service",
    "chat": "nexify-chat.service",
}

# Direct process/port checks for non-systemd components
PROCESS_CHECKS = {
    "qdrant": ("pgrep", "-x", "qdrant"),
    "anton_cli": ("pgrep", "-f", "anton$"),
}

def check_service(name, svc_name):
    r = subprocess.run(["systemctl", "is-active", svc_name], capture_output=True, text=True, timeout=10)
    status = r.stdout.strip()
    return {"alive": status == "active", "status": status}

def check_process(name, cmd):
    r = subprocess.run(list(cmd), capture_output=True, text=True, timeout=10)
    return {"alive": r.returncode == 0, "pids": len(r.stdout.strip().split()) if r.stdout else 0}

def ping():
    results = {}
    for name, svc in SERVICE_CHECKS.items():
        results[name] = check_service(name, svc)
    for name, cmd in PROCESS_CHECKS.items():
        results[name] = check_process(name, cmd)

    alive = sum(1 for v in results.values() if v.get("alive", False))
    total = len(results)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "alive": alive,
        "total": total,
        "all_alive": alive == total,
        "components": results
    }

def main():
    r = ping()
    print(json.dumps(r, indent=2))
    # Only fail if core components are dead (anton, planner, event_bus)
    core = {k: v for k, v in r["components"].items() if k in ("anton", "planner", "event_bus")}
    if any(not v.get("alive", False) for v in core.values()):
        log.warning("Core component failure detected")
        return 1
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
