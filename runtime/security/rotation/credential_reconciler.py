#!/usr/bin/env python3
"""Credential Reconciler -- sync env vars with registry, detect drift."""
import os, json
from datetime import datetime, timezone

class CredentialReconciler:
    def __init__(self):
        self.registry_path = "/runtime/security/vault/registry.json"
    def scan_env(self):
        env_creds = {}
        for k, v in os.environ.items():
            if k.startswith("DS_"):
                base_name = k.split("__")[0].replace("DS_", "", 1).lower()
                field = k.split("__")[1].lower() if "__" in k else "value"
                env_creds.setdefault(base_name, {})[field] = len(v)
        return env_creds
    def reconcile(self):
        env_creds = self.scan_env()
        report = {"ts": datetime.now(timezone.utc).isoformat(), "env_groups": len(env_creds)}
        if os.path.exists(self.registry_path):
            with open(self.registry_path) as f: reg = json.load(f)
            reg_names = set(reg.keys())
            env_names = set()
            for bn in env_creds:
                for fld in env_creds[bn]:
                    env_names.add(bn + "_" + fld)
            report["registry_gaps"] = list(env_names - reg_names)[:20]
            report["env_gaps"] = list(reg_names - env_names)[:20]
        return report
    def auto_register_gaps(self):
        report = self.reconcile()
        reg = {}
        if os.path.exists(self.registry_path):
            with open(self.registry_path) as f: reg = json.load(f)
        count = 0
        for gap in report.get("registry_gaps", []):
            if gap not in reg:
                now = datetime.now(timezone.utc).isoformat()
                reg[gap] = {"name": gap, "type": gap.split("_")[0], "source": "reconciler", "created": now, "last_rotation": now, "status": "active"}
                count += 1
        with open(self.registry_path, "w") as f: json.dump(reg, f, indent=2)
        return {"registered": count}
