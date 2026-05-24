#!/usr/bin/env python3
"""semantic_capability_graph.py — Semantic relationship graph of all capabilities.
Understands: which caps compose, conflict, depend-on, and serve-similar-goals."""
import json, logging
from collections import defaultdict
log = logging.getLogger("semantic-cap-graph")

class SemanticCapabilityGraph:
    def __init__(self):
        self._nodes = {}; self._edges = defaultdict(list)  # cap -> [(relation, target)]
        self._goals = defaultdict(list)  # goal -> [cap_ids]

    def add_capability(self, cap_id, domain, goals=None, related_caps=None, risk="low"):
        self._nodes[cap_id] = {"domain": domain, "goals": goals or [], "risk": risk}
        for g in (goals or []): self._goals[g].append(cap_id)
        for rel in (related_caps or []):
            if isinstance(rel, tuple): self._edges[cap_id].append(rel)

    def find_by_goal(self, goal): return self._goals.get(goal, [])
    def get_related(self, cap_id): return [t for (r,t) in self._edges.get(cap_id,[])]
    def get_relations(self, cap_id): return self._edges.get(cap_id, [])
    def stats(self):
        return {"capabilities": len(self._nodes), "edges": sum(len(v) for v in self._edges.values()), "goals": len(self._goals)}

GRAPH = SemanticCapabilityGraph()

# Populate from existing MCP capabilities
GOALS = {
    "github.issue.create": ["triage","governance"], "github.issue.list": ["observe","triage"],
    "github.pr.create": ["delivery","code_change"], "github.pr.list": ["observe","governance"],
    "github.repo.info": ["observe","strategy"], "brain.query": ["knowledge","observe"],
    "brain.store": ["memory","learning"], "brain.count": ["observe","monitor"],
    "brain.category_search": ["knowledge","analysis"], "infra.systemd.status": ["monitor","infra"],
    "infra.systemd.list": ["monitor","infra"], "infra.disk.usage": ["monitor","infra"],
    "infra.process.list": ["security","monitor"], "infra.file.list": ["observe","infra"],
    "infra.service.restart": ["recovery","infra"], "security.audit.log": ["audit","governance"],
    "security.permissions.check": ["governance","security"], "security.threat.scan": ["security","monitor"],
    "runtime.health": ["monitor","observe"], "runtime.shell": ["infra","recovery"],
}
for cap, goals in GOALS.items():
    GRAPH.add_capability(cap, cap.split(".")[0], goals)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(GRAPH.stats()))
