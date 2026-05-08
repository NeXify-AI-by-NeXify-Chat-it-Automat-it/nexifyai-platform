"""
NeXifyAI — Causal Confidence Propagation (E5)

Confidence is NOT local. It propagates through the dependency graph.

Formula:
  effective_confidence(node) =
      local_confidence(node)
      × Π(parent_confidence × edge_weight × temporal_decay)

Where:
  - local_confidence: direct confidence from probes/validation
  - parent_confidence: confidence of each upstream dependency
  - edge_weight: how strongly this dependency affects this node (0.0-1.0)
  - temporal_decay: 0.95^(hours since last probe of parent)

Effects:
  - Blast radius calculation (which services are impacted by a failure)
  - Cascading degradation detection (confidence erosion through graph)
  - Dependency-weighted deploy blocking (don't deploy if critical deps degraded)
  - Probabilistic rollback triggers (confidence drop > threshold → rollback)
  - Causal incident graphs (trace root cause through confidence chain)
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from enum import Enum


class ConfidenceLevel(Enum):
    EXCELLENT = "excellent"   # ≥ 0.9
    GOOD = "good"              # ≥ 0.75
    FAIR = "fair"              # ≥ 0.5
    DEGRADED = "degraded"      # ≥ 0.25
    CRITICAL = "critical"      # < 0.25


@dataclass
class ConfidenceNode:
    """A node in the confidence propagation graph."""
    service: str
    local_confidence: float = 1.0
    effective_confidence: float = 1.0
    parents: Dict[str, float] = field(default_factory=dict)  # service → edge_weight
    children: List[str] = field(default_factory=list)
    
    # Temporal data
    last_probed: float = field(default_factory=time.time)
    confidence_history: List[Tuple[float, float]] = field(default_factory=list)  # (timestamp, confidence)
    
    # Propagation metadata
    propagation_depth: int = 0  # How many hops from root cause
    degraded_by: Optional[str] = None  # Which parent caused degradation
    blast_radius_impact: int = 0  # How many downstream services affected
    
    @property
    def level(self) -> ConfidenceLevel:
        if self.effective_confidence >= 0.9:
            return ConfidenceLevel.EXCELLENT
        elif self.effective_confidence >= 0.75:
            return ConfidenceLevel.GOOD
        elif self.effective_confidence >= 0.5:
            return ConfidenceLevel.FAIR
        elif self.effective_confidence >= 0.25:
            return ConfidenceLevel.DEGRADED
        return ConfidenceLevel.CRITICAL
    
    @property
    def age_hours(self) -> float:
        return (time.time() - self.last_probed) / 3600


# ══════════════════════════════════════════════
# PROPAGATION ENGINE
# ══════════════════════════════════════════════

class CausalPropagationEngine:
    """
    Propagates confidence through the dependency graph.
    
    When a service's confidence drops, its downstream dependents
    are penalized proportionally to the edge weight and temporal decay.
    
    The engine walks the graph topologically, applying the formula:
      effective = local × Π(parent_effective × edge_weight × temporal_decay)
    """
    
    DECAY_RATE = 0.95  # Per hour
    DEFAULT_EDGE_WEIGHT = 0.8  # Default dependency strength
    PROPAGATION_DAMPING = 0.7  # Each hop reduces impact (prevents amplification)
    BLAST_RADIUS_THRESHOLD = 0.7  # Below this, service is "impacted"
    
    def __init__(self):
        self.nodes: Dict[str, ConfidenceNode] = {}
        self._load_topology()
    
    def _load_topology(self):
        """Load dependency topology from Canonical Service Registry."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        for svc_id, svc in CANONICAL_REGISTRY.items():
            node = ConfidenceNode(service=svc_id)
            
            # Parents: services this node depends on
            for dep_id in svc.depends_on:
                node.parents[dep_id] = self.DEFAULT_EDGE_WEIGHT
            
            self.nodes[svc_id] = node
        
        # Build child relationships (reverse of depends_on)
        for svc_id, node in self.nodes.items():
            for parent_id in node.parents:
                if parent_id in self.nodes:
                    self.nodes[parent_id].children.append(svc_id)
    
    def set_local_confidence(self, service: str, confidence: float):
        """Set local confidence for a service (from direct probes/validation)."""
        if service not in self.nodes:
            self.nodes[service] = ConfidenceNode(service=service)
        
        node = self.nodes[service]
        node.local_confidence = max(0.0, min(1.0, confidence))
        node.last_probed = time.time()
        node.confidence_history.append((time.time(), confidence))
        
        # Keep only last 100 history entries
        if len(node.confidence_history) > 100:
            node.confidence_history = node.confidence_history[-100:]
    
    def propagate(self, root_service: str = None) -> Dict[str, float]:
        """
        Propagate confidence through the entire dependency graph.
        
        If root_service is provided, only propagate from that service downstream.
        Otherwise, recompute all nodes.
        
        Returns {service: effective_confidence} for all nodes.
        """
        if root_service and root_service in self.nodes:
            # Targeted propagation from a specific degradation
            self._propagate_from(root_service, depth=0, degraded_by=root_service)
        else:
            # Full recomputation — topological order
            visited = set()
            for svc_id in self.nodes:
                if svc_id not in visited:
                    self._compute_effective(svc_id, visited, set())
        
        return {svc: node.effective_confidence for svc, node in self.nodes.items()}
    
    def _propagate_from(self, service: str, depth: int, degraded_by: str):
        """Propagate confidence degradation downstream from a service."""
        node = self.nodes.get(service)
        if not node:
            return
        
        node.propagation_depth = depth
        node.degraded_by = degraded_by if depth > 0 else None
        
        # Compute effective confidence for this node
        self._compute_node(node)
        
        # Propagate to children
        for child_id in node.children:
            child = self.nodes.get(child_id)
            if not child:
                continue
            
            # Apply propagation damping: impact reduces with each hop
            damping = self.PROPAGATION_DAMPING ** (depth + 1)
            
            # Child's local confidence is penalized by parent's effective confidence
            parent_impact = node.effective_confidence * self.DEFAULT_EDGE_WEIGHT * damping
            child.local_confidence = min(child.local_confidence, parent_impact + (1 - damping))
            
            # Recurse
            self._propagate_from(child_id, depth + 1, degraded_by)
    
    def _compute_effective(self, service: str, visited: Set[str], path: Set[str]) -> float:
        """Recursively compute effective confidence (topological)."""
        if service in path:
            return self.nodes[service].effective_confidence  # Cycle — use current value
        
        node = self.nodes.get(service)
        if not node:
            return 1.0
        
        if service in visited:
            return node.effective_confidence
        
        path.add(service)
        
        # Compute parents first
        parent_product = 1.0
        for parent_id, edge_weight in node.parents.items():
            if parent_id in self.nodes:
                parent_effective = self._compute_effective(parent_id, visited, path)
                parent_node = self.nodes[parent_id]
                
                # Temporal decay on parent confidence
                temporal = self.DECAY_RATE ** parent_node.age_hours
                
                # Contribution: parent_effective × edge_weight × temporal_decay
                contribution = parent_effective * edge_weight * temporal
                parent_product *= max(0.3, contribution)  # Floor: 0.3 prevents total collapse
            
            elif parent_id not in self.nodes:
                # Unknown parent — assume healthy
                pass
        
        node.effective_confidence = round(
            node.local_confidence * parent_product, 2
        )
        
        path.remove(service)
        visited.add(service)
        
        return node.effective_confidence
    
    def _compute_node(self, node: ConfidenceNode):
        """Compute effective confidence for a single node."""
        parent_product = 1.0
        
        for parent_id, edge_weight in node.parents.items():
            parent_node = self.nodes.get(parent_id)
            if not parent_node:
                continue
            
            temporal = self.DECAY_RATE ** parent_node.age_hours
            contribution = parent_node.effective_confidence * edge_weight * temporal
            parent_product *= max(0.3, contribution)
        
        node.effective_confidence = round(node.local_confidence * parent_product, 2)
    
    def blast_radius(self, service: str) -> Dict:
        """
        Calculate blast radius if a service degrades.
        Returns all downstream services that would be impacted.
        """
        impacted = []
        node = self.nodes.get(service)
        if not node:
            return {"service": service, "impacted": [], "total": 0}
        
        for child_id in node.children:
            child = self.nodes.get(child_id)
            if child:
                propagated_confidence = child.local_confidence * node.effective_confidence * self.DEFAULT_EDGE_WEIGHT
                if propagated_confidence < self.BLAST_RADIUS_THRESHOLD:
                    impacted.append({
                        "service": child_id,
                        "propagated_confidence": round(propagated_confidence, 2),
                        "current_effective": child.effective_confidence,
                        "level": child.level.value,
                    })
        
        return {
            "service": service,
            "current_confidence": node.effective_confidence,
            "impacted_services": impacted,
            "total_impacted": len(impacted),
            "max_propagation_depth": max((n.propagation_depth for n in self.nodes.values() if n.degraded_by == service), default=0),
        }
    
    def degrade_cascade_report(self) -> Dict:
        """Full causal confidence propagation report."""
        cascade_chain = []
        
        # Find root causes (nodes with degraded_by=None and low confidence)
        for node in self.nodes.values():
            if node.local_confidence < 0.8 and node.degraded_by is None:
                cascade_chain.append({
                    "root_cause": node.service,
                    "confidence": node.local_confidence,
                    "level": node.level.value,
                    "propagated_to": len([n for n in self.nodes.values() if n.degraded_by == node.service]),
                    "depth": max((n.propagation_depth for n in self.nodes.values() if n.degraded_by == node.service), default=0),
                })
        
        return {
            "timestamp": time.time(),
            "total_nodes": len(self.nodes),
            "degraded_nodes": len([n for n in self.nodes.values() if n.level in (ConfidenceLevel.DEGRADED, ConfidenceLevel.CRITICAL)]),
            "cascade_chains": cascade_chain,
            "nodes": [
                {
                    "service": n.service,
                    "local": n.local_confidence,
                    "effective": n.effective_confidence,
                    "level": n.level.value,
                    "degraded_by": n.degraded_by,
                    "depth": n.propagation_depth,
                }
                for n in self.nodes.values()
            ],
            "should_block_deploy": any(
                n.effective_confidence < 0.5 and len(n.children) > 2
                for n in self.nodes.values()
            ),
        }
