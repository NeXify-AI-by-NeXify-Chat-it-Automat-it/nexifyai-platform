"""
NeXifyAI — Governance Kernel (Package: governance_kernel)

NOT: AI agent with guardrails
BUT:  independent governance layer that gates ALL operations

Pre-execution: capability check → risk assess → blast radius → approve/deny
Post-execution: record → reconcile → compensate → audit

This is the CORE DIFFERENTIATOR of the AI Fabrik.
Most AI systems have 0 governance. NeXifyAI has this kernel.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import uuid


# ═══════════════════════════════════════════════════
# GOVERNANCE TYPES
# ═══════════════════════════════════════════════════

class ApprovalStatus(Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    ESCALATED = "escalated"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class CapabilityToken:
    """A scoped capability granted to an agent or skill."""
    name: str                              # "github.write", "vercel.deploy"
    scope: str = "*"                       # "repo:nexifyai-dev/*", "project:frontend"
    granted_at: float = field(default_factory=time.time)
    expires_at: float = 0.0                # 0 = never
    grantor: str = ""                      # Who granted this
    revoked: bool = False

@dataclass
class GovernanceDecision:
    """Result of a governance check."""
    decision_id: str = field(default_factory=lambda: f"gov_{uuid.uuid4().hex[:12]}")
    status: ApprovalStatus = ApprovalStatus.PENDING
    reason: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    blast_radius: int = 0
    required_capabilities: List[str] = field(default_factory=list)
    missing_capabilities: List[str] = field(default_factory=list)
    policy_violations: List[str] = field(default_factory=list)
    decided_at: float = field(default_factory=time.time)
    decided_by: str = ""
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


# ═══════════════════════════════════════════════════
# GOVERNANCE KERNEL
# ═══════════════════════════════════════════════════

class GovernanceKernel:
    """
    Central governance enforcement layer.

    Every operation flows through:
      check_capabilities() → assess_risk() → check_blast_radius() → decide()

    This is NOT AI. This is deterministic policy enforcement.
    """

    def __init__(self):
        self.capabilities: Dict[str, CapabilityToken] = {}
        self._policies: List[Callable] = []
        self._register_default_capabilities()
        self._register_default_policies()

    def _register_default_capabilities(self):
        """Register standard capability tokens."""
        defaults = [
            CapabilityToken("github.read", "*"),
            CapabilityToken("github.write", "repo:nexifyai-dev/*"),
            CapabilityToken("vercel.read", "project:frontend"),
            CapabilityToken("vercel.write", "project:frontend"),
            CapabilityToken("supabase.read", "database:*"),
            CapabilityToken("supabase.write", "database:*"),
            CapabilityToken("browser.read", "*"),
            CapabilityToken("browser.write", "*"),
            CapabilityToken("slack.write", "channel:#operations"),
        ]
        for cap in defaults:
            self.capabilities[cap.name] = cap

    def _register_default_policies(self):
        """Register mandatory policies."""
        # Policy 1: No Stripe
        self._policies.append(lambda ctx: (
            "stripe" not in str(ctx.get("tags", [])).lower(),
            "Stripe reference detected — use Revolut instead"
        ))
        # Policy 2: No GPL/AGPL/SSPL
        self._policies.append(lambda ctx: (
            not any(lic in str(ctx.get("dependencies", [])).lower()
                   for lic in ["gpl", "agpl", "sspl"]),
            "GPL/AGPL/SSPL license detected"
        ))
        # Policy 3: RLS required for Supabase
        self._policies.append(lambda ctx: (
            ctx.get("connector") != "supabase"
            or ctx.get("has_rls", False)
            or ctx.get("risk_level", "LOW") == "LOW",
            "Supabase write without RLS policy"
        ))
        # Policy 4: Blast radius cap
        self._policies.append(lambda ctx: (
            ctx.get("blast_radius", 0) <= 3,
            "Blast radius exceeds maximum (3)"
        ))

    def check_capabilities(self, required: List[str],
                           granted: List[str]) -> GovernanceDecision:
        """Check if all required capabilities are granted."""
        decision = GovernanceDecision()
        decision.required_capabilities = required

        for cap_name in required:
            if cap_name not in granted:
                decision.missing_capabilities.append(cap_name)

        if decision.missing_capabilities:
            decision.status = ApprovalStatus.DENIED
            decision.reason = f"Missing capabilities: {decision.missing_capabilities}"
        else:
            decision.status = ApprovalStatus.AUTO_APPROVED

        return decision

    def assess_risk(self, skill_risk: RiskLevel,
                    context: Dict[str, Any]) -> GovernanceDecision:
        """Assess operational risk."""
        decision = GovernanceDecision()
        decision.risk_level = skill_risk

        # Run all policies
        for policy_fn in self._policies:
            passed, reason = policy_fn(context)
            if not passed:
                decision.policy_violations.append(reason)

        if decision.policy_violations:
            if skill_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                decision.status = ApprovalStatus.DENIED
            else:
                decision.status = ApprovalStatus.ESCALATED
            decision.reason = "; ".join(decision.policy_violations)
        else:
            if skill_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                decision.status = ApprovalStatus.PENDING  # Needs human
            else:
                decision.status = ApprovalStatus.AUTO_APPROVED

        return decision

    def check_blast_radius(self, blast_radius: int,
                           max_allowed: int = 3) -> GovernanceDecision:
        """Check blast radius constraints."""
        decision = GovernanceDecision()
        decision.blast_radius = blast_radius

        if blast_radius > max_allowed:
            decision.status = ApprovalStatus.DENIED
            decision.reason = f"Blast radius {blast_radius} exceeds max {max_allowed}"
        else:
            decision.status = ApprovalStatus.AUTO_APPROVED

        return decision

    def govern(self, skill_id: str, risk_level: RiskLevel,
               required_caps: List[str], granted_caps: List[str],
               blast_radius: int, context: Dict[str, Any] = None) -> GovernanceDecision:
        """
        Full governance pipeline.

        1. Capability check
        2. Risk assessment (policy enforcement)
        3. Blast radius check
        4. Final decision
        """
        context = context or {}

        # 1. Capabilities
        cap_decision = self.check_capabilities(required_caps, granted_caps)
        if cap_decision.status == ApprovalStatus.DENIED:
            return cap_decision

        # 2. Risk
        risk_decision = self.assess_risk(risk_level, context)
        if risk_decision.status == ApprovalStatus.DENIED:
            return risk_decision

        # 3. Blast radius
        blast_decision = self.check_blast_radius(blast_radius)
        if blast_decision.status == ApprovalStatus.DENIED:
            return blast_decision

        # 4. Final — requires human approval for HIGH/CRITICAL
        final = GovernanceDecision(
            status=ApprovalStatus.PENDING if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
                   else ApprovalStatus.APPROVED,
            risk_level=risk_level,
            blast_radius=blast_radius,
            required_capabilities=required_caps,
            reason="All checks passed" if risk_level not in (RiskLevel.HIGH, RiskLevel.CRITICAL)
                   else "Requires human approval (HIGH/CRITICAL risk)",
        )
        return final


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_kernel: Optional[GovernanceKernel] = None

def get_kernel() -> GovernanceKernel:
    global _kernel
    if _kernel is None:
        _kernel = GovernanceKernel()
    return _kernel
