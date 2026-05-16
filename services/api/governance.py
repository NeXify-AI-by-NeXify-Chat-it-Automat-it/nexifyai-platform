"""Runtime Governance — autonomous worker validation, drift detection, and recovery.
Every backend startup triggers full governance validation.
"""

import os, json, logging, subprocess, time, socket
from datetime import datetime, timezone


_VAULT_DIR = "/root/.anton/data_vault"
_CACHED_VAULT = None

def _read_vault():
    global _CACHED_VAULT
    if _CACHED_VAULT is not None:
        return _CACHED_VAULT
    _CACHED_VAULT = {}
    if os.path.isdir(_VAULT_DIR):
        for fname in sorted(os.listdir(_VAULT_DIR)):
            fpath = os.path.join(_VAULT_DIR, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath) as f:
                        data = json.load(f)
                    fields = data.get("fields", {})
                    engine = data.get("engine", "")
                    name = data.get("name", "")
                    slug = f"{engine}_{name}"
                    if fields:
                        for k, v in fields.items():
                            env_key = f"DS_{slug}__{k.upper()}"
                            if v and not v.startswith("[DS_"):
                                _CACHED_VAULT[env_key] = v
                            elif v:
                                _CACHED_VAULT[env_key] = ""
                except:
                    pass
    return _CACHED_VAULT


def _resolve_env_var(name):
    """Try env, then vault, then default."""
    val = os.environ.get(name, "")
    if val:
        return val
    
    vault = _read_vault()
    if name in vault and vault[name]:
        return vault[name]
    
    # Map common names
    # Defaults for standard infra vars
    defaults = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "INTERNAL_AUTH": "governance-internal-token",
    }
    if name in defaults:
        return defaults[name]
    
    mappings = {
        "CAMBRO_API_KEY": ["DS_CAMBO_158B458E__API_KEY"],
        "CAMBRO_BASE_URL": ["DS_CAMBO_158B458E__BASE_URL"],
        "SUPABASE_URL": ["DS_SUPABASE_1E93118D__PROJECT_URL"],
        "SUPABASE_SERVICE_KEY": ["DS_SUPABASE_1E93118D__SECRET_KEY"],
    }
    for alt in mappings.get(name, []):
        val = os.environ.get(alt, "")
        if val:
            return val
        if alt in vault and vault[alt]:
            return vault[alt]
    
    return ""

logger = logging.getLogger("nexifyai.governance")

WORKER_ENV_REQUIREMENTS = {
    "main": {
        "required": ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "REDIS_HOST", "REDIS_PORT", "INTERNAL_AUTH"],
        "optional": ["OPENROUTER_API_KEY", "OPENROUTER_BASE_URL"],
        "description": "Main worker — orchestrator and task routing",
    },
    "analysis": {
        "required": ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"],
        "optional": [],
        "description": "Analysis worker — research and data processing",
    },
    "engineering": {
        "required": ["CAMBRO_API_KEY", "CAMBRO_BASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"],
        "optional": [],
        "description": "Engineering worker — code and deploy pipelines",
    },
}

SYSTEMD_UNITS = {
    "main": "nexifyai-worker-main",
    "analysis": "nexifyai-worker-analysis",
    "engineering": "nexifyai-worker-engineering",
}

REQUIRED_PATHS = {
    "backend": "/opt/nexifyai-website-sicherheitskopie/backend",
    "venv": "/opt/nexifyai-website-sicherheitskopie/backend/venv/bin/python",
    "activities": "/opt/nexifyai-website-sicherheitskopie/backend/temporal/activities.py",
}

REQUIRED_SERVICES = {
    "temporal": {"host": "localhost", "port": 7233},
    "redis": {"host": "localhost", "port": 6379},
    "qdrant": {"host": "localhost", "port": 6333},
}


def validate_env(worker_role, env_override=None):
    reqs = WORKER_ENV_REQUIREMENTS.get(worker_role, {})
    required = reqs.get("required", [])
    env = {**os.environ, **(env_override or {})}
    missing = []
    present = []
    for var in required:
        val = env.get(var, "") or _resolve_env_var(var)
        if val:
            present.append(var)
        else:
            missing.append(var)
    return {
        "worker": worker_role,
        "present": present,
        "missing": missing,
        "total_required": len(required),
        "total_present": len(present),
        "valid": len(missing) == 0,
    }


def validate_systemd_units():
    results = {}
    for role, unit_name in SYSTEMD_UNITS.items():
        unit_path = "/etc/systemd/system/" + unit_name + ".service"
        override_dir = "/etc/systemd/system/" + unit_name + ".service.d"
        unit_exists = os.path.exists(unit_path)
        has_overrides = os.path.exists(override_dir) and len(os.listdir(override_dir)) > 0
        exec_start = ""
        if unit_exists:
            with open(unit_path) as f:
                for line in f:
                    if line.strip().startswith("ExecStart="):
                        exec_start = line.strip()[10:]
                        break
        try:
            r = subprocess.run("systemctl is-active " + unit_name, shell=True, capture_output=True, text=True, timeout=5)
            status = r.stdout.strip()
        except:
            status = "unknown"
        results[role] = {
            "unit_name": unit_name,
            "exists": unit_exists,
            "has_overrides": has_overrides,
            "exec_start": exec_start[:120] if exec_start else "",
            "status": status,
            "healthy": unit_exists and status == "active",
        }
    return results


def validate_service_endpoints():
    results = {}
    for name, info in REQUIRED_SERVICES.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex((info["host"], info["port"]))
            s.close()
            reachable = result == 0
        except:
            reachable = False
        results[name] = {"host": info["host"], "port": info["port"], "reachable": reachable}
    return results


def validate_file_integrity():
    results = {}
    for name, p in REQUIRED_PATHS.items():
        results[name] = {"path": p, "exists": os.path.exists(p)}
    return results


def generate_missing_env_report():
    reports = []
    for role in WORKER_ENV_REQUIREMENTS:
        env_status = validate_env(role)
        if not env_status["valid"]:
            missing = ", ".join(env_status["missing"])
            reports.append({
                "worker": role,
                "issue": "Missing env vars: " + missing,
                "severity": "critical",
                "action": "Add Environment= to /etc/systemd/system/" + SYSTEMD_UNITS[role] + ".service.d/override.conf",
            })
    units = validate_systemd_units()
    for role, info in units.items():
        if not info["healthy"]:
            reports.append({
                "worker": role,
                "issue": "Unit " + info["unit_name"] + " is " + info["status"],
                "severity": "critical" if info["status"] == "failed" else "warning",
                "action": "systemctl restart " + info["unit_name"],
            })
    return reports


def auto_repair_worker(worker_role):
    result = {"role": worker_role, "actions_taken": [], "success": False}
    unit_name = SYSTEMD_UNITS.get(worker_role)
    if not unit_name:
        return result
    if not os.path.exists("/etc/systemd/system/" + unit_name + ".service"):
        result["error"] = "Unit not found"
        return result
    required_vars = WORKER_ENV_REQUIREMENTS.get(worker_role, {}).get("required", [])
    env_vars = []
    for var in required_vars:
        value = os.environ.get(var, "") or _resolve_env_var(var)
        if value:
            env_vars.append("Environment=" + var + "=" + value)
    if not env_vars:
        result["error"] = "No env vars available in current process"
        return result
    override_dir = "/etc/systemd/system/" + unit_name + ".service.d"
    os.makedirs(override_dir, exist_ok=True)
    nl = chr(10)
    override_content = "[Service]" + nl + nl.join(env_vars) + nl
    override_path = override_dir + "/autorepair-env.conf"
    with open(override_path, "w") as f:
        f.write(override_content)
    result["actions_taken"].append("Wrote " + override_path + " with " + str(len(env_vars)) + " env vars")
    subprocess.run("systemctl daemon-reload", shell=True, timeout=10)
    subprocess.run("systemctl restart " + unit_name, shell=True, timeout=30)
    time.sleep(3)
    try:
        r = subprocess.run("systemctl is-active " + unit_name, shell=True, capture_output=True, text=True, timeout=5)
        status = r.stdout.strip()
        result["new_status"] = status
        result["success"] = status == "active"
        result["actions_taken"].append("Restart -> " + status)
    except Exception as e:
        result["error"] = "Verification failed: " + str(e)
    return result


def run_full_governance_check(repair=False):
    logger.info("Running full Runtime Governance check...")
    env_results = {}
    for role in WORKER_ENV_REQUIREMENTS:
        env_results[role] = validate_env(role)
    unit_results = validate_systemd_units()
    service_results = validate_service_endpoints()
    file_results = validate_file_integrity()
    issues = generate_missing_env_report()
    repairs = []
    if repair:
        for issue in issues:
            if issue["severity"] == "critical" and "worker" in issue:
                repair_result = auto_repair_worker(issue["worker"])
                repairs.append(repair_result)
                env_results[issue["worker"]] = validate_env(issue["worker"])
    overall_healthy = (
        all(e["valid"] for e in env_results.values())
        and all(u.get("healthy", False) for u in unit_results.values())
        and all(s["reachable"] for s in service_results.values())
        and all(f["exists"] for f in file_results.values())
    )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_healthy": overall_healthy,
        "workers": env_results,
        "systemd_units": unit_results,
        "services": service_results,
        "files": file_results,
        "issues": issues,
        "repairs": repairs,
        "repair_attempted": repair,
    }


if __name__ == "__main__":
    import sys
    repair = "--repair" in sys.argv
    result = run_full_governance_check(repair=repair)
    print(json.dumps(result, indent=2, default=str))
    if result["overall_healthy"]:
        print(chr(10) + "RUNTIME GOVERNANCE: HEALTHY")
    else:
        print(chr(10) + "RUNTIME GOVERNANCE: " + str(len(result["issues"])) + " issues")
        for issue in result["issues"]:
            print("  [" + issue.get("severity", "?") + "] " + issue.get("worker", "?") + ": " + issue.get("issue", "?"))
        sys.exit(1)
