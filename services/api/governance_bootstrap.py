
"""Autonomous Runtime Governance Bootstrap Layer.

7-stage startup lifecycle. Runs before ANY runtime component is operational.
Blocks workflow execution until governance passes or degrades gracefully.
"""

import os, json, logging, subprocess, time, socket, sys
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("nexifyai.governance.bootstrap")

# ====== STAGE 0: Configuration ======

GOVERNANCE_STATE_KEY = "nexifyai:governance:state"
GOVERNANCE_REPORT_KEY = "nexifyai:governance:report"
VAULT_DIR = "/root/.anton/data_vault"
GOVERNANCE_BLOCK_WORKFLOWS = True

REQUIRED_ENV = {
    "MINIMAL": ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"],
    "FULL": ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "REDIS_HOST", "REDIS_PORT", "INTERNAL_AUTH"],
}

SYSTEMD_WORKER_MAP = {
    "main": "nexifyai-worker-main",
    "analysis": "nexifyai-worker-analysis",
    "engineering": "nexifyai-worker-engineering",
}

REQUIRED_PORTS = {"temporal-server": 7233, "redis": 6379, "qdrant": 6333}
REQUIRED_PATHS = [
    "/opt/nexifyai-website-sicherheitskopie/backend",
    "/opt/nexifyai-website-sicherheitskopie/backend/venv/bin/python",
    "/opt/nexifyai-website-sicherheitskopie/backend/temporal/activities.py",
    "/opt/nexifyai-website-sicherheitskopie/backend/dlq.py",
    "/opt/nexifyai-website-sicherheitskopie/backend/circuit_breaker.py",
    "/opt/nexifyai-website-sicherheitskopie/backend/governance.py",
]

# ====== STAGE 1: Runtime Discovery ======

def _check_port(host, port, timeout=3):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        r = s.connect_ex((host, port))
        s.close()
        return r == 0
    except:
        return False

def _read_vault():
    result = {}
    if not os.path.isdir(VAULT_DIR):
        return result
    for fname in sorted(os.listdir(VAULT_DIR)):
        fpath = os.path.join(VAULT_DIR, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                fields = data.get("fields", {})
                engine = data.get("engine", "")
                name = data.get("name", "")
                slug = "%s_%s" % (engine, name)
                for k, v in fields.items():
                    env_key = "DS_%s__%s" % (slug.upper(), k.upper())
                    if v and not v.startswith("[DS_"):
                        result[env_key] = v
            except:
                pass
    return result

def _resolve_env(name):
    val = os.environ.get(name, "")
    if val:
        return val
    vault = _read_vault()
    alt_map = {
        "CAMBRO_API_KEY": "DS_CAMBO_158B458E__API_KEY",
        "CAMBRO_BASE_URL": "DS_CAMBO_158B458E__BASE_URL",
        "SUPABASE_URL": "DS_SUPABASE_1E93118D__PROJECT_URL",
        "SUPABASE_SERVICE_KEY": "DS_SUPABASE_1E93118D__SECRET_KEY",
    }
    if name in alt_map and alt_map[name] in vault:
        return vault[alt_map[name]]
    if name in alt_map:
        return os.environ.get(alt_map[name], "")
    defaults = {"REDIS_HOST": "localhost", "REDIS_PORT": "6379", "INTERNAL_AUTH": "governance-internal-token"}
    return defaults.get(name, "")

def runtime_discovery():
    """Stage 1: Discover all runtime components."""
    discovery = {"services": {}, "workers": {}, "files": {}, "docker_containers": [], "ports": {}}

    for name, port in REQUIRED_PORTS.items():
        discovery["ports"][name] = {"port": port, "reachable": _check_port("localhost", port)}

    for role, unit in SYSTEMD_WORKER_MAP.items():
        r = subprocess.run("systemctl is-active %s" % unit, shell=True, capture_output=True, text=True, timeout=5)
        status = r.stdout.strip()
        discovery["workers"][role] = {
            "unit_name": unit,
            "exists": os.path.exists("/etc/systemd/system/%s.service" % unit),
            "status": status,
            "alive": status == "active",
        }

    for p in REQUIRED_PATHS:
        discovery["files"][os.path.basename(p)] = {"path": p, "exists": os.path.exists(p)}

    r = subprocess.run("docker ps --format '{{.Names}}' 2>/dev/null", shell=True, capture_output=True, text=True, timeout=10)
    discovery["docker_containers"] = [l.strip() for l in r.stdout.split(chr(10)) if l.strip()]

    return discovery

# ====== STAGE 2: Configuration Validation ======

def config_validation():
    """Stage 2: Validate all configuration."""
    validation = {"env": {}, "env_summary": {"total": 0, "present": 0, "missing": []}, "secrets_valid": False}

    for var in REQUIRED_ENV["FULL"]:
        val = _resolve_env(var)
        ok = bool(val)
        validation["env"][var] = {"present": ok, "length": len(val)}
        if ok:
            validation["env_summary"]["present"] += 1
        else:
            validation["env_summary"]["missing"].append(var)
        validation["env_summary"]["total"] += 1

    vault = _read_vault()
    validation["secrets_valid"] = len(vault) > 0
    validation["vault_entries"] = len(vault)

    return validation

# ====== STAGE 3: Capability Verification ======

def _try_http(url, timeout=5):
    try:
        import httpx
        r = httpx.get(url, timeout=timeout)
        return r.status_code < 500
    except:
        return False

def capability_verification():
    """Stage 3: Verify all capabilities are operational."""
    capabilities = {
        "temporal_web_ui": _check_port("localhost", 8234),
        "prometheus_scrapable": _try_http("http://localhost:8001/metrics"),
        "grafana_accessible": _try_http("http://localhost:3000"),
        "dlq_module_importable": False,
        "circuit_breaker_module_importable": False,
        "governance_module_importable": False,
    }
    try:
        import importlib
        importlib.import_module("dlq")
        capabilities["dlq_module_importable"] = True
    except:
        pass
    try:
        import importlib
        importlib.import_module("circuit_breaker")
        capabilities["circuit_breaker_module_importable"] = True
    except:
        pass
    try:
        import importlib
        importlib.import_module("governance")
        capabilities["governance_module_importable"] = True
    except:
        pass
    return capabilities

# ====== STAGE 4: Drift Detection ======

def _check_worker_env_drift(role):
    unit = SYSTEMD_WORKER_MAP.get(role)
    if not unit:
        return []
    unit_path = "/etc/systemd/system/%s.service" % unit
    override_dir = "/etc/systemd/system/%s.service.d" % unit
    issues = []
    if not os.path.exists(unit_path):
        issues.append({"type": "missing_unit", "detail": "%s.service does not exist" % unit})
        return issues
    has_env = []
    with open(unit_path) as f:
        for line in f:
            if line.strip().startswith("Environment="):
                has_env.append(line.strip()[12:].split("=")[0])
    if os.path.exists(override_dir):
        for fname in sorted(os.listdir(override_dir)):
            with open(os.path.join(override_dir, fname)) as f:
                for line in f:
                    if line.strip().startswith("Environment="):
                        has_env.append(line.strip()[12:].split("=")[0])
    required = ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing = [v for v in required if v not in has_env]
    for v in missing:
        issues.append({"type": "missing_env", "detail": "%s missing env: %s" % (unit, v)})
    return issues

def drift_detection():
    """Stage 4: Detect runtime drift."""
    drift = {"issues": [], "worker_drift": {}, "config_drift": []}
    for role in SYSTEMD_WORKER_MAP:
        issues = _check_worker_env_drift(role)
        if issues:
            drift["worker_drift"][role] = issues
            drift["issues"].extend(issues)
    gp = "/opt/nexifyai-website-sicherheitskopie/backend/governance.py"
    if os.path.exists(gp):
        drift["governance_last_modified"] = datetime.fromtimestamp(os.path.getmtime(gp)).isoformat()
    return drift

# ====== STAGE 5: Auto-Repair ======

def auto_repair(discovery, validation, drift):
    """Stage 5: Attempt autonomous repair for all detected issues."""
    repairs = []
    for role, issues in drift.get("worker_drift", {}).items():
        unit = SYSTEMD_WORKER_MAP.get(role)
        if not unit:
            continue
        missing = [i["detail"] for i in issues if i["type"] == "missing_env"]
        if missing:
            required = ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "REDIS_HOST", "REDIS_PORT", "INTERNAL_AUTH"]
            env_lines = ["Environment=%s=%s" % (var, _resolve_env(var)) for var in required if _resolve_env(var)]
            if env_lines:
                override_dir = "/etc/systemd/system/%s.service.d" % unit
                os.makedirs(override_dir, exist_ok=True)
                with open("%s/autorepair-env.conf" % override_dir, "w") as f:
                    f.write("[Service]" + chr(10))
                    for line in env_lines:
                        f.write(line + chr(10))
                subprocess.run("systemctl daemon-reload", shell=True, timeout=10)
                subprocess.run("systemctl restart %s" % unit, shell=True, timeout=30)
                time.sleep(3)
                r = subprocess.run("systemctl is-active %s" % unit, shell=True, capture_output=True, text=True, timeout=5)
                status = r.stdout.strip()
                repairs.append({"target": "worker:%s" % role, "action": "env_override_restart", "detail": "Wrote %d env vars" % len(env_lines), "result": "worker now %s" % status, "success": status == "active"})
    for role, info in discovery.get("workers", {}).items():
        if not info.get("alive", False) and info.get("exists", False):
            subprocess.run("systemctl restart %s" % info["unit_name"], shell=True, timeout=30)
            time.sleep(2)
            r = subprocess.run("systemctl is-active %s" % info["unit_name"], shell=True, capture_output=True, text=True, timeout=5)
            status = r.stdout.strip()
            repairs.append({"target": "worker:%s" % role, "action": "restart", "detail": "Was %s" % info.get("status", "unknown"), "result": "now %s" % status, "success": status == "active"})
    return repairs

# ====== STAGE 6: Governance Report ======

def persist_report(report):
    """Persist governance report to Qdrant."""
    try:
        import httpx as _h
        import json as _j
        info = _h.get("http://localhost:6333/collections/nexifyai_brain", timeout=5)
        dims = 4096
        if info.status_code == 200:
            dims = info.json().get("result", {}).get("config", {}).get("params", {}).get("vectors", {}).get("size", 4096)
        pid = int(time.time() * 10000)
        point = {
            "id": pid,
            "vector": [0.0] * dims,
            "payload": {
                "category": "governance_report",
                "title": "Governance: PASSED" if report.get("governance_passed") else "Governance: BLOCKED",
                "content": _j.dumps(report, default=str)[:50000],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        r = _h.put("http://localhost:6333/collections/nexifyai_brain/points", json={"points": [point]}, timeout=10)
        report["persisted_to_brain"] = r.status_code in [200, 201]
        if not r.status_code in [200, 201]:
            report["persist_debug"] = "status=%d dims=%d pid=%d text=%s" % (r.status_code, dims, pid, r.text[:100])
    except Exception as e:
        report["persisted_to_brain"] = False
        report["persist_error"] = str(e)[:200]
    return report

# ====== STAGE 7: Workflow Gate ======

class GovernanceGate:
    """Blocks workflow execution if governance has not passed."""
    _instance = None
    _passed = False
    _last_report = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_result(cls, passed, report):
        cls._passed = passed
        cls._last_report = report

    @classmethod
    def can_execute(cls):
        return cls._passed

    @classmethod
    def get_status(cls):
        return {"gate_open": cls._passed, "last_report": cls._last_report}

# ====== MAIN BOOTSTRAP ======

def run_bootstrap(repair=True, block_workflows=True):
    """Execute the full 7-stage governance bootstrap lifecycle."""
    start = time.time()
    stages = []

    logger.info("=== AUTONOMOUS RUNTIME GOVERNANCE BOOTSTRAP ===")

    # Stage 1
    t1 = time.time()
    discovery = runtime_discovery()
    stages.append({"stage": 1, "name": "Runtime Discovery", "duration_s": round(time.time() - t1, 2), "status": "complete",
        "data": {"services_up": sum(1 for s in discovery["ports"].values() if s["reachable"]), "services_total": len(discovery["ports"]),
                 "workers_alive": sum(1 for w in discovery["workers"].values() if w["alive"]), "workers_total": len(discovery["workers"]),
                 "docker_count": len(discovery["docker_containers"])}})
    logger.info("  [1/7] Runtime Discovery: %d/%d services, %d/%d workers" % (
        stages[-1]["data"]["services_up"], stages[-1]["data"]["services_total"],
        stages[-1]["data"]["workers_alive"], stages[-1]["data"]["workers_total"]))

    # Stage 2
    t1 = time.time()
    validation = config_validation()
    stages.append({"stage": 2, "name": "Configuration Validation", "duration_s": round(time.time() - t1, 2), "status": "complete",
        "data": {"env_present": validation["env_summary"]["present"], "env_total": validation["env_summary"]["total"],
                 "env_missing": validation["env_summary"]["missing"], "vault_entries": validation["vault_entries"]}})
    logger.info("  [2/7] Config Validation: %d/%d env vars" % (stages[-1]["data"]["env_present"], stages[-1]["data"]["env_total"]))

    # Stage 3
    t1 = time.time()
    capabilities = capability_verification()
    stages.append({"stage": 3, "name": "Capability Verification", "duration_s": round(time.time() - t1, 2), "status": "complete", "data": capabilities})
    cap_ok = sum(1 for v in capabilities.values() if v)
    logger.info("  [3/7] Capability Verification: %d/%d capabilities ok" % (cap_ok, len(capabilities)))

    # Stage 4
    t1 = time.time()
    drift = drift_detection()
    stages.append({"stage": 4, "name": "Drift Detection", "duration_s": round(time.time() - t1, 2), "status": "complete",
        "data": {"total_issues": len(drift["issues"]),
                 "worker_drifts": {k: [i["type"] for i in v] for k, v in drift.get("worker_drift", {}).items() if v}}})
    logger.info("  [4/7] Drift Detection: %d issues" % len(drift["issues"]))

    # Stage 5
    t1 = time.time()
    repairs = auto_repair(discovery, validation, drift) if repair else []
    stages.append({"stage": 5, "name": "Auto-Repair", "duration_s": round(time.time() - t1, 2), "status": "complete",
        "data": {"repairs_attempted": len(repairs), "repairs_succeeded": sum(1 for r in repairs if r.get("success")), "repairs": repairs}})
    logger.info("  [5/7] Auto-Repair: %d/%d succeeded" % (stages[-1]["data"]["repairs_succeeded"], stages[-1]["data"]["repairs_attempted"]))

    # Stage 6: Build and persist report
    t1 = time.time()
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_duration_s": round(time.time() - start, 2),
        "stages": stages,
        "governance_passed": False,
        "block_workflows": block_workflows,
    }
    env_ok = validation["env_summary"]["present"] >= len(REQUIRED_ENV["MINIMAL"])
    services_ok = all(s["reachable"] for s in discovery["ports"].values())
    report["governance_passed"] = env_ok and services_ok
    report = persist_report(report)
    stages.append({"stage": 6, "name": "Governance Report", "duration_s": round(time.time() - t1, 2), "status": "complete",
        "data": {"persisted": report.get("persisted_to_brain", False)}})
    logger.info("  [6/7] Governance Report: persisted=%s" % report.get("persisted_to_brain", False))

    # Stage 7
    GovernanceGate.set_result(report["governance_passed"], report)
    stages.append({"stage": 7, "name": "Workflow Gate", "duration_s": 0, "status": "complete",
        "data": {"gate_open": report["governance_passed"],
                 "reason": "All checks passed" if report["governance_passed"] else "Env: %d/%d" % (validation["env_summary"]["present"], validation["env_summary"]["total"])}})

    report["total_duration_s"] = round(time.time() - start, 2)
    verdict = "PASSED OK" if report["governance_passed"] else "BLOCKED"
    logger.info("=== GOVERNANCE BOOTSTRAP: %s in %.2fs ===" % (verdict, report.get("total_duration_s", 0)))
    return report

def is_governance_passed():
    return GovernanceGate.can_execute()

def get_governance_status():
    return GovernanceGate.get_status()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    repair = "--no-repair" not in sys.argv
    _report = run_bootstrap(repair=repair)
    print(json.dumps(_report, indent=2, default=str))
    sys.exit(0 if _report["governance_passed"] else 1)
