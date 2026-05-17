#!/usr/bin/env python3
"""capability_discovery_runtime.py -- Runtime discovery of available MCP capabilities."""
import json, logging
from mcp_registry import get_registry
log = logging.getLogger("cap-discovery")

class CapabilityDiscoveryRuntime:
    def discover(self, query=None):
        reg = get_registry()
        all_caps = reg.list_by_domain()
        if not query: return {"capabilities": list(all_caps.keys()), "total": len(all_caps)}
        query_lower = query.lower()
        results = {k:v for k,v in all_caps.items() if query_lower in k.lower() or query_lower in v.get("metadata",{}).get("domain","").lower()}
        return {"capabilities": list(results.keys()), "total": len(results), "query": query}
    def discover_by_agent(self, agent):
        from mcp_agent_permissions import PERMS
        reg = get_registry()
        allowed = [k for k in reg.list_by_domain() if PERMS.allowed(agent, k)]
        return {"agent": agent, "allowed": allowed, "total": len(allowed)}

DISCOVERY = CapabilityDiscoveryRuntime()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(DISCOVERY.discover("github"), indent=2))
