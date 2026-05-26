#!/usr/bin/env python3
"""Revocation Engine -- immediate credential revocation across all layers."""
import os, json, sys, logging
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.security.revocation")

class RevocationEngine:
    def __init__(self):
        self.revocation_log = "/services/runtime/security/audit/revocation_log.json"

    def revoke_credential(self, secret_name, reason="manual", operator="system"):
        ts = datetime.now(timezone.utc).isoformat()
        layers_affected = []
        reg_path = "/services/runtime/security/vault/registry.json"
        if os.path.exists(reg_path):
            with open(reg_path) as f: reg = json.load(f)
            if secret_name in reg:
                reg[secret_name]["status"] = "revoked"
                reg[secret_name]["revoked_at"] = ts
                reg[secret_name]["revoke_reason"] = reason
                with open(reg_path, "w") as f: json.dump(reg, f, indent=2)
                layers_affected.append("registry")
        sys.path.insert(0, "/services/runtime/security/rotation")
        from lease_manager import get_lease_manager
        lm = get_lease_manager()
        count = sum(1 for l in lm.leases.values() if hasattr(l, "secret_name") and l.secret_name == secret_name and not l.revoked)
        lm.revoke_all_for_worker(secret_name)
        if count: layers_affected.append("leases(" + str(count) + ")")
        entry = {"ts": ts, "action": "revoke", "secret": secret_name, "reason": reason, "operator": operator, "layers": layers_affected}
        self._log(entry)
        return entry

    def revoke_all_expired(self):
        results = []
        reg_path = "/services/runtime/security/vault/registry.json"
        if os.path.exists(reg_path):
            with open(reg_path) as f: reg = json.load(f)
            now = datetime.now(timezone.utc)
            for name, meta in reg.items():
                exp = meta.get("expires_at")
                if exp:
                    try:
                        if datetime.fromisoformat(exp) < now:
                            results.append(self.revoke_credential(name, "expired", "auto"))
                    except: pass
        return results

    def _log(self, entry):
        os.makedirs(os.path.dirname(self.revocation_log), exist_ok=True)
        history = []
        if os.path.exists(self.revocation_log):
            with open(self.revocation_log) as f: history = json.load(f)
        history.append(entry)
        if len(history) > 1000: history = history[-1000:]
        with open(self.revocation_log, "w") as f: json.dump(history, f, indent=2)
        with open("/services/runtime/security/audit/events.log", "a") as f: f.write(json.dumps(entry) + "\n")  # gitleaks:allow - metadata, secret names only

    def status(self):
        if os.path.exists(self.revocation_log):
            with open(self.revocation_log) as f: log = json.load(f)
            return {"total_revocations": len(log), "last": log[-1] if log else None}
        return {"total_revocations": 0}

if __name__ == "__main__":
    eng = RevocationEngine()
    result = eng.revoke_credential("test_secret", "test", "verifier")
    logger.info("Revocation test result: %s", json.dumps(result))
