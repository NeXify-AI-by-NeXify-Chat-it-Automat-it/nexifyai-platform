"""
NeXifyAI — Counterfactual Engine (E9)
Deterministic simulation of recovery actions. NOT LLM speculation.

Architecture:
  snapshot_t + typed_action + event_replay + incremental_propagation
  = delta(confidence)

Components:
  E9.1 — Typed Actions: RestartService, RollbackDeployment, ScaleReplica, DoNothing
  E9.2 — Copy-on-Write Snapshot Graph: persistent state, delta overlays
  E9.3 — Utility Engine: multi-objective optimization

Principle: LLM proposes strategies. Runtime evaluates them.
          NOT: LLM imagines outcomes.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod


# ══════════════════════════════════════════════
# E9.1 — TYPED ACTIONS (Operational Semantics)
# ══════════════════════════════════════════════

class ActionType(Enum):
    RESTART = "restart"
    ROLLBACK = "rollback"
    SCALE = "scale"
    DO_NOTHING = "do_nothing"
    PORT_REBIND = "port_rebind"
    CONFIG_CHANGE = "config_change"


@dataclass
class TypedAction(ABC):
    """Abstract base for typed operational actions."""
    action_type: ActionType = ActionType.RESTART
    service: str = ""
    description: str = ""
    
    @abstractmethod
    def simulate_effect(self, current_confidence: float) -> float:
        """Simulate the effect on local confidence. Returns estimated post-action confidence."""
        pass
    
    @abstractmethod
    def blast_radius(self, children_count: int) -> int:
        """Estimate how many downstream services are affected."""
        pass
    
    @abstractmethod
    def rollback_risk(self) -> float:
        """Probability that this action makes things worse (0.0-1.0)."""
        pass
    
    @abstractmethod
    def recovery_time_estimate(self) -> float:
        """Estimated seconds until convergence."""
        pass


@dataclass
class RestartService(TypedAction):
    """Restart a specific service."""
    
    def __post_init__(self):
        self.action_type = ActionType.RESTART
        self.description = f"Restart {self.service}"
    
    def simulate_effect(self, current_confidence: float) -> float:
        # Restart typically restores to ~0.85-0.95, with diminishing returns
        if current_confidence < 0.3:
            return 0.85  # Big recovery from degraded state
        elif current_confidence < 0.7:
            return min(0.95, current_confidence + 0.2)
        else:
            return min(0.98, current_confidence + 0.05)
    
    def blast_radius(self, children_count: int) -> int:
        return children_count  # Restart affects all dependents
    
    def rollback_risk(self) -> float:
        return 0.08  # Restarts are generally safe
    
    def recovery_time_estimate(self) -> float:
        return 5.0  # ~5 seconds


@dataclass
class RollbackDeployment(TypedAction):
    """Rollback to a previous deployment version."""
    target_version: str = ""
    
    def __post_init__(self):
        self.action_type = ActionType.ROLLBACK
        self.description = f"Rollback {self.service}" + (f" to {self.target_version}" if self.target_version else "")
    
    def simulate_effect(self, current_confidence: float) -> float:
        # Rollback is more aggressive but riskier
        return min(0.95, current_confidence + 0.35)
    
    def blast_radius(self, children_count: int) -> int:
        return children_count + 1  # Rollback affects service + all dependents
    
    def rollback_risk(self) -> float:
        return 0.18  # Rollbacks have higher risk (schema drift, config mismatch)
    
    def recovery_time_estimate(self) -> float:
        return 15.0  # ~15 seconds for rollback


@dataclass
class ScaleReplica(TypedAction):
    """Scale a service (add replicas)."""
    replicas: int = 2
    
    def __post_init__(self):
        self.action_type = ActionType.SCALE
        self.description = f"Scale {self.service} to {self.replicas} replicas"
    
    def simulate_effect(self, current_confidence: float) -> float:
        return min(0.95, current_confidence + 0.15)  # Moderate improvement
    
    def blast_radius(self, children_count: int) -> int:
        return 0  # Scaling doesn't directly affect dependents
    
    def rollback_risk(self) -> float:
        return 0.05  # Scaling is low-risk
    
    def recovery_time_estimate(self) -> float:
        return 10.0


@dataclass  
class DoNothing(TypedAction):
    """Deliberate inaction — let the system stabilize on its own."""
    
    def __post_init__(self):
        self.action_type = ActionType.DO_NOTHING
        self.description = f"Wait and observe {self.service}"
    
    def simulate_effect(self, current_confidence: float) -> float:
        return current_confidence  # No change
    
    def blast_radius(self, children_count: int) -> int:
        return 0
    
    def rollback_risk(self) -> float:
        return 0.0
    
    def recovery_time_estimate(self) -> float:
        return 60.0  # Natural stabilization is slow


@dataclass
class PortRebind(TypedAction):
    """Change port binding (e.g., 127.0.0.1 → 0.0.0.0)."""
    old_binding: str = "127.0.0.1"
    new_binding: str = "0.0.0.0"
    
    def __post_init__(self):
        self.action_type = ActionType.PORT_REBIND
        self.description = f"Rebind {self.service} from {self.old_binding} to {self.new_binding}"
    
    def simulate_effect(self, current_confidence: float) -> float:
        return 0.95  # Port rebinding is highly effective for isolation issues
    
    def blast_radius(self, children_count: int) -> int:
        return 0  # Only affects network visibility, not dependents
    
    def rollback_risk(self) -> float:
        return 0.06
    
    def recovery_time_estimate(self) -> float:
        return 8.0


# ══════════════════════════════════════════════
# E9.2 — COPY-ON-WRITE SNAPSHOT GRAPH
# ══════════════════════════════════════════════

@dataclass
class CoWSnapshot:
    """
    Copy-on-Write snapshot node.
    
    Like git commits or ZFS snapshots: parent + delta.
    NOT deepcopy(state) — that explodes memory under speculative branching.
    
    Lookup: resolve(key) → check delta, then recurse to parent.
    Only changed keys are stored in delta. Unchanged keys reference parent.
    """
    snapshot_id: str
    parent: Optional['CoWSnapshot'] = None
    delta: Dict[str, float] = field(default_factory=dict)  # service → confidence
    timestamp: float = field(default_factory=time.time)
    logical_time: int = 0  # Monotonic event counter (NOT wall-clock)
    action: Optional[TypedAction] = None  # Action that created this snapshot
    
    def resolve(self, service: str) -> float:
        """Resolve confidence for a service. Walk delta → parent chain."""
        if service in self.delta:
            return self.delta[service]
        if self.parent:
            return self.parent.resolve(service)
        return 1.0  # Default: healthy
    
    def fork(self, action: TypedAction, new_confidences: Dict[str, float]) -> 'CoWSnapshot':
        """
        Create a new snapshot as a child of this one.
        Only stores CHANGED confidences in delta.
        """
        delta = {}
        for svc, new_conf in new_confidences.items():
            old_conf = self.resolve(svc)
            if abs(old_conf - new_conf) > 0.001:
                delta[svc] = round(new_conf, 2)
        
        return CoWSnapshot(
            snapshot_id=f"snap-{self.logical_time + 1}",
            parent=self,
            delta=delta,
            logical_time=self.logical_time + 1,
            action=action,
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Materialize full confidence map at this snapshot."""
        result = {}
        # Walk to root first, then apply deltas forward
        if self.parent:
            result = self.parent.to_dict()
        result.update(self.delta)
        return result
    
    def depth(self) -> int:
        """How many snapshots deep from root."""
        return 1 + (self.parent.depth() if self.parent else 0)
    
    def memory_efficiency(self) -> float:
        """Ratio of delta size to full state size."""
        full_size = len(self.to_dict())
        delta_size = len(self.delta)
        return delta_size / max(1, full_size)


# ══════════════════════════════════════════════
# E9.3 — UTILITY ENGINE (Multi-Objective)
# ══════════════════════════════════════════════

@dataclass
class CounterfactualResult:
    """Result of a counterfactual simulation."""
    action: TypedAction
    confidence_gain: float          # Δ effective confidence (system-wide avg)
    blast_radius: int               # Downstream services affected
    rollback_risk: float            # Probability action makes things worse
    contradiction_probability: float # Probability of new contradictions
    recovery_time: float            # Estimated seconds to converge
    topology_instability: float     # Risk of cascading instability
    utility_score: float            # Computed multi-objective utility
    
    # Pre/post snapshots
    pre_confidences: Dict[str, float] = field(default_factory=dict)
    post_confidences: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    simulation_time_ms: float = 0.0
    logical_time: int = 0


class UtilityEngine:
    """
    Multi-objective utility evaluation for counterfactual actions.
    
    NOT: "highest confidence wins"
    BUT:  utility = gain - risk - blast - contradiction - instability
    
    The Policy Engine uses these scores to rank actions.
    The LLM proposes strategies. The Runtime evaluates them.
    """
    
    # Weights (tunable per environment)
    WEIGHT_CONFIDENCE_GAIN = 1.0
    WEIGHT_BLAST_RADIUS = 0.3       # Each affected service costs -0.3
    WEIGHT_ROLLBACK_RISK = 1.5       # Rollback risk is heavily penalized
    WEIGHT_CONTRADICTION_PROB = 0.8
    WEIGHT_RECOVERY_TIME = 0.01     # Per second
    WEIGHT_TOPOLOGY_INSTABILITY = 1.2
    
    def evaluate(
        self,
        action: TypedAction,
        pre_confidences: Dict[str, float],
        post_confidences: Dict[str, float],
        children_count: int,
        simulation_time_ms: float = 0,
    ) -> CounterfactualResult:
        """
        Evaluate a counterfactual action.
        
        Computes multi-objective utility from:
        - Confidence gain (system-wide average)
        - Blast radius (downstream impact)
        - Rollback risk (action-intrinsic)
        - Contradiction probability (from confidence deltas)
        - Recovery time (estimated convergence)
        - Topology instability (variance in confidence changes)
        """
        # Confidence gain
        pre_avg = sum(pre_confidences.values()) / max(1, len(pre_confidences))
        post_avg = sum(post_confidences.values()) / max(1, len(post_confidences))
        gain = post_avg - pre_avg
        
        # Blast radius
        blast = action.blast_radius(children_count)
        
        # Rollback risk
        risk = action.rollback_risk()
        
        # Contradiction probability: based on variance of confidence changes
        deltas = [post_confidences.get(svc, 0) - pre_confidences.get(svc, 0) 
                  for svc in pre_confidences]
        variance = sum(d*d for d in deltas) / max(1, len(deltas))
        contradiction_prob = min(1.0, variance * 2)  # High variance → likely contradictions
        
        # Recovery time
        recovery_time = action.recovery_time_estimate()
        
        # Topology instability: penalize if many services change significantly
        big_changes = sum(1 for d in deltas if abs(d) > 0.2)
        topology_instability = big_changes / max(1, len(deltas))
        
        # Multi-objective utility
        utility = (
            self.WEIGHT_CONFIDENCE_GAIN * gain
            - self.WEIGHT_BLAST_RADIUS * blast
            - self.WEIGHT_ROLLBACK_RISK * risk
            - self.WEIGHT_CONTRADICTION_PROB * contradiction_prob
            - self.WEIGHT_RECOVERY_TIME * recovery_time
            - self.WEIGHT_TOPOLOGY_INSTABILITY * topology_instability
        )
        
        return CounterfactualResult(
            action=action,
            confidence_gain=round(gain, 3),
            blast_radius=blast,
            rollback_risk=round(risk, 2),
            contradiction_probability=round(contradiction_prob, 2),
            recovery_time=recovery_time,
            topology_instability=round(topology_instability, 2),
            utility_score=round(utility, 3),
            pre_confidences=pre_confidences,
            post_confidences=post_confidences,
            simulation_time_ms=round(simulation_time_ms, 1),
        )


# ══════════════════════════════════════════════
# COUNTERFACTUAL SIMULATOR
# ══════════════════════════════════════════════

class CounterfactualSimulator:
    """
    Deterministic counterfactual simulation engine.
    
    For each candidate action:
    1. Fork a CoW snapshot from current state
    2. Apply action's simulated effect to the target service
    3. Propagate confidence changes through dependency graph
    4. Measure delta between pre and post state
    5. Evaluate utility
    
    This is operational Monte Carlo — NOT LLM speculation.
    """
    
    def __init__(self):
        self.utility = UtilityEngine()
        self.simulations_run: int = 0
        self.total_simulation_time_ms: float = 0.0
    
    def simulate(
        self,
        base_snapshot: CoWSnapshot,
        actions: List[TypedAction],
        dependency_graph: Dict[str, List[str]] = None,
    ) -> List[CounterfactualResult]:
        """
        Simulate multiple counterfactual actions against a base snapshot.
        
        Returns ranked results (highest utility first).
        """
        results = []
        
        for action in actions:
            start = time.time()
            
            pre_confidences = base_snapshot.to_dict()
            
            # Simulate action effect on target service
            current_conf = base_snapshot.resolve(action.service)
            new_local = action.simulate_effect(current_conf)
            
            # Propagate through dependencies (simplified incremental)
            post_confidences = self._propagate(
                pre_confidences,
                action.service,
                new_local,
                dependency_graph or {},
            )
            
            # Fork snapshot
            new_snapshot = base_snapshot.fork(action, post_confidences)
            
            # Evaluate
            children_count = len(dependency_graph.get(action.service, []))
            elapsed = (time.time() - start) * 1000
            
            result = self.utility.evaluate(
                action, pre_confidences, post_confidences, children_count, elapsed
            )
            result.pre_confidences = pre_confidences
            result.post_confidences = post_confidences
            result.logical_time = new_snapshot.logical_time
            
            results.append(result)
            
            self.simulations_run += 1
            self.total_simulation_time_ms += elapsed
        
        # Rank by utility (highest first)
        results.sort(key=lambda r: -r.utility_score)
        
        return results
    
    def _propagate(
        self,
        confidences: Dict[str, float],
        changed_service: str,
        new_local: float,
        graph: Dict[str, List[str]],
    ) -> Dict[str, float]:
        """
        Simplified incremental propagation for counterfactual simulation.
        
        Only propagates from the changed service to its transitive dependents.
        Uses 0.8 edge weight and 0.7 damping per hop.
        """
        result = dict(confidences)
        result[changed_service] = round(new_local, 2)
        
        # BFS propagation to children
        visited = {changed_service}
        queue = [(changed_service, new_local, 0)]  # (service, confidence, depth)
        
        while queue:
            svc, conf, depth = queue.pop(0)
            
            for child in graph.get(svc, []):
                if child in visited:
                    continue
                visited.add(child)
                
                # Damping: impact reduces with depth
                damping = 0.7 ** (depth + 1)
                edge_weight = 0.8
                
                child_old = result.get(child, 1.0)
                child_new = child_old * (conf * edge_weight * damping + (1 - damping))
                result[child] = round(child_new, 2)
                
                # Only propagate if significant change
                if abs(child_old - child_new) > 0.01:
                    queue.append((child, child_new, depth + 1))
        
        return result
    
    def compare_strategies(
        self,
        snapshot: CoWSnapshot,
        strategy_sets: Dict[str, List[TypedAction]],
        dependency_graph: Dict[str, List[str]] = None,
    ) -> Dict[str, List[CounterfactualResult]]:
        """
        Compare multiple strategy sets.
        
        Each strategy set is a named list of actions.
        Returns ranked results per strategy.
        """
        results = {}
        for strategy_name, actions in strategy_sets.items():
            results[strategy_name] = self.simulate(snapshot, actions, dependency_graph)
        return results
    
    def stats(self) -> Dict:
        return {
            "simulations_run": self.simulations_run,
            "total_time_ms": round(self.total_simulation_time_ms, 1),
            "avg_time_per_simulation_ms": round(
                self.total_simulation_time_ms / max(1, self.simulations_run), 1
            ),
        }
