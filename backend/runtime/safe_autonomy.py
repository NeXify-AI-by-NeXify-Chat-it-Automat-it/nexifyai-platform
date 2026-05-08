"""
NeXifyAI — Safe Bounded Autonomy (R5)
Deterministically governed operational autonomy.

Three hard protection layers:
  1. Capability Bounding: explicit tokens with scope, blast radius limits, expiry
  2. Simulation-before-Execution: E9 is never optional
  3. Epistemic Uncertainty Tracking: evidence_strength, causal_confidence, observability_coverage

Principle: NOT "self-healing AI" — BUT "deterministically governed operational autonomy"
  - Replayable AI operations
  - Causally traceable infrastructure decisions
  - Auditable autonomous recovery
  - Epistemically weighted runtime governance

Execution pipeline:
  LLM proposal → counterfactual simulation → policy validation
  → contradiction scan → confidence threshold → capability check
  → human gate (if required) → execution → re-observation → ledger
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from datetime import datetime, timezone


# ══════════════════════════════════════════════
# R5.1 — CAPABILITY BOUNDING
# ══════════════════════════════════════════════

class CapabilityScope(Enum):
    SERVICE = "service"           # Single service only
    DEPENDENCY_GROUP = "group"    # Service + direct dependents
    INFRASTRUCTURE = "infra"      # Wider infrastructure
    GLOBAL = "global"             # Everything (requires human)


@dataclass
class CapabilityToken:
    """
    Explicit permission to perform an action.
    
    No runtime component has implicit rights.
    Every action requires a valid, non-expired token.
    """
    token_id: str
    action_type: str               # "restart", "rollback", "scale", "port_rebind"
    scope: CapabilityScope
    allowed_services: List[str]    # Specific services this token applies to
    max_blast_radius: int = 1      # Maximum downstream services affected
    max_rollback_risk: float = 0.10
    requires_human: bool = False
    issuer: str = "system"
    issued_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1h default
    max_uses: int = 10
    uses: int = 0
    
    @property
    def is_valid(self) -> bool:
        return (
            time.time() < self.expires_at
            and self.uses < self.max_uses
        )
    
    def authorize(self, service: str, blast_radius: int, rollback_risk: float) -> bool:
        """Check if this token authorizes a specific action."""
        if not self.is_valid:
            return False
        if service not in self.allowed_services and "*" not in self.allowed_services:
            return False
        if blast_radius > self.max_blast_radius:
            return False
        if rollback_risk > self.max_rollback_risk:
            return False
        self.uses += 1
        return True


class CapabilityRegistry:
    """
    Central capability authority.
    
    Issues, validates, and expires tokens.
    No action can be executed without a valid token.
    """
    
    def __init__(self):
        self.tokens: Dict[str, CapabilityToken] = {}
        self.denials: List[Dict] = []
    
    def issue(
        self,
        action_type: str,
        allowed_services: List[str],
        max_blast_radius: int = 1,
        max_rollback_risk: float = 0.10,
        scope: CapabilityScope = CapabilityScope.SERVICE,
        requires_human: bool = False,
        ttl_seconds: int = 3600,
    ) -> CapabilityToken:
        """Issue a new capability token."""
        token = CapabilityToken(
            token_id=f"cap-{len(self.tokens):04d}",
            action_type=action_type,
            scope=scope,
            allowed_services=allowed_services,
            max_blast_radius=max_blast_radius,
            max_rollback_risk=max_rollback_risk,
            requires_human=requires_human,
            expires_at=time.time() + ttl_seconds,
        )
        self.tokens[token.token_id] = token
        return token
    
    def validate(
        self, action_type: str, service: str, blast_radius: int, rollback_risk: float
    ) -> Tuple[bool, str, Optional[CapabilityToken]]:
        """
        Validate an action against all active tokens.
        Returns (authorized, reason, token).
        """
        for token in self.tokens.values():
            if token.action_type == action_type and token.authorize(service, blast_radius, rollback_risk):
                if token.requires_human:
                    return False, "Human approval required", token
                return True, "Authorized", token
        
        reason = f"No valid token for {action_type} on {service} (blast={blast_radius}, risk={rollback_risk})"
        self.denials.append({
            "action_type": action_type, "service": service,
            "blast_radius": blast_radius, "rollback_risk": rollback_risk,
            "timestamp": time.time(), "reason": reason,
        })
        return False, reason, None
    
    def expire_stale(self):
        """Remove expired tokens."""
        self.tokens = {k: v for k, v in self.tokens.items() if v.is_valid}
    
    def stats(self) -> Dict:
        self.expire_stale()
        return {
            "active_tokens": len(self.tokens),
            "total_denials": len(self.denials),
            "tokens": [
                {"id": t.token_id, "action": t.action_type, "services": t.allowed_services,
                 "blast": t.max_blast_radius, "uses": f"{t.uses}/{t.max_uses}",
                 "expires": round(t.expires_at - time.time())}
                for t in self.tokens.values()
            ],
        }


# ══════════════════════════════════════════════
# R5.2 — SIMULATION-BEFORE-EXECUTION GATE
# ══════════════════════════════════════════════

class GateResult(Enum):
    APPROVED = "approved"
    REQUIRES_HUMAN = "requires_human"
    REJECTED_POLICY = "rejected_policy"
    REJECTED_CONTRADICTION = "rejected_contradiction"
    REJECTED_CONFIDENCE = "rejected_confidence"
    REJECTED_CAPABILITY = "rejected_capability"
    REJECTED_UNCERTAINTY = "rejected_uncertainty"


@dataclass
class ExecutionGate:
    """
    The E9-enforced gate. Simulation is NEVER optional.
    
    Pipeline:
      LLM proposal → counterfactual simulation → policy validation
      → contradiction scan → confidence threshold → capability check
      → human gate (if required) → EXECUTE → re-observation → ledger
    """
    
    proposal: str                           # What the LLM proposed
    action_type: str                        # Typed action
    service: str
    
    # Simulation results (from E9 CounterfactualSimulator)
    confidence_gain: float = 0.0
    blast_radius: int = 0
    rollback_risk: float = 0.0
    contradiction_probability: float = 0.0
    utility_score: float = 0.0
    topology_instability: float = 0.0
    
    # Policy check
    policy_allowed: bool = True
    policy_reason: str = ""
    
    # Contradiction check
    contradiction_severity: str = "none"
    contradiction_improved: int = 0
    contradiction_degraded: int = 0
    
    # Capability check
    capability_allowed: bool = False
    capability_reason: str = ""
    
    # Confidence threshold
    min_confidence_threshold: float = 0.15
    confidence_met: bool = False
    
    # Uncertainty
    uncertainty_score: float = 0.0
    uncertainty_acceptable: bool = True
    
    # Human gate
    requires_human: bool = False
    human_approved: bool = False
    
    # Result
    result: GateResult = GateResult.APPROVED
    executed: bool = False
    execution_logical_time: int = 0
    
    def evaluate(self) -> GateResult:
        """Run the full gate pipeline. Returns the gate decision."""
        # 1. Policy check
        if not self.policy_allowed:
            self.result = GateResult.REJECTED_POLICY
            return self.result
        
        # 2. Contradiction check
        if self.contradiction_severity == "high" and self.contradiction_degraded >= 2:
            self.result = GateResult.REJECTED_CONTRADICTION
            return self.result
        
        # 3. Confidence threshold
        if not self.confidence_met:
            self.result = GateResult.REJECTED_CONFIDENCE
            return self.result
        
        # 4. Capability check
        if not self.capability_allowed:
            self.result = GateResult.REJECTED_CAPABILITY
            return self.result
        
        # 5. Uncertainty check
        if not self.uncertainty_acceptable:
            self.result = GateResult.REJECTED_UNCERTAINTY
            return self.result
        
        # 6. Human gate (if required)
        if self.requires_human and not self.human_approved:
            self.result = GateResult.REQUIRES_HUMAN
            return self.result
        
        self.result = GateResult.APPROVED
        return self.result
    
    def to_audit_record(self) -> Dict:
        """Full audit trail of the gate decision."""
        return {
            "proposal": self.proposal,
            "action": self.action_type,
            "service": self.service,
            "result": self.result.value,
            "simulation": {
                "gain": self.confidence_gain,
                "blast": self.blast_radius,
                "risk": self.rollback_risk,
                "utility": self.utility_score,
            },
            "checks": {
                "policy": self.policy_allowed,
                "contradiction": self.contradiction_severity,
                "confidence": self.confidence_met,
                "capability": self.capability_allowed,
                "uncertainty": self.uncertainty_acceptable,
                "human": self.human_approved if self.requires_human else "not_required",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class AutonomousExecutionGate:
    """
    Central gate controller for autonomous execution.
    
    Every autonomous action MUST pass through this gate.
    E9 simulation is NEVER optional.
    """
    
    def __init__(self, capabilities: CapabilityRegistry):
        self.capabilities = capabilities
        self.gate_history: List[ExecutionGate] = []
    
    def propose(
        self,
        proposal: str,
        action_type: str,
        service: str,
        confidence_gain: float,
        blast_radius: int,
        rollback_risk: float,
        utility_score: float = 0.0,
        contradiction_severity: str = "none",
        contradiction_improved: int = 0,
        contradiction_degraded: int = 0,
        topology_instability: float = 0.0,
        uncertainty_score: float = 0.0,
    ) -> ExecutionGate:
        """
        Propose an autonomous action.
        Returns the gate decision.
        """
        gate = ExecutionGate(
            proposal=proposal,
            action_type=action_type,
            service=service,
            confidence_gain=confidence_gain,
            blast_radius=blast_radius,
            rollback_risk=rollback_risk,
            utility_score=utility_score,
            contradiction_severity=contradiction_severity,
            contradiction_improved=contradiction_improved,
            contradiction_degraded=contradiction_degraded,
            topology_instability=topology_instability,
            uncertainty_score=uncertainty_score,
        )
        
        # Policy check
        from backend.runtime.runtime_governance import PolicyEngine
        policy = PolicyEngine()
        dec = policy.check(action_type, blast_radius, rollback_risk, utility_score)
        gate.policy_allowed = dec.allowed
        gate.policy_reason = dec.reason
        gate.requires_human = dec.requires_human
        
        # Contradiction check
        if contradiction_degraded >= 2:
            gate.contradiction_severity = "high"
        
        # Confidence threshold
        gate.confidence_met = utility_score > gate.min_confidence_threshold
        
        # Capability check
        allowed, reason, _ = self.capabilities.validate(
            action_type, service, blast_radius, rollback_risk
        )
        gate.capability_allowed = allowed
        gate.capability_reason = reason
        
        # Uncertainty check
        gate.uncertainty_acceptable = uncertainty_score < 0.6  # Below 60% uncertainty = acceptable
        
        # Evaluate
        gate.evaluate()
        self.gate_history.append(gate)
        
        return gate
    
    def stats(self) -> Dict:
        return {
            "total_proposals": len(self.gate_history),
            "approved": len([g for g in self.gate_history if g.result == GateResult.APPROVED]),
            "rejected": len([g for g in self.gate_history if g.result.value.startswith("rejected")]),
            "requires_human": len([g for g in self.gate_history if g.result == GateResult.REQUIRES_HUMAN]),
            "approval_rate": len([g for g in self.gate_history if g.result == GateResult.APPROVED]) / max(1, len(self.gate_history)),
        }


# ══════════════════════════════════════════════
# R5.3 — EPISTEMIC UNCERTAINTY TRACKING
# ══════════════════════════════════════════════

@dataclass
class UncertaintyProfile:
    """
    Epistemic uncertainty for an action or state.
    
    Goes beyond simple confidence to track:
    - How strong is the evidence?
    - How causally certain are we?
    - How well can we observe this?
    """
    service: str
    confidence: float                     # Standard confidence (0-1)
    uncertainty_score: float = 0.0        # How uncertain are we? (0=certain, 1=total guess)
    evidence_strength: float = 0.5        # How much evidence supports this? (0=none, 1=overwhelming)
    causal_confidence: float = 0.5        # How confident in the causal chain? (0=correlation, 1=causation)
    observability_coverage: float = 0.5   # How much of the system can we observe? (0=blind, 1=full)
    
    # Derived
    hallucination_risk: float = 0.0       # Risk of hallucinated state (0=safe, 1=certain hallucination)
    
    def __post_init__(self):
        self._recompute()
    
    def _recompute(self):
        """Recompute derived uncertainty metrics."""
        # Uncertainty: inverse of confidence, weighted by evidence weakness
        self.uncertainty_score = round((1 - self.confidence) * (1 - self.evidence_strength * 0.5), 2)
        
        # Hallucination risk: high confidence + low evidence + low observability
        self.hallucination_risk = round(
            self.confidence * (1 - self.evidence_strength) * (1 - self.observability_coverage), 2
        )
    
    def is_safe_for_autonomy(self) -> bool:
        """Is this uncertainty profile safe for autonomous action?"""
        return (
            self.uncertainty_score < 0.5
            and self.hallucination_risk < 0.3
            and self.evidence_strength > 0.4
        )
    
    def to_dict(self) -> Dict:
        return {
            "confidence": self.confidence,
            "uncertainty": self.uncertainty_score,
            "evidence_strength": self.evidence_strength,
            "causal_confidence": self.causal_confidence,
            "observability_coverage": self.observability_coverage,
            "hallucination_risk": self.hallucination_risk,
            "safe_for_autonomy": self.is_safe_for_autonomy(),
        }
