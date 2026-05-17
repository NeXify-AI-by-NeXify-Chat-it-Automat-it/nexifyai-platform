#!/usr/bin/env python3
"""Secret Registry — central inventory of all managed secrets."""
import json, os
from datetime import datetime, timezone

class SecretRegistry:
    def __init__(self):
        self.store_path = "/runtime/security/vault/registry.json"
        self.secrets = {}
        self._load()
    def _load(self):
        if os.path.exists(self.store_path):
            with open(self.store_path) as f: self.secrets = json.load(f)
    def _save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, 'w') as f: json.dump(self.secrets, f, indent=2)
    def register(self, name, stype, source, rotation_days=90):
        now = datetime.now(timezone.utc).isoformat()
        self.secrets[name] = {"name": name, "type": stype, "source": source, "created": now, "last_rotation": now, "rotation_days": rotation_days, "status": "active", "access_count": 0}
        self._save()
    def record_access(self, name, worker=""):
        if name in self.secrets:
            self.secrets[name]["access_count"] += 1
            self.secrets[name]["last_access"] = datetime.now(timezone.utc).isoformat()
            self.secrets[name]["last_worker"] = worker
            self._save()
    def mark_rotated(self, name):
        if name in self.secrets:
            self.secrets[name]["last_rotation"] = datetime.now(timezone.utc).isoformat()
            self.secrets[name]["status"] = "active"
            self._save()
    def revoke(self, name):
        if name in self.secrets:
            self.secrets[name]["status"] = "revoked"
            self.secrets[name]["revoked_at"] = datetime.now(timezone.utc).isoformat()
            self._save()
    def get_due_rotation(self):
        now = datetime.now(timezone.utc)
        return [n for n,m in self.secrets.items() if (now - datetime.fromisoformat(m["last_rotation"])).days >= m.get("rotation_days", 90)]
    def summary(self):
        return {"total": len(self.secrets), "active": sum(1 for s in self.secrets.values() if s["status"]=="active"), "revoked": sum(1 for s in self.secrets.values() if s["status"]=="revoked"), "due_rotation": len(self.get_due_rotation())}

if __name__ == "__main__":
    reg = SecretRegistry()
    print(json.dumps(reg.summary()))
