#!/usr/bin/env python3
"""Expiry Monitor -- watches credential expiry dates, alerts."""
import os, json
from datetime import datetime, timezone

class ExpiryMonitor:
    def __init__(self):
        self.registry_path = "/runtime/security/vault/registry.json"
    def check(self, warning_days=[7, 3, 1]):
        if not os.path.exists(self.registry_path):
            return {"status": "no_registry"}
        with open(self.registry_path) as f: reg = json.load(f)
        now = datetime.now(timezone.utc)
        expiring = []
        expired = []
        for name, meta in reg.items():
            exp_str = meta.get("expires_at")
            if not exp_str: continue
            try: exp_dt = datetime.fromisoformat(exp_str)
            except: continue
            remaining = (exp_dt - now).total_seconds() / 86400
            if remaining < 0:
                expired.append({"name": name, "days_over": round(-remaining, 1)})
            else:
                for wd in warning_days:
                    if remaining <= wd:
                        expiring.append({"name": name, "expires_in": round(remaining, 1), "warn_level": wd})
                        break
        return {"expired": expired, "expiring_soon": expiring, "total": len(reg)}
