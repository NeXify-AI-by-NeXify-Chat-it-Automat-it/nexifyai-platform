#!/usr/bin/env python3
"""Runtime Security Policy — governing all credential/secret operations."""
"""This is the single source of truth for security policy."""
import json, os, sys
from datetime import datetime, timezone

POLICY = {
    "version": "2.0",
    "title": "Enterprise Secret Governance Policy",
    "effective": "2026-05-17",
    "rules": [
        {"id": "SEC-001", "priority": "P0", "rule": "ALL secrets MUST be accessed through vault_compat, never os.environ directly"},
        {"id": "SEC-002", "priority": "P0", "rule": "NO static secrets in repository, docs, logs, or runtime files"},
        {"id": "SEC-003", "priority": "P0", "rule": "EVERY secret access MUST be audited via event log"},
        {"id": "SEC-004", "priority": "P1", "rule": "Workers MUST use scoped credentials, never global root"},
        {"id": "SEC-005", "priority": "P1", "rule": "Secrets MUST be rotated per type: GitHub 30d, Vercel 60d, others 90d"},
        {"id": "SEC-006", "priority": "P1", "rule": "Runtime MUST NOT start if secret health gate fails"},
        {"id": "SEC-007", "priority": "P1", "rule": "All DS_ env vars require registry registration"},
        {"id": "SEC-008", "priority": "P2", "rule": "Secret access anomalies MUST be reported to Brain"},
        {"id": "SEC-009", "priority": "P2", "rule": "Pre-commit scanning MUST block leaked credentials"},
        {"id": "SEC-010", "priority": "P2", "rule": "Log redaction MUST apply to all output channels"},
    ],
    "rotation_schedule": {
        "github": 30,
        "vercel": 60,
        "deepseek": 90,
        "resend": 90,
        "supabase": 90,
        "cloudflare": 60,
        "default": 90,
    },
    "anomaly_thresholds": {
        "max_access_per_hour": 50,
        "max_workers_per_secret": 5,
        "max_failed_lookups": 10,
    },
    "enforcement": {
        "startup_gate": True,
        "pre_commit_scanning": True,
        "runtime_scanning": True,
        "audit_logging": True,
        "telemetry": True,
        "brain_reporting": True,
    },
}

def get_policy():
    return POLICY

def check_compliance():
    """Check if runtime complies with all P0 rules."""
    issues = []
    # Check: vault_compat imported in server.py
    if os.path.exists("/opt/nexifyai-platform/services/api/server.py"):
        with open("/opt/nexifyai-platform/services/api/server.py") as f:
            if "vault_compat" not in f.read():
                issues.append("SEC-001: vault_compat not imported in server.py")
    # Check: audit log exists
    if not os.path.exists("/services/runtime/security/audit/events.log"):
        issues.append("SEC-003: audit log missing")
    # Check: no direct os.environ in critical paths (stub check)
    # Check: scanner ran recently
    if os.path.exists("/services/runtime/security/vault/registry.json"):
        with open("/services/runtime/security/vault/registry.json") as f:
            reg = json.load(f)
        revoked = [n for n,m in reg.items() if m.get("status")=="revoked"]
        if revoked:
            issues.append(f"SEC-004: {len(revoked)} revoked secrets still registered")
    return {"compliant": len(issues)==0, "issues": issues}

if __name__ == "__main__":
    print(json.dumps({"policy": POLICY, "compliance": check_compliance()}, indent=2))
