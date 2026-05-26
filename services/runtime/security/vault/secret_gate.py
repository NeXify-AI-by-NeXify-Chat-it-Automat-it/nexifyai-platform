#!/usr/bin/env python3
"""Secret Health Gate — blocks runtime start if secret state is invalid."""
import os, sys, json, logging
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.security.secret_gate")

def check_secret_health():
    """Check vault health and required secret availability."""
    sys.path.insert(0, "/services/runtime/security/vault")
    from vault_compat import get_vault
    v = get_vault("healthcheck")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "healthy",
        "vault_accessible": True,
    }
    try:
        with open("/services/runtime/security/audit/events.log", "a") as f:
            f.write("")
        report["audit_writable"] = True
    except:
        report["audit_writable"] = False
        report["status"] = "degraded"
    ds_count = sum(1 for k in os.environ if k.startswith("DS_"))
    report["env_credentials"] = ds_count
    if ds_count != 100:
        report["status"] = "degraded"
    reg_path = "/services/runtime/security/vault/registry.json"
    if os.path.exists(reg_path):
        with open(reg_path) as f:
            reg = json.load(f)
        report["registry_entries"] = len(reg)
        expired = [n for n,m in reg.items() if m.get("status")=="revoked"]
        if expired:
            report["revoked_secrets"] = expired[:5]
            report["status"] = "degraded"
    return report

def main():
    report = check_secret_health()
    # Report metadata only — no secret values are exposed
    safe_report = {k: v for k, v in report.items() if k not in ("env_credentials",)}
    logger.info("Secret health check: %s", json.dumps(safe_report))
    if report["status"] == "healthy":
        logger.info("SECRET HEALTH: PASS - Runtime may start")
        return 0
    else:
        msg = "SECURITY GATE BLOCKED: secret state is " + report["status"]
        logger.error(msg)
        print(msg, file=sys.stderr)  # gitleaks:allow - status message, not secret value
        return 1

if __name__ == "__main__":
    sys.exit(main())
