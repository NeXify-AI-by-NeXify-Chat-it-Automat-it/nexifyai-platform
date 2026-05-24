#!/usr/bin/env python3
"""runtime_dep_graph.py -- Dependency graph of all runtime systems and their interdependencies."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("runtime-deps")

DEPENDENCIES = {
    "planner_daemon": {"depends": ["event_bus"], "required_by": ["capability_scheduler","priority_runtime"]},
    "event_bus": {"depends": [], "required_by": ["*"]},
    "reconciliation": {"depends": ["brain"], "required_by": ["watchdog"]},
    "brain": {"depends": [], "required_by": ["*"]},
    "watchdog": {"depends": ["event_bus"], "required_by": ["incident_manager"]},
    "incident_manager": {"depends": ["watchdog"], "required_by": ["recovery"]},
    "governance": {"depends": ["policy_engine"], "required_by": ["delivery"]},
    "delivery": {"depends": ["governance","reconciliation"], "required_by": []},
}

def get_deps(system):
    return DEPENDENCIES.get(system, {"depends":[],"required_by":[]})

def validate_chain(start, target):
    visited = set()
    def dfs(node):
        if node == target: return True
        if node in visited: return False
        visited.add(node)
        for dep in DEPENDENCIES.get(node,{}).get("depends",[]):
            if dfs(dep): return True
        return False
    return dfs(start)

if __name__ == "__main__":
    import sys; s = sys.argv[1] if len(sys.argv)>1 else "delivery"
    print(json.dumps(get_deps(s), indent=2))
