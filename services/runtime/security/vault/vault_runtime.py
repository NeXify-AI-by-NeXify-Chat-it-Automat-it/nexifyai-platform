#!/usr/bin/env python3
"""Vault Runtime — central secret injection interface for workers."""
import json, os
from datetime import datetime, timezone
class Vault:
    def get(self, name, worker="system"):
        env = f"DS_{name.upper()}"
        v = os.environ.get(env)
        if v: self._log(name, worker, "direct"); return v
        for k, vv in os.environ.items():
            if k.startswith("DS_") and name.upper() in k.replace("__","_"):
                self._log(name, worker, "matched"); return vv
        return None
    def get_set(self, name):
        prefix = f"DS_{name.upper()}__"
        return {k.replace(prefix,"").lower(): v for k, v in os.environ.items() if k.startswith(prefix)} or None
    def _log(self, name, worker, method):
        now = datetime.now(timezone.utc).isoformat()
        os.makedirs("/services/runtime/security/vault", exist_ok=True)
        with open("/services/runtime/security/vault/access.log", "a") as f:
            f.write(json.dumps({"ts": now, "secret": name, "worker": worker, "method": method})+"\n")

if __name__ == "__main__":
    v = Vault()
    sets = set()
    for k in os.environ:
        if k.startswith("DS_"):
            sets.add(k.split("__")[0].replace("DS_","",1).lower())
    print(json.dumps({"credential_sets": len(sets), "sets": sorted(sets)}, indent=2))
