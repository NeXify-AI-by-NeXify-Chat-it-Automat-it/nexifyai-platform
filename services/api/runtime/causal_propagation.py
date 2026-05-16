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
    FEEDBACK_WEIGHT = 0.3       # Bidirectional: how much child instability erodes parent confidence
    FEEDBACK_THRESHOLD = 3      # Min number of degraded children to trigger parent erosion
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
    
    # ══════════════════════════════════════════
    # E5.5: BIDIRECTIONAL PROPAGATION
    # ══════════════════════════════════════════
    
    def propagate_bidirectional(self) -> Dict[str, float]:
        """
        Bidirectional confidence propagation.
        
        Forward:  parent↓  → children↓ (standard propagation)
        Backward: many degraded children → parent confidence↓ (inferential)
        
        If ≥ FEEDBACK_THRESHOLD children are degraded without a known
        parent degradation, the system infers the parent's confidence
        may be overstated and applies a feedback penalty.
        """
        # First: standard forward propagation
        self.propagate()
        
        # Second: backward feedback loop
        for parent_id, parent_node in self.nodes.items():
            if not parent_node.children:
                continue
            
            # Find degraded children that are NOT degraded by this parent
            degraded_children = []
            for child_id in parent_node.children:
                child = self.nodes.get(child_id)
                if child and child.effective_confidence < 0.7:
                    if child.degraded_by != parent_id or child.degraded_by is None:
                        degraded_children.append(child)
            
            # Feedback: if many children degraded independently, parent may be overstated
            if len(degraded_children) >= self.FEEDBACK_THRESHOLD:
                avg_child_confidence = sum(c.effective_confidence for c in degraded_children) / len(degraded_children)
                feedback_penalty = (1 - avg_child_confidence) * self.FEEDBACK_WEIGHT
                
                old_effective = parent_node.effective_confidence
                parent_node.effective_confidence = round(
                    max(0.1, parent_node.effective_confidence - feedback_penalty), 2
                )
                
                # Don't mark as degraded_by — this is inferential, not causal
                parent_node.confidence_history.append((
                    time.time(),
                    parent_node.effective_confidence,
                ))
        
        return {svc: node.effective_confidence for svc, node in self.nodes.items()}
    
    # ══════════════════════════════════════════
    # E7: AUTONOMOUS RECONCILIATION
    # ══════════════════════════════════════════
    
    def propose_reconciliation(self, service: str) -> Dict:
        """
        Propose a reconciliation plan for a degraded service.
        
        NOT: "restart blindly"
        BUT:  simulate remediation → estimate confidence delta →
              compare alternatives → apply only if epistemic gain > 0
        
        Returns a plan with:
        - Root cause analysis
        - Remediation options ranked by expected epistemic gain
        - Rollback vs repair comparison
        - Pre-action confidence snapshot
        """
        node = self.nodes.get(service)
        if not node:
            return {"error": f"Service {service} not found"}
        
        # Determine root cause
        root_cause = node.degraded_by or service
        
        # Gather current state
        pre_snapshot = {
            svc: n.effective_confidence
            for svc, n in self.nodes.items()
        }
        
        # Generate remediation options
        options = []
        
        # Option 1: Restart the degraded service
        restart_gain = self._estimate_restart_gain(service)
        options.append({
            "action": f"restart {service}",
            "type": "repair",
            "expected_confidence_delta": round(restart_gain, 2),
            "risk": "low" if restart_gain > 0.3 else "medium",
            "blast_radius": len(node.children),
            "description": f"Restart {service} and re-observe after stabilization wait",
        })
        
        # Option 2: Restart the root cause (if different)
        if root_cause != service:
            root_gain = self._estimate_restart_gain(root_cause)
            options.append({
                "action": f"restart {root_cause} (root cause)",
                "type": "root_cause_repair",
                "expected_confidence_delta": round(root_gain, 2),
                "risk": "medium",
                "blast_radius": len(self.nodes.get(root_cause, node).children),
                "description": f"Address root cause by restarting {root_cause}. May cascade to {len(self.nodes.get(root_cause, node).children)} dependents.",
            })
        
        # Option 3: Rollback (reverse last known-good state)
        rollback_gain = self._estimate_rollback_gain(service)
        options.append({
            "action": f"rollback {service}",
            "type": "rollback",
            "expected_confidence_delta": round(rollback_gain, 2),
            "risk": "high",
            "blast_radius": len(node.children) + 1,
            "description": f"Rollback {service} to last known-good deployment. Higher risk, broader blast radius.",
        })
        
        # Sort by expected gain (descending)
        options.sort(key=lambda o: -o["expected_confidence_delta"])
        
        # Determine best action
        best = options[0] if options else None
        should_apply = best and best["expected_confidence_delta"] > 0.15
        
        return {
            "service": service,
            "root_cause": root_cause,
            "current_confidence": node.effective_confidence,
            "current_level": node.level.value,
            "degraded_by": node.degraded_by,
            "propagation_depth": node.propagation_depth,
            "options": options,
            "recommended": best,
            "should_apply": should_apply,
            "reason": (
                f"Expected confidence gain +{best['expected_confidence_delta']:.2f} — apply"
                if should_apply
                else f"Expected gain too low ({best['expected_confidence_delta']:.2f}) — manual review recommended"
            ) if best else "No viable options found",
            "pre_snapshot": pre_snapshot,
        }
    
    def _estimate_restart_gain(self, service: str) -> float:
        """Estimate confidence improvement if service is restarted."""
        node = self.nodes.get(service)
        if not node:
            return 0.0
        
        # Restart typically resolves local issues → local_confidence → 0.9
        simulated_local = 0.9
        current_effective = node.effective_confidence
        
        # Simulate: what would effective confidence be after restart?
        # Local goes to 0.9, parents unchanged, temporal decay reset
        parent_product = 1.0
        for parent_id, edge_weight in node.parents.items():
            parent_node = self.nodes.get(parent_id)
            if parent_node:
                parent_product *= parent_node.effective_confidence * edge_weight
        
        simulated_effective = simulated_local * parent_product
        
        return simulated_effective - current_effective
    
    def _estimate_rollback_gain(self, service: str) -> float:
        """Estimate confidence improvement if service is rolled back."""
        node = self.nodes.get(service)
        if not node:
            return 0.0
        
        # Rollback is riskier — max gain is restoring to last known good
        # Use confidence_history to estimate
        if len(node.confidence_history) >= 2:
            last_good = max(c for _, c in node.confidence_history[-10:])
            return last_good - node.effective_confidence
        
        return self._estimate_restart_gain(service) * 0.8  # Rollback slightly less effective
    
    def apply_reconciliation(self, service: str, action: str) -> Dict:
        """
        Apply a reconciliation action and re-propagate.
        
        After applying:
        1. Set service local_confidence based on action type
        2. Re-propagate through entire graph
        3. Compute epistemic gain (pre vs post)
        4. Return reconciliation result
        
        This is the E7 core: action → re-observation → validation.
        """
        pre_snapshot = {svc: n.effective_confidence for svc, n in self.nodes.items()}
        
        # Simulate the action's effect on local confidence
        if "restart" in action:
            confidence_boost = 0.9  # Restart typically resolves transient issues
        elif "rollback" in action:
            confidence_boost = 0.85  # Rollback slightly more conservative
        else:
            confidence_boost = 0.8
        
        self.set_local_confidence(service, confidence_boost)
        
        # Re-propagate
        self.propagate(service)
        
        post_snapshot = {svc: n.effective_confidence for svc, n in self.nodes.items()}
        
        # Compute epistemic gain
        gains = {}
        total_gain = 0.0
        for svc in pre_snapshot:
            delta = post_snapshot.get(svc, 0) - pre_snapshot[svc]
            gains[svc] = round(delta, 2)
            total_gain += delta
        
        avg_gain = total_gain / max(1, len(gains))
        success = avg_gain > 0.05  # Net positive epistemic gain
        
        return {
            "action": action,
            "service": service,
            "success": success,
            "average_confidence_gain": round(avg_gain, 3),
            "per_service_gains": gains,
            "pre_avg_confidence": round(sum(pre_snapshot.values()) / len(pre_snapshot), 2),
            "post_avg_confidence": round(sum(post_snapshot.values()) / len(post_snapshot), 2),
            "requires_reobservation": True,  # Per Constitution §I.2
            "next_step": "Re-observe all observers after stabilization wait",
        }
