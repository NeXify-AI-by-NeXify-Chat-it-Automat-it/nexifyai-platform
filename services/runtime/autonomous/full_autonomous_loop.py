#!/usr/bin/env python3
"""full_autonomous_loop.py — Continuous autonomous enterprise execution loop.
Runs ALL enterprise systems in sequence: observe -> plan -> execute -> validate -> learn.
Designed as systemd oneshot that gets triggered every 5 minutes.
"""
import json, logging, os, requests, subprocess, sys, time, uuid
from datetime import datetime, timezone
log = logging.getLogger("auto-loop")

REPO = "/opt/nexify/repos/nexifyai-platform"
ENTERPRISE_CYCLE = [
    {"name": "observe", "path": f"{REPO}/services/runtime/autonomous/autonomous_orchestration_kernel.py", "critical": True},
    {"name": "heartbeat", "path": f"{REPO}/services/runtime/rhythm/organization_heartbeat.py", "critical": False},
    {"name": "cycle_detect", "path": f"{REPO}/services/runtime/rhythm/organizational_cycle_controller.py", "critical": False},
    {"name": "maturity", "path": f"{REPO}/services/runtime/rhythm/runtime_maturity_evaluator.py", "critical": False},
    {"name": "planner", "path": f"{REPO}/services/runtime/planner/autonomous_program_manager.py", "critical": True},
    {"name": "incidents", "path": f"{REPO}/services/runtime/incidents/incident_manager.py", "critical": True},
    {"name": "reconciliation", "path": f"{REPO}/services/runtime/reconciliation/state_reconciler.py", "critical": True},
    {"name": "watchdog", "path": f"{REPO}/services/runtime/watchdog/runtime_watchdog.py", "critical": True},
    {"name": "convergence", "path": f"{REPO}/services/runtime/convergence/post_deploy_convergence.py", "critical": False},
    {"name": "learning", "path": f"{REPO}/services/runtime/learning/organizational_learning_engine.py", "critical": False},
    {"name": "issues", "path": f"{REPO}/services/runtime/github_governance/issue_autogenerator.py", "critical": False},
]

def run_enterprise_cycle(full=False):
    log.info("=== ENTERPRISE CYCLE START ===")
    results = {}
    for module in ENTERPRISE_CYCLE:
        path = module["path"]
        name = module["name"]
        if not os.path.exists(path):
            results[name] = {"status": "not_found", "path": path}
            if module["critical"]:
                log.warning(f"CRITICAL: {name} not found at {path}")
            continue
        try:
            r = subprocess.run(["python3", path], capture_output=True, text=True, timeout=30)
            status = "ok" if r.returncode == 0 else "error"
            results[name] = {"status": status, "rc": r.returncode}
            log.info(f"  {name}: {status} (rc={r.returncode})")
        except subprocess.TimeoutExpired:
            results[name] = {"status": "timeout"}
            log.warning(f"  {name}: TIMEOUT")
        except Exception as e:
            results[name] = {"status": "exception", "error": str(e)[:50]}
            log.error(f"  {name}: {e}")
    oks = sum(1 for v in results.values() if v.get("status") == "ok")
    fails = len(results) - oks
    log.info(f"=== ENTERPRISE CYCLE COMPLETE: {oks}/{len(results)} OK, {fails} FAILS ===")
    return {"results": results, "ok": oks, "total": len(results), "ts": datetime.now(timezone.utc).isoformat()}

def main():
    full = "--full" in sys.argv
    result = run_enterprise_cycle(full)
    print(json.dumps(result, indent=2))
    return 0  # always exit 0 for systemd

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [auto-loop] %(name)s: %(levelname)s: %(message)s")
    sys.exit(main())
