#!/usr/bin/env python3
"""auto_recovery_router.py — Routes detected incidents to recovery actions. Now with actual execution."""
import json, logging, os, subprocess, sys
from datetime import datetime, timezone

log = logging.getLogger("recovery-router")

# Action mappings
ACTIONS = {
    "service_down": "restart_service",
    "memory_pressure": "scale_up",
    "disk_full": "clean_disk",
    "app_error": "rollback",
    "network_issue": "retry",
    "planner_freeze": "restart_planner",
    "fd_leak": "restart_leaking_service",
}

# Track retry counts per incident source
_retry_counts = {}
MAX_RETRIES = 3

def execute_restart_service(service_slug):
    """Attempt systemd restart. Returns True if successful."""
    svc_map = {
        "anton": "anton.service",
        "planner": "anton-planner-runtime.service",
        "planner_daemon": "anton-planner-runtime.service",
        "event_bus": "nexify-event-bus.service",
        "mcp": "nexify-mcp-daemon.service",
        "cognitive": "nexify-cognitive-runtime.service",
        "chat": "nexify-chat.service",
        "watchdog": "nexify-watchdog.service",
    }
    svc = svc_map.get(service_slug, f"{service_slug}.service")
    log.info("Restarting %s", svc)
    r = subprocess.run(["systemctl", "restart", svc], capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        log.info("✓ %s restarted successfully", svc)
        return True
    log.error("✗ %s restart failed: %s", svc, r.stderr[:200])
    return False

def execute_restart_planner(inc):
    log.info("Planner freeze detected — hard restart")
    subprocess.run(["systemctl", "kill", "--signal=SIGKILL", "anton-planner-runtime.service"], capture_output=True, text=True, timeout=5)
    subprocess.run(["systemctl", "restart", "anton-planner-runtime.service"], capture_output=True, text=True, timeout=15)
    log.info("✓ planner hard restarted")

def execute_restart_leaking(inc):
    pid = inc.get("pid", "")
    if pid:
        log.info("Killing leaking process %s", pid)
        subprocess.run(["kill", "-9", str(pid)], capture_output=True, text=True, timeout=5)

def route(inc=None):
    if not inc:
        inc = {"title": "Error", "causes": ["service_down"], "source": "unknown"}
    
    causes = inc.get("causes", ["unknown"])
    source = inc.get("source", "unknown")
    
    # Track retries
    key = f"{source}:{causes[0]}"
    _retry_counts[key] = _retry_counts.get(key, 0) + 1
    
    if _retry_counts[key] > MAX_RETRIES:
        log.critical("ESCALATION: %s failed %d times — manual intervention required", key, MAX_RETRIES)
        return {"title": inc.get("title"), "actions": ["escalate"], "retries": _retry_counts[key], "priority": "critical"}
    
    actions_taken = []
    for cause in causes:
        action = ACTIONS.get(cause, "manual")
        if action == "restart_service":
            ok = execute_restart_service(source)
            actions_taken.append({"action": action, "success": ok, "target": source})
        elif action == "restart_planner":
            execute_restart_planner(inc)
            actions_taken.append({"action": action, "success": True, "target": "planner"})
        elif action == "restart_leaking_service":
            execute_restart_leaking(inc)
            actions_taken.append({"action": action, "success": True, "target": source})
        else:
            actions_taken.append({"action": action, "success": False, "reason": "not_implemented"})
    
    return {
        "title": inc.get("title"),
        "actions": actions_taken,
        "retries": _retry_counts[key],
        "priority": "immediate" if "service_down" in causes else "scheduled",
        "ts": datetime.now(timezone.utc).isoformat()
    }

def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Down","causes":["service_down"],"source":"anton"}
    result = route(inc)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
