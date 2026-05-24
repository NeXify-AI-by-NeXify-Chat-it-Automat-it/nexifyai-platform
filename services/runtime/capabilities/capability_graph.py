#!/usr/bin/env python3
"""capability_graph.py -- Semantic graph of all MCP capabilities and their relationships."""
import json, logging, uuid
from collections import defaultdict
log = logging.getLogger("cap-graph")

class CapabilityGraph:
    def __init__(self):
        self._nodes = {}; self._edges = {}  # cap_id -> list of related cap_ids

    def add_capability(self, cap_id, metadata):
        self._nodes[cap_id] = metadata
        self._edges[cap_id] = metadata.get("depends_on", [])

    def add_dependency(self, from_cap, to_cap):
        if from_cap not in self._edges: self._edges[from_cap] = []
        self._edges[from_cap].append(to_cap)

    def get_dependents(self, cap_id):
        return [c for c, deps in self._edges.items() if cap_id in deps and c != cap_id]

    def find_by_domain(self, domain):
        return {k:v for k,v in self._nodes.items() if v.get("domain") == domain}

    def stats(self):
        domains = defaultdict(int)
        for n in self._nodes.values(): domains[n.get("domain","unknown")] += 1
        return {"capabilities": len(self._nodes), "dependencies": sum(len(v) for v in self._edges.values()), "domains": dict(domains)}

GRAPH = CapabilityGraph()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    GRAPH.add_capability("github.pr.create", {"domain":"github","governance":"required"})
    GRAPH.add_capability("deployment.run", {"domain":"deployment","depends_on":["github.pr.create"]})
    print(json.dumps(GRAPH.stats(), indent=2))
