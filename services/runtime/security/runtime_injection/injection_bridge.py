#!/usr/bin/env python3
"""Runtime Injection Bridge -- connects vault_compat to external vault (Infisical)."""
"""Phase 4-ready: swap DS_ env source with Infisical API calls."""
import os, json

class InjectionBridge:
    def __init__(self, source="env"):
        self.source = source
        self.cache = {}
    def get(self, key, default=None):
        if self.source == "env":
            env_key = "DS_" + key.upper()
            val = os.environ.get(env_key)
            if val: return val
            for k, v in os.environ.items():
                if k.startswith("DS_") and key.upper() in k.replace("__", "_"):
                    return v
            val = os.environ.get(key)
            return val if val else default
        return default
    def set_source(self, source_type):
        """Switch to external vault backend."""
        self.source = source_type

if __name__ == "__main__":
    b = InjectionBridge()
    print(json.dumps({"source": b.source, "ready": True}))
