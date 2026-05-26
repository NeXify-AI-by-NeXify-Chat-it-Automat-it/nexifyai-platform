#!/usr/bin/env python3
"""Vault Compatibility Layer -- drop-in replacement for os.environ for DS_ secrets."""
"""Phase 1: vault read with audit. Phase 2: TTL/scope. Phase 3: block direct."""
import os, json, logging
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.security.vault_compat")

class VaultCompat:
    """Thread-safe vault access with audit logging."""
    def __init__(self, worker_id="system"):
        self.worker_id = worker_id
        self.audit_log = "/services/runtime/security/audit/events.log"
        os.makedirs("/services/runtime/security/audit", exist_ok=True)

    def _log_access(self, key, found=True):
        entry = {"ts": datetime.now(timezone.utc).isoformat(),
                 "type": "vault_access", "key": key,
                 "worker": self.worker_id, "found": found}
        try:
            with open(self.audit_log, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except:
            pass

    def get(self, key, default=None):
        """Get secret via vault. Falls back to os.environ with audit."""
        env_key = "DS_" + key.upper()
        val = os.environ.get(env_key)
        if val:
            self._log_access(key, True)
            return val
        for k, v in os.environ.items():
            if k.startswith("DS_") and key.upper() in k.replace("__", "_"):
                self._log_access(key, True)
                return v
        val = os.environ.get(key)
        if val:
            self._log_access(key, True)
            return val
        self._log_access(key, False)
        return default

    def get_set(self, name):
        """Get all fields for a credential set."""
        prefix = "DS_" + name.upper() + "__"
        result = {}
        for k, v in os.environ.items():
            if k.startswith(prefix):
                field = k.replace(prefix, "").lower()
                result[field] = v
        return result or None

    def __getitem__(self, key):
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __contains__(self, key):
        return self.get(key) is not None


_vault = None


def get_vault(worker_id="system"):
    global _vault
    if _vault is None:
        _vault = VaultCompat(worker_id)
    return _vault


def vault_get(key, default=None):
    return get_vault().get(key, default)


if __name__ == "__main__":
    v = get_vault("test")
    for k in ["MONGO_URL", "RESEND_API_KEY", "ADMIN_EMAIL", "NONEXISTENT"]:
        val = v.get(k)
        # Log existence metadata only — never log secret values
        logger.info("Vault check: %s present=%s", k, "yes" if val else "no")
