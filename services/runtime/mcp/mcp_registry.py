#!/usr/bin/env python3
"""mcp_registry.py -- Central registry of all MCP capabilities with metadata."""
import json, logging, os, uuid
from datetime import datetime, timezone
log = logging.getLogger("mcp-registry")

class MCPRegistry:
    def __init__(self):
        self._capabilities = {}

    def register(self, cap_id, metadata):
        """Register a capability with full metadata."""
        entry = {"id": cap_id, "metadata": metadata, "ts": datetime.now(timezone.utc).isoformat(), "version": metadata.get("version", "1.0")}
        self._capabilities[cap_id] = entry
        log.info(f"Registered capability: {cap_id} (v{entry['version']})")
        return entry

    def get(self, cap_id):
        return self._capabilities.get(cap_id)

    def list_by_domain(self, domain=None):
        if domain: return {k:v for k,v in self._capabilities.items() if v.get("metadata",{}).get("domain") == domain}
        return dict(self._capabilities)

    def find_by_governance(self, level="required"):
        return {k:v for k,v in self._capabilities.items() if v.get("metadata",{}).get("governance") == level}

    def stats(self):
        domains = {}
        for c in self._capabilities.values():
            d = c.get("metadata",{}).get("domain","unknown")
            domains[d] = domains.get(d, 0) + 1
        return {"total": len(self._capabilities), "domains": domains}

REGISTRY = MCPRegistry()
def get_registry(): return REGISTRY

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reg = get_registry()
    reg.register("github.pr.create", {"domain":"github","governance":"required","audit":True,"rollback":True})
    print(json.dumps(reg.stats(), indent=2))
