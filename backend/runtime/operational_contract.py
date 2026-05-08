"""
NeXifyAI — Operational Contract (E3.5)
Sub-Agent Inheritance — enforced operational doctrine.

Every agent MUST inherit this contract. No agent may override.
No agent may emit "SUCCESS" without validation.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationRequirement(Enum):
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


@dataclass
class OperationalContract:
    """
    Binding operational contract for ALL agents.
    
    Inherited by: ArchitectAgent, SecurityAgent, FinOpsAgent, QAAgent,
    DocsAgent, RetrievalAgent, ComplianceAgent, RefactorAgent,
    and any future agent.
    
    These fields are NOT configurable per agent. They are system-wide.
    """
    
    # ══════════════════════════════════════════
    # MANDATORY VALIDATION (never skippable)
    # ══════════════════════════════════════════
    
    mandatory_validation: bool = True
    """Every mutation must be validated post-execution."""
    
    mandatory_reobservation: bool = True
    """After any state change, re-observe from ALL observer positions."""
    
    mandatory_convergence: bool = True
    """Recovery is only complete when all observers converge."""
    
    forbid_unverified_success: bool = True
    """Never emit 'SUCCESS' without multi-observer validation."""
    
    forbid_single_observer_trust: bool = True
    """A single observer's report is NEVER canonical truth."""
    
    require_contradiction_delta: bool = True
    """Must report contradiction count before and after action."""
    
    require_confidence_recomputation: bool = True
    """Must recompute confidence scores after any mutation."""
    
    # ══════════════════════════════════════════
    # TEMPORAL CONSTRAINTS
    # ══════════════════════════════════════════
    
    max_staleness_seconds: int = 3600
    """State older than 1 hour is stale and must be re-probed."""
    
    confidence_decay_rate: float = 0.95
    """Confidence multiplier per hour without re-observation."""
    
    stabilization_wait_seconds: int = 3
    """Minimum wait time after mutation before re-observation."""
    
    # ══════════════════════════════════════════
    # EPISTEMIC RULES (how to know truth)
    # ══════════════════════════════════════════
    
    canonical_sources: List[str] = None
    """Ordered list of canonical truth sources."""
    
    def __post_init__(self):
        if self.canonical_sources is None:
            self.canonical_sources = [
                "systemctl is-active",     # Systemd truth
                "docker ps --filter",      # Docker truth
                "tcp://direct:port",       # Network truth
                "curl -sf endpoint",       # HTTP truth
            ]
    
    # ══════════════════════════════════════════
    # VIOLATION DETECTION
    # ══════════════════════════════════════════
    
    def validate_agent_result(self, result: Dict[str, Any]) -> List[str]:
        """
        Validate an agent's result against this contract.
        Returns list of violations (empty = compliant).
        """
        violations = []
        
        if self.forbid_unverified_success:
            if result.get("status") == "success":
                if not result.get("validation"):
                    violations.append("Agent reported SUCCESS without validation evidence")
                if not result.get("multi_observer_check"):
                    violations.append("Agent reported SUCCESS without multi-observer check")
        
        if self.require_contradiction_delta:
            if "contradictions_before" not in result or "contradictions_after" not in result:
                violations.append("Agent did not report contradiction delta")
        
        if self.require_confidence_recomputation:
            if result.get("confidence") is None and result.get("status") == "success":
                violations.append("Agent reported SUCCESS without confidence recomputation")
        
        return violations
    
    def is_compliant(self, result: Dict[str, Any]) -> bool:
        """Check if an agent result complies with this contract."""
        return len(self.validate_agent_result(result)) == 0


# ══════════════════════════════════════════════
# GLOBAL CONTRACT (all agents inherit this)
# ══════════════════════════════════════════════

GLOBAL_OPERATIONAL_CONTRACT = OperationalContract()


def enforce_contract(result: Dict[str, Any]) -> None:
    """
    Enforce the operational contract on an agent result.
    Raises OperationalContractViolation if non-compliant.
    """
    violations = GLOBAL_OPERATIONAL_CONTRACT.validate_agent_result(result)
    if violations:
        raise OperationalContractViolation(violations)


class OperationalContractViolation(Exception):
    """Raised when an agent violates the operational contract."""
    def __init__(self, violations: List[str]):
        self.violations = violations
        super().__init__(f"Operational Contract violated: {'; '.join(violations)}")
