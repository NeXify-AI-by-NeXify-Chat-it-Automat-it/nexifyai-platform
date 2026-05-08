"""
NeXifyAI — Runtime Truth Graph (E2.2)
Models runtime relationships as a directed graph with causality edges.

NOT: "qdrant: down" (boolean)
BUT:  "qdrant reachable from host ✓, from container ✗ — blocked by 127.0.0.1 port binding"

Each edge is qualified with:
- reachable_via: which path works
- blocked_by: what prevents reachability
- projected_as: what current health checks report
- recovered_by: how to fix
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
import time


class EdgeType(Enum):
    DEPENDS_ON = "depends_on"           # Service A requires service B
    REACHABLE_VIA = "reachable_via"     # Observer O can reach service S via path P
    BLOCKED_BY = "blocked_by"           # Observer O cannot reach service S because of X
    PROJECTED_AS = "projected_as"       # Health system reports service S as status T
    RECOVERED_BY = "recovered_by"       # Service S can be restored via action A
    CONTRADICTS = "contradicts"         # Two observers report conflicting states


class TruthValue(Enum):
    """Not binary. Multi-valued truth."""
    CANONICALLY_RUNNING = "canonically_running"    # Verified via source_of_truth
    REACHABLE = "reachable"                         # TCP/HTTP probe succeeded
    UNREACHABLE = "unreachable"                     # Probe failed
    DEGRADED = "degraded"                           # Reachable but limited (e.g., 401)
    UNKNOWN = "unknown"                             # Not yet probed
    FALSE_POSITIVE = "false_positive"               # Reports healthy but isn't
    FALSE_NEGATIVE = "false_negative"               # Reports down but isn't


@dataclass
class TruthEdge:
    """A directed edge in the truth graph with causality context."""
    source: str           # Observer or service ID
    target: str           # Service ID
    edge_type: EdgeType
    truth_value: TruthValue
    description: str      # Human-readable explanation of WHY
    evidence: str         # Raw probe data / command output
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TruthGraph:
    """Directed graph of runtime truth relationships."""
    nodes: Set[str] = field(default_factory=set)      # All service + observer IDs
    edges: List[TruthEdge] = field(default_factory=list)
    
    def add_edge(self, edge: TruthEdge):
        self.nodes.add(edge.source)
        self.nodes.add(edge.target)
        self.edges.append(edge)
    
    def find_contradictions(self) -> List[Dict]:
        """
        Find pairs of edges that contradict each other.
        Example: Observer A says "healthy", Observer B says "down" for same target.
        """
        contradictions = []
        for i, e1 in enumerate(self.edges):
            for e2 in self.edges[i+1:]:
                if e1.target != e2.target:
                    continue
                if e1.source == e2.source:
                    continue
                
                # Contradiction: one says reachable, other says unreachable
                reachable_values = {TruthValue.REACHABLE, TruthValue.CANONICALLY_RUNNING}
                unreachable_values = {TruthValue.UNREACHABLE, TruthValue.FALSE_NEGATIVE}
                
                e1_positive = e1.truth_value in reachable_values
                e2_positive = e2.truth_value in reachable_values
                e1_negative = e1.truth_value in unreachable_values
                e2_negative = e2.truth_value in unreachable_values
                
                if (e1_positive and e2_negative):
                    contradictions.append({
                        "target": e1.target,
                        "observer_a": e1.source,
                        "observer_a_says": e1.truth_value.value,
                        "observer_b": e2.source,
                        "observer_b_says": e2.truth_value.value,
                        "diagnosis": f"Contradiction: {e1.source} sees {e1.target} as {e1.truth_value.value}, but {e2.source} sees {e2.target} as {e2.truth_value.value}",
                        "causes": {
                            "a_reason": e1.description,
                            "b_reason": e2.description,
                        }
                    })
        
        return contradictions
    
    def find_false_positives(self) -> List[Dict]:
        """
        Find services that report as healthy but are actually degraded/unreachable.
        """
        false_positives = []
        
        for edge in self.edges:
            if edge.truth_value == TruthValue.FALSE_POSITIVE:
                # Find the canonical edge for same target
                canonical = [e for e in self.edges 
                           if e.target == edge.target 
                           and e.edge_type == EdgeType.DEPENDS_ON
                           and e.truth_value == TruthValue.CANONICALLY_RUNNING]
                
                false_positives.append({
                    "target": edge.target,
                    "projected_by": edge.source,
                    "projected_as": edge.truth_value.value,
                    "actually": "not as healthy as projected",
                    "evidence": edge.evidence,
                    "canonical_state": [e.evidence for e in canonical],
                })
        
        return false_positives
    
    def recovery_paths(self, target: str) -> List[TruthEdge]:
        """Get all recovery edges for a service."""
        return [e for e in self.edges 
                if e.target == target and e.edge_type == EdgeType.RECOVERED_BY]
    
    def to_dict(self) -> Dict:
        return {
            "nodes": list(self.nodes),
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.edge_type.value,
                    "truth": e.truth_value.value,
                    "description": e.description,
                }
                for e in self.edges
            ],
            "contradictions": self.find_contradictions(),
            "false_positives": self.find_false_positives(),
        }


# ══════════════════════════════════════════════
# BUILD TRUTH GRAPH FROM E1 DATA
# ══════════════════════════════════════════════

def build_truth_graph() -> TruthGraph:
    """
    Build the runtime truth graph from the canonical service registry
    and topology probe results.
    """
    from backend.runtime.service_registry import CANONICAL_REGISTRY, ObserverPosition
    
    graph = TruthGraph()
    
    for svc_id, svc in CANONICAL_REGISTRY.items():
        graph.nodes.add(svc_id)
        
        # Canonical state edge
        canonical_state = TruthValue.CANONICALLY_RUNNING if svc.is_canonically_running else TruthValue.UNKNOWN
        graph.add_edge(TruthEdge(
            source="vps-host",
            target=svc_id,
            edge_type=EdgeType.DEPENDS_ON,
            truth_value=canonical_state,
            description=f"Canonical check: {svc.source_of_truth_command}",
            evidence=svc.source_of_truth,
        ))
        
        # Observer-specific edges
        for ep in svc.endpoints:
            if ep.is_reachable is None:
                continue
            
            truth = TruthValue.REACHABLE if ep.is_reachable else TruthValue.UNREACHABLE
            
            # Diagnose WHY unreachable
            if not ep.is_reachable:
                if "127.0.0.1" in ep.url or "localhost" in ep.url:
                    desc = f"Port bound to localhost — not routable from {ep.observer.value}"
                    truth = TruthValue.FALSE_NEGATIVE  # Service IS running, just not reachable
                elif ep.error and "connection refused" in (ep.error or "").lower():
                    desc = f"Connection refused — network isolation between {ep.observer.value} and {svc_id}"
                    truth = TruthValue.FALSE_NEGATIVE
                else:
                    desc = f"Unreachable from {ep.observer.value}: {ep.error or 'unknown reason'}"
            else:
                desc = f"Reachable from {ep.observer.value} via {ep.url} ({ep.protocol})"
            
            graph.add_edge(TruthEdge(
                source=ep.observer.value,
                target=svc_id,
                edge_type=EdgeType.REACHABLE_VIA if ep.is_reachable else EdgeType.BLOCKED_BY,
                truth_value=truth,
                description=desc,
                evidence=f"{ep.protocol} {ep.url} → {'OK' if ep.is_reachable else 'FAIL'}",
            ))
        
        # Recovery edge
        if svc.recovery_command:
            graph.add_edge(TruthEdge(
                source="operator",
                target=svc_id,
                edge_type=EdgeType.RECOVERED_BY,
                truth_value=TruthValue.UNKNOWN,
                description=f"Recovery: {svc.recovery_command}",
                evidence=svc.recovery_validation,
            ))
        
        # Health projection edges
        for observer, projection in svc.health_projections.items():
            if "healthy" in projection.lower():
                truth = TruthValue.REACHABLE
            elif "down" in projection.lower() or "unreachable" in projection.lower():
                truth = TruthValue.FALSE_NEGATIVE if svc.is_canonically_running else TruthValue.UNREACHABLE
            else:
                truth = TruthValue.DEGRADED
            
            graph.add_edge(TruthEdge(
                source=observer,
                target=svc_id,
                edge_type=EdgeType.PROJECTED_AS,
                truth_value=truth,
                description=f"Health projection from {observer}: {projection[:100]}",
                evidence=projection,
            ))
        
        # Dependency edges
        for dep_id in svc.depends_on:
            graph.add_edge(TruthEdge(
                source=svc_id,
                target=dep_id,
                edge_type=EdgeType.DEPENDS_ON,
                truth_value=TruthValue.UNKNOWN,
                description=f"{svc_id} requires {dep_id}",
                evidence=f"Dependency declared in service registry",
            ))
    
    return graph


def graph_summary() -> str:
    """CLI-friendly truth graph summary."""
    graph = build_truth_graph()
    data = graph.to_dict()
    
    lines = [
        "═══ RUNTIME TRUTH GRAPH ═══",
        f"Nodes: {len(data['nodes'])}",
        f"Edges: {len(data['edges'])}",
        f"Contradictions: {len(data['contradictions'])}",
        f"False Positives: {len(data['false_positives'])}",
        "",
    ]
    
    if data["contradictions"]:
        lines.append("CONTRADICTIONS:")
        for c in data["contradictions"]:
            lines.append(f"  ⚡ {c['target']}: {c['diagnosis']}")
        lines.append("")
    
    if data["false_positives"]:
        lines.append("FALSE POSITIVES:")
        for fp in data["false_positives"]:
            lines.append(f"  🔍 {fp['target']}: projected as {fp['projected_as']} by {fp['projected_by']}")
        lines.append("")
    
    lines.append("EDGES:")
    for e in data["edges"]:
        icon = {"reachable_via": "→", "blocked_by": "✗", "depends_on": "↓", 
                 "projected_as": "◈", "recovered_by": "♻", "contradicts": "⚡"}.get(e["type"], "?")
        lines.append(f"  {icon} {e['source']} → {e['target']} [{e['truth']}] {e['description'][:80]}")
    
    return "\n".join(lines)
