#!/usr/bin/env python3
"""capability_dependencies.py -- Dependency resolver for MCP capabilities."""
import json, logging
log = logging.getLogger("cap-deps")

class CapabilityDependencyResolver:
    def __init__(self):
        self._deps = {}

    def add_dependency(self, cap_id, requires):
        self._deps[cap_id] = requires

    def resolve(self, cap_id, visited=None):
        if visited is None: visited = set()
        if cap_id in visited: return {"cap": cap_id, "cyclic": True, "path": list(visited)}
        visited.add(cap_id)
        deps = self._deps.get(cap_id, [])
        resolved = []
        for d in deps:
            sub = self.resolve(d, set(visited))
            if isinstance(sub, list): resolved.extend(sub)
            elif isinstance(sub, dict) and sub.get("cyclic"): return sub
            else: resolved.append(sub)
        return [cap_id] + list(set(deps))

RESOLVER = CapabilityDependencyResolver()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    RESOLVER.add_dependency("deployment.run", ["github.pr.create","governance.pass"])
    print(json.dumps(RESOLVER.resolve("deployment.run"), indent=2))
