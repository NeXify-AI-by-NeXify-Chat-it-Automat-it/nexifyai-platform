"""
NeXifyAI — Causality Graph (Sprint E.3)
Directed Acyclic Graph for operational causality tracing.

Answers:
  Why did confidence drop?
  Which action caused instability?
  Which recovery created contradiction?
  Which dependency propagated the damage?

NOT text-based. DAG-based. Each node is an event. Each edge is causal.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

@dataclass
class CausalNode:
    """A node in the causality graph."""
    event_id: str
    logical_time: int
    actor: str
    event_type: str
    description: str
    confidence_delta: float = 0.0
    
    parents: List[str] = field(default_factory=list)    # Causal parents
    children: List[str] = field(default_factory=list)   # Causal children


class CausalityGraph:
    """
    Operational causality DAG.
    
    Traces root causes, blast lineages, and propagation chains.
    Like git log --graph, but for runtime events.
    """
    
    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.edges: List[tuple] = []  # (parent_event_id, child_event_id, edge_type)
    
    def add_event(
        self,
        event_id: str,
        logical_time: int,
        actor: str,
        event_type: str,
        description: str,
        confidence_delta: float = 0.0,
        causal_parent: str = None,
    ):
        """Add an event to the causality graph."""
        node = CausalNode(
            event_id=event_id,
            logical_time=logical_time,
            actor=actor,
            event_type=event_type,
            description=description,
            confidence_delta=confidence_delta,
        )
        
        if causal_parent and causal_parent in self.nodes:
            node.parents.append(causal_parent)
            self.nodes[causal_parent].children.append(event_id)
        
        self.nodes[event_id] = node
    
    def root_cause(self, event_id: str) -> Optional[CausalNode]:
        """Trace back to find the root cause event."""
        visited = set()
        current = self.nodes.get(event_id)
        
        while current and current.event_id not in visited:
            visited.add(current.event_id)
            if not current.parents:
                return current
            # Follow first parent (primary cause)
            current = self.nodes.get(current.parents[0])
        
        return current
    
    def blast_lineage(self, event_id: str) -> List[str]:
        """
        All events causally downstream from this event.
        BFS from this node through all children.
        """
        if event_id not in self.nodes:
            return []
        
        lineage = []
        visited = {event_id}
        queue = [event_id]
        
        while queue:
            current = queue.pop(0)
            node = self.nodes.get(current)
            if not node:
                continue
            
            if current != event_id:
                lineage.append(current)
            
            for child_id in node.children:
                if child_id not in visited:
                    visited.add(child_id)
                    queue.append(child_id)
        
        return lineage
    
    def propagation_chain(self, event_id: str) -> List[Dict]:
        """
        Full propagation chain from root cause to all affected nodes.
        Returns ordered list with depth and confidence impact.
        """
        root = self.root_cause(event_id)
        if not root:
            return []
        
        chain = []
        visited = {root.event_id}
        queue = [(root.event_id, 0)]  # (event_id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            node = self.nodes.get(current_id)
            if not node:
                continue
            
            chain.append({
                "event_id": current_id,
                "depth": depth,
                "actor": node.actor,
                "type": node.event_type,
                "confidence_delta": node.confidence_delta,
                "description": node.description,
            })
            
            for child_id in node.children:
                if child_id not in visited:
                    visited.add(child_id)
                    queue.append((child_id, depth + 1))
        
        return sorted(chain, key=lambda c: c["depth"])  # Root cause first
    
    def to_ascii(self, start_event: str = None) -> str:
        """ASCII representation of the causality graph."""
        if not self.nodes:
            return "(empty)"
        
        if start_event:
            return self._render_subtree(start_event)
        
        # Find root nodes (no parents)
        roots = [n for n in self.nodes.values() if not n.parents]
        lines = []
        for root in sorted(roots, key=lambda r: r.logical_time):
            lines.append(self._render_subtree(root.event_id))
        return "\n".join(lines)
    
    def _render_subtree(self, event_id: str, indent: int = 0) -> str:
        """Render a subtree as ASCII."""
        node = self.nodes.get(event_id)
        if not node:
            return ""
        
        prefix = "  " * indent + ("├─ " if indent > 0 else "")
        icon = {"confidence_update": "↓", "contradiction": "⚡", "recovery_complete": "♻",
                "observation": "👁", "action_applied": "▶"}.get(node.event_type, "●")
        
        lines = [f"{prefix}{icon} [{node.logical_time}] {node.actor}: {node.description} (Δ={node.confidence_delta:+.2f})"]
        
        for child_id in node.children:
            lines.append(self._render_subtree(child_id, indent + 1))
        
        return "\n".join(lines)
    
    def stats(self) -> Dict:
        roots = [n for n in self.nodes.values() if not n.parents]
        return {
            "total_nodes": len(self.nodes),
            "root_causes": len(roots),
            "max_depth": max(
                (len(self.blast_lineage(n.event_id)) for n in self.nodes.values()),
                default=0
            ),
            "roots": [r.event_id for r in roots],
        }


# ══════════════════════════════════════════════
# POLICY ENGINE (Sprint E.4)
# ══════════════════════════════════════════════

@dataclass
class GovernancePolicy:
    """A policy rule for autonomous action governance."""
    name: str
    max_blast_radius: int = 2
    max_rollback_risk: float = 0.12
    min_utility_score: float = -0.4
    forbidden_actions: List[str] = field(default_factory=list)
    require_human_approval_above_risk: float = 0.15
    cooldown_seconds: int = 300  # Min time between same action


@dataclass
class PolicyDecision:
    """Result of a policy check."""
    allowed: bool
    reason: str
    violating_rules: List[str] = field(default_factory=list)
    requires_human: bool = False


class PolicyEngine:
    """
    Operational governance layer.
    
    Validates actions BEFORE they're applied.
    NOT advisory — BLOCKING.
    """
    
    DEFAULT_POLICY = GovernancePolicy(
        name="default",
        max_blast_radius=2,
        max_rollback_risk=0.12,
        min_utility_score=-0.4,
        forbidden_actions=["rollback_production_without_approval"],
        require_human_approval_above_risk=0.15,
    )
    
    def __init__(self):
        self.policies: Dict[str, GovernancePolicy] = {"default": self.DEFAULT_POLICY}
        self.decisions: List[PolicyDecision] = []
        self._action_history: Dict[str, List[float]] = defaultdict(list)
    
    def check(
        self,
        action_type: str,
        blast_radius: int,
        rollback_risk: float,
        utility_score: float,
        policy_name: str = "default",
    ) -> PolicyDecision:
        """
        Check if an action is allowed under governance policy.
        Returns PolicyDecision with allowed/reason/violations.
        """
        policy = self.policies.get(policy_name, self.DEFAULT_POLICY)
        violations = []
        
        # Check blast radius
        if blast_radius > policy.max_blast_radius:
            violations.append(
                f"Blast radius {blast_radius} exceeds max {policy.max_blast_radius}"
            )
        
        # Check rollback risk
        if rollback_risk > policy.max_rollback_risk:
            violations.append(
                f"Rollback risk {rollback_risk} exceeds max {policy.max_rollback_risk}"
            )
        
        # Check utility threshold
        if utility_score < policy.min_utility_score:
            violations.append(
                f"Utility {utility_score} below minimum {policy.min_utility_score}"
            )
        
        # Check forbidden actions
        if action_type in policy.forbidden_actions:
            violations.append(f"Action '{action_type}' is forbidden")
        
        # Check cooldown
        now = __import__('time').time()
        recent = [t for t in self._action_history.get(action_type, []) 
                  if now - t < policy.cooldown_seconds]
        if recent:
            violations.append(
                f"Action '{action_type}' on cooldown ({len(recent)} executions in {policy.cooldown_seconds}s)"
            )
        
        requires_human = rollback_risk > policy.require_human_approval_above_risk
        
        decision = PolicyDecision(
            allowed=len(violations) == 0,
            reason="Approved" if not violations else f"Rejected: {'; '.join(violations)}",
            violating_rules=violations,
            requires_human=requires_human,
        )
        
        self.decisions.append(decision)
        return decision
    
    def record_action(self, action_type: str):
        """Record that an action was executed (for cooldown tracking)."""
        self._action_history[action_type].append(__import__('time').time())
        # Prune old entries
        self._action_history[action_type] = [
            t for t in self._action_history[action_type]
            if __import__('time').time() - t < 3600
        ]
    
    def stats(self) -> Dict:
        return {
            "policies": len(self.policies),
            "total_decisions": len(self.decisions),
            "rejections": len([d for d in self.decisions if not d.allowed]),
            "acceptance_rate": len([d for d in self.decisions if d.allowed]) / max(1, len(self.decisions)),
        }


# ══════════════════════════════════════════════
# CONTRADICTION ENGINE (Sprint E.6)
# ══════════════════════════════════════════════

@dataclass
class ContradictionFinding:
    """An action that helped A but degraded B."""
    action: str
    source_actor: str
    improved: List[str]  # Services that improved
    degraded: List[str]  # Services that degraded
    instability_increase: float
    severity: str  # "low", "medium", "high"


class ContradictionEngine:
    """
    Detects when actions produce conflicting outcomes.
    
    Example: Restart backend improves backend (+0.2) but 
             degrades traefik (-0.1) and increases topology instability.
             
    This is the epistemic immune system — it flags actions that
    create new problems while solving old ones.
    """
    
    def __init__(self):
        self.findings: List[ContradictionFinding] = []
    
    def analyze(
        self,
        action: str,
        actor: str,
        pre_confidences: Dict[str, float],
        post_confidences: Dict[str, float],
        instability_delta: float = 0.0,
    ) -> Optional[ContradictionFinding]:
        """
        Analyze an action for contradictory outcomes.
        Returns ContradictionFinding if action helped some services but hurt others.
        """
        improved = []
        degraded = []
        
        for svc in set(pre_confidences.keys()) | set(post_confidences.keys()):
            pre = pre_confidences.get(svc, 1.0)
            post = post_confidences.get(svc, 1.0)
            delta = post - pre
            
            if delta > 0.02:
                improved.append(f"{svc} ({delta:+.2f})")
            elif delta < -0.02:
                degraded.append(f"{svc} ({delta:+.2f})")
        
        # Contradiction: action helped some, degraded others
        if improved and degraded:
            severity = "high" if len(degraded) >= 2 else "medium" if len(degraded) >= 1 else "low"
            
            finding = ContradictionFinding(
                action=action,
                source_actor=actor,
                improved=improved,
                degraded=degraded,
                instability_increase=round(instability_delta, 2),
                severity=severity,
            )
            
            self.findings.append(finding)
            return finding
        
        return None
    
    def stats(self) -> Dict:
        return {
            "total_findings": len(self.findings),
            "high_severity": len([f for f in self.findings if f.severity == "high"]),
            "recent": [
                {"action": f.action, "improved": len(f.improved), "degraded": len(f.degraded), "severity": f.severity}
                for f in self.findings[-5:]
            ],
        }


# ══════════════════════════════════════════════
# RUNTIME METRICS (Sprint E.7)
# ══════════════════════════════════════════════

@dataclass
class RuntimeMetrics:
    """Operational observability for the actor system."""
    
    @staticmethod
    def collect(actor_system=None, ledger=None,
                policy_engine=None,
                contradiction_engine=None) -> Dict:
        """Collect all runtime metrics."""
        metrics = {
            "timestamp": __import__('time').time(),
        }
        
        # Actor system metrics
        if actor_system:
            try:
                stats = actor_system.system_stats()
                metrics["actors"] = {
                    "total": stats.get("total_actors", 0),
                    "active": stats.get("active_actors", 0),
                    "total_messages": stats.get("total_messages", 0),
                }
                # Mailbox depths
                if "actors" in stats:
                    depths = [a.get("mailbox_size", 0) for a in stats["actors"].values()]
                    metrics["actors"]["mailbox_depth_avg"] = round(sum(depths) / max(1, len(depths)), 1)
                    metrics["actors"]["mailbox_depth_max"] = max(depths) if depths else 0
            except Exception:
                metrics["actors"] = {"error": "Actor system not available"}
        
        # Ledger metrics
        if ledger:
            metrics["ledger"] = ledger.stats()
        
        # Policy metrics
        if policy_engine:
            metrics["policy"] = policy_engine.stats()
        
        # Contradiction metrics
        if contradiction_engine:
            metrics["contradictions"] = contradiction_engine.stats()
        
        return metrics
    
    @staticmethod
    def health_summary(metrics: Dict) -> str:
        """Human-readable health summary."""
        actors = metrics.get("actors", {})
        ledger = metrics.get("ledger", {})
        policy = metrics.get("policy", {})
        contradictions = metrics.get("contradictions", {})
        
        lines = [
            "═══ RUNTIME HEALTH ═══",
            f"Actors: {actors.get('total', '?')} total, {actors.get('active', '?')} active, {actors.get('total_messages', '?')} msgs",
            f"Mailbox: avg={actors.get('mailbox_depth_avg', '?')}, max={actors.get('mailbox_depth_max', '?')}",
            f"Ledger: {ledger.get('total_events', '?')} events, logical_time={ledger.get('logical_clock', '?')}",
            f"Policy: {policy.get('acceptance_rate', 1.0):.0%} acceptance ({policy.get('rejections', 0)} rejections)",
            f"Contradictions: {contradictions.get('total_findings', 0)} total, {contradictions.get('high_severity', 0)} high",
        ]
        return "\n".join(lines)
