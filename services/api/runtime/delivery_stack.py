"""
NeXifyAI — Hyperscale Delivery Stack (R8)
Production-grade autonomous software delivery infrastructure.

R8.1: Tool Fabric — standardized tool runtime (Vercel AI SDK + MCP compatible)
R8.2: Deployment Graph — Preview→Canary→Partial→Full→Observe→Rollback
R8.3: Economic Governance — cost, ROI, execution economics
R8.4: Human Collaboration — approvals, comments, override, audit exports

Principle: NOT "more intelligence" — BUT "integrate existing hyperscaling infra".
          The governance layer (R5) is strong enough for production delivery now.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


# ══════════════════════════════════════════════
# R8.1 — TOOL FABRIC (Vercel AI SDK / MCP compatible)
# ══════════════════════════════════════════════

class ToolProtocol(Enum):
    """Tool protocol: MCP standard or custom."""
    MCP = "mcp"
    VERCEL_AI_SDK = "vercel_ai_sdk"
    OPENAI_FUNCTION = "openai_function"
    CUSTOM = "custom"


@dataclass
class ToolSchema:
    """Standardized tool definition — compatible with Vercel AI SDK + MCP + OpenAI function calling."""
    name: str                          # "github.create_pr", "vercel.deploy"
    description: str
    protocol: ToolProtocol = ToolProtocol.CUSTOM
    
    # JSON Schema for parameters (OpenAI/MCP/Vercel compatible)
    parameters_schema: Dict = field(default_factory=dict)
    
    # Execution
    handler: str = ""                  # Registered function name
    capability_required: str = ""      # Capability token type needed
    risk_level: float = 0.0            # 0.0-1.0
    default_timeout_seconds: int = 120
    default_retry_count: int = 2
    
    # Rollback
    rollback_tool: str = ""
    rollback_parameters_schema: Dict = field(default_factory=dict)
    
    # Rate limiting
    max_invocations_per_minute: int = 30
    max_invocations_per_hour: int = 500
    
    # Vercel AI SDK specific
    ai_sdk_config: Dict = field(default_factory=dict)  # streaming, temperature, etc.


class ToolFabric:
    """
    Unified tool registry with MCP/Vercel-AI-SDK/OpenAI compatibility.
    
    Every tool is defined once with a schema, and automatically exposed
    in all supported protocols.
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolSchema] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register the standard delivery tool set."""
        defaults = [
            ToolSchema("github.create_pr", "Create a GitHub Pull Request",
                protocol=ToolProtocol.MCP, capability_required="github.write", risk_level=0.05,
                parameters_schema={"type": "object", "properties": {
                    "title": {"type": "string"}, "branch": {"type": "string"},
                    "body": {"type": "string"}}, "required": ["title", "branch"]},
                rollback_tool="github.close_pr"),
            
            ToolSchema("github.merge_pr", "Merge a Pull Request",
                protocol=ToolProtocol.MCP, capability_required="github.write", risk_level=0.10,
                parameters_schema={"type": "object", "properties": {
                    "pr_number": {"type": "integer"}, "merge_method": {"type": "string", "enum": ["merge", "squash", "rebase"]}},
                    "required": ["pr_number"]},
                rollback_tool="github.revert_merge"),
            
            ToolSchema("vercel.deploy", "Deploy to Vercel",
                protocol=ToolProtocol.VERCEL_AI_SDK, capability_required="vercel.write", risk_level=0.12,
                parameters_schema={"type": "object", "properties": {
                    "project": {"type": "string"}, "environment": {"type": "string", "enum": ["preview", "production"]},
                    "commit_sha": {"type": "string"}}, "required": ["project"]},
                rollback_tool="vercel.rollback", default_timeout_seconds=300,
                ai_sdk_config={"streaming": True, "max_tokens": 1000}),
            
            ToolSchema("browser.test", "Run Playwright browser test",
                protocol=ToolProtocol.MCP, capability_required="browser.execute", risk_level=0.03,
                parameters_schema={"type": "object", "properties": {
                    "url": {"type": "string"}, "test_script": {"type": "string"}}, "required": ["url"]},
                max_invocations_per_minute=10, max_invocations_per_hour=100),
            
            ToolSchema("browser.screenshot", "Take a page screenshot",
                protocol=ToolProtocol.MCP, capability_required="browser.execute", risk_level=0.01,
                parameters_schema={"type": "object", "properties": {
                    "url": {"type": "string"}, "full_page": {"type": "boolean"}}, "required": ["url"]}),
            
            ToolSchema("supabase.migrate", "Run database migration",
                protocol=ToolProtocol.MCP, capability_required="database.write", risk_level=0.15,
                parameters_schema={"type": "object", "properties": {
                    "migration_file": {"type": "string"}}, "required": ["migration_file"]},
                rollback_tool="supabase.rollback_migration", default_timeout_seconds=600),
            
            ToolSchema("slack.notify", "Send Slack notification",
                protocol=ToolProtocol.MCP, capability_required="slack.write", risk_level=0.01,
                parameters_schema={"type": "object", "properties": {
                    "channel": {"type": "string"}, "message": {"type": "string"}}, "required": ["channel", "message"]}),
            
            ToolSchema("email.send", "Send email via Resend",
                protocol=ToolProtocol.CUSTOM, capability_required="email.send", risk_level=0.02,
                parameters_schema={"type": "object", "properties": {
                    "to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                    "required": ["to", "subject"]}),
        ]
        
        for tool in defaults:
            self.register(tool)
    
    def register(self, tool: ToolSchema):
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolSchema]:
        return self.tools.get(name)
    
    def list_for_protocol(self, protocol: ToolProtocol) -> List[ToolSchema]:
        return [t for t in self.tools.values() if t.protocol == protocol]
    
    def to_mcp_manifest(self) -> Dict:
        """Generate MCP server manifest."""
        return {
            "protocol": "mcp",
            "version": "1.0",
            "tools": {
                name: {
                    "description": t.description,
                    "inputSchema": t.parameters_schema,
                }
                for name, t in self.tools.items()
                if t.protocol in (ToolProtocol.MCP, ToolProtocol.CUSTOM)
            }
        }
    
    def to_vercel_ai_sdk_tools(self) -> List[Dict]:
        """Generate Vercel AI SDK tool definitions."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters_schema,
                **t.ai_sdk_config,
            }
            for t in self.tools.values()
            if t.protocol in (ToolProtocol.VERCEL_AI_SDK, ToolProtocol.CUSTOM)
        ]
    
    def stats(self) -> Dict:
        return {
            "total_tools": len(self.tools),
            "by_protocol": {p.value: len(self.list_for_protocol(p)) for p in ToolProtocol},
            "highest_risk": max((t for t in self.tools.values()), key=lambda t: t.risk_level).name,
        }


# ══════════════════════════════════════════════
# R8.3 — DEPLOYMENT GRAPH
# ══════════════════════════════════════════════

class DeployStage(Enum):
    PREVIEW = "preview"
    CANARY = "canary"
    PARTIAL = "partial"
    FULL = "full"
    OBSERVE = "observe"
    ROLLBACK = "rollback"
    COMPLETE = "complete"


@dataclass
class DeployStep:
    """One step in a deployment graph."""
    stage: DeployStage
    tool: str                          # Tool to execute
    parameters: Dict = field(default_factory=dict)
    health_check_url: str = ""         # URL to validate after this step
    health_check_attempts: int = 3
    stabilization_seconds: int = 10
    auto_advance: bool = True          # Auto-advance on success?
    requires_approval: bool = False    # Human approval needed?
    
    # State
    completed: bool = False
    success: bool = False
    started_at: float = 0.0
    duration_ms: float = 0.0


@dataclass
class DeploymentGraph:
    """
    Full deployment pipeline: Preview→Canary→Partial→Full→Observe→Rollback.
    
    Like Vercel's deployment model but with governance hooks
    and artifact lineage at every stage.
    """
    deploy_id: str
    project: str
    commit_sha: str
    
    steps: List[DeployStep] = field(default_factory=list)
    current_stage: DeployStage = DeployStage.PREVIEW
    
    # Governance
    max_canary_duration_minutes: int = 10
    max_observe_duration_minutes: int = 30
    rollback_triggered: bool = False
    
    # Artifact tracking
    artifacts_created: List[str] = field(default_factory=list)
    
    # Budget
    cost_estimate_usd: float = 0.0
    cost_actual_usd: float = 0.0
    
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.steps:
            self.steps = self._default_pipeline()
    
    def _default_pipeline(self) -> List[DeployStep]:
        return [
            DeployStep(DeployStage.PREVIEW, "vercel.deploy",
                {"environment": "preview", "project": self.project},
                stabilization_seconds=5),
            DeployStep(DeployStage.CANARY, "vercel.deploy",
                {"environment": "production", "project": self.project, "canary_percent": 10},
                health_check_url=f"https://{self.project}.vercel.app/api/health/live",
                stabilization_seconds=15, requires_approval=True),
            DeployStep(DeployStage.PARTIAL, "vercel.deploy",
                {"environment": "production", "project": self.project, "canary_percent": 50},
                stabilization_seconds=30, requires_approval=True),
            DeployStep(DeployStage.FULL, "vercel.deploy",
                {"environment": "production", "project": self.project, "canary_percent": 100},
                health_check_url=f"https://www.nexify-automate.com/api/health/v2",
                stabilization_seconds=30),
            DeployStep(DeployStage.OBSERVE, "browser.test",
                {"url": f"https://{self.project}.vercel.app", "test_script": "smoke_test"},
                stabilization_seconds=60),
        ]
    
    def advance(self, success: bool):
        current = self.steps[self.current_stage_index()]
        current.completed = True
        current.success = success
        
        if not success and self.current_stage != DeployStage.PREVIEW:
            self.rollback_triggered = True
            self.current_stage = DeployStage.ROLLBACK
        elif self.current_stage_index() + 1 < len(self.steps):
            self.current_stage = self.steps[self.current_stage_index() + 1].stage
        else:
            self.current_stage = DeployStage.COMPLETE
    
    def current_stage_index(self) -> int:
        for i, s in enumerate(self.steps):
            if s.stage == self.current_stage:
                return i
        return 0
    
    def rollback_steps(self) -> List[DeployStep]:
        """Steps to execute for rollback (reverse order of completed steps)."""
        return [s for s in reversed(self.steps) if s.completed and s.stage != DeployStage.ROLLBACK]
    
    def to_dict(self) -> Dict:
        return {
            "deploy_id": self.deploy_id, "project": self.project, "commit": self.commit_sha[:8],
            "current_stage": self.current_stage.value,
            "completed_steps": sum(1 for s in self.steps if s.completed),
            "total_steps": len(self.steps),
            "rollback_triggered": self.rollback_triggered,
            "cost_actual": self.cost_actual_usd,
        }


# ══════════════════════════════════════════════
# R8.4 — ECONOMIC GOVERNANCE
# ══════════════════════════════════════════════

@dataclass
class CostEstimate:
    """Estimated cost for an agent action."""
    action: str
    llm_tokens_estimate: int = 0
    api_calls_estimate: int = 0
    browser_minutes_estimate: int = 0
    deployment_count_estimate: int = 0
    
    # Cost rates (USD)
    llm_cost_per_1k_tokens: float = 0.002     # ~$2/M tokens for v4-flash
    api_call_cost: float = 0.001
    browser_cost_per_minute: float = 0.05
    deployment_cost: float = 0.02              # Vercel
    
    @property
    def total_estimate_usd(self) -> float:
        return round(
            (self.llm_tokens_estimate / 1000) * self.llm_cost_per_1k_tokens +
            self.api_calls_estimate * self.api_call_cost +
            self.browser_minutes_estimate * self.browser_cost_per_minute +
            self.deployment_count_estimate * self.deployment_cost,
            2
        )


@dataclass  
class ProjectBudget:
    """Budget for a single customer project."""
    project_id: str
    max_total_cost_usd: float = 5.00         # $5 default budget
    max_llm_cost_usd: float = 2.00
    max_deployment_cost_usd: float = 1.00
    max_browser_cost_usd: float = 1.00
    
    # Current spending
    llm_cost_spent: float = 0.0
    deployment_cost_spent: float = 0.0
    browser_cost_spent: float = 0.0
    
    # Gates
    warn_at_pct: float = 0.70
    block_at_pct: float = 0.90
    
    @property
    def total_spent(self) -> float:
        return round(self.llm_cost_spent + self.deployment_cost_spent + self.browser_cost_spent, 2)
    
    @property
    def remaining(self) -> float:
        return round(self.max_total_cost_usd - self.total_spent, 2)
    
    def can_afford(self, estimate: CostEstimate) -> tuple:
        """
        Check if project can afford an action.
        Returns (can_afford: bool, reason: str).
        """
        projected = self.total_spent + estimate.total_estimate_usd
        
        if projected > self.max_total_cost_usd * self.block_at_pct:
            return False, f"Budget block: ${projected:.2f} would exceed {self.block_at_pct:.0%} of ${self.max_total_cost_usd:.2f}"
        
        if projected > self.max_total_cost_usd * self.warn_at_pct:
            return True, f"Budget warning: ${projected:.2f} at {self.warn_at_pct:.0%} of ${self.max_total_cost_usd:.2f} (${self.remaining:.2f} remaining)"
        
        return True, f"Budget OK: ${projected:.2f} of ${self.max_total_cost_usd:.2f}"
    
    def spend(self, estimate: CostEstimate):
        """Record spending."""
        self.llm_cost_spent += (estimate.llm_tokens_estimate / 1000) * estimate.llm_cost_per_1k_tokens
        self.deployment_cost_spent += estimate.deployment_count_estimate * estimate.deployment_cost
        self.browser_cost_spent += estimate.browser_minutes_estimate * estimate.browser_cost_per_minute


class EconomicGovernor:
    """
    Economic governance for parallel customer projects.
    
    Prevents: cost overruns, runaway agent loops, budget exhaustion.
    Every agent action is cost-estimated BEFORE execution.
    """
    
    def __init__(self):
        self.projects: Dict[str, ProjectBudget] = {}
        self.estimates: List[CostEstimate] = []
    
    def create_project(self, project_id: str, max_cost: float = 5.00) -> ProjectBudget:
        budget = ProjectBudget(project_id=project_id, max_total_cost_usd=max_cost)
        self.projects[project_id] = budget
        return budget
    
    def estimate_action(self, action: str) -> CostEstimate:
        """Quick cost estimate for an action (without LLM call)."""
        estimates = {
            "github.create_pr": CostEstimate("github.create_pr", llm_tokens_estimate=500, api_calls_estimate=1),
            "github.merge_pr": CostEstimate("github.merge_pr", llm_tokens_estimate=200, api_calls_estimate=1),
            "vercel.deploy": CostEstimate("vercel.deploy", llm_tokens_estimate=100, deployment_count_estimate=1),
            "browser.test": CostEstimate("browser.test", api_calls_estimate=2, browser_minutes_estimate=2),
            "browser.screenshot": CostEstimate("browser.screenshot", api_calls_estimate=1, browser_minutes_estimate=0.5),
            "supabase.migrate": CostEstimate("supabase.migrate", llm_tokens_estimate=300, api_calls_estimate=1),
            "slack.notify": CostEstimate("slack.notify", api_calls_estimate=1),
            "email.send": CostEstimate("email.send", api_calls_estimate=1),
        }
        est = estimates.get(action, CostEstimate(action, llm_tokens_estimate=1000, api_calls_estimate=2))
        self.estimates.append(est)
        return est
    
    def stats(self) -> Dict:
        return {
            "projects": len(self.projects),
            "total_budget": sum(p.max_total_cost_usd for p in self.projects.values()),
            "total_spent": sum(p.total_spent for p in self.projects.values()),
            "projects_at_warning": len([p for p in self.projects.values() if p.total_spent > p.max_total_cost_usd * p.warn_at_pct]),
        }


# ══════════════════════════════════════════════
# R8.5 — HUMAN COLLABORATION RUNTIME
# ══════════════════════════════════════════════

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """A request for human approval."""
    request_id: str
    action: str                    # What needs approval
    requested_by: str              # Agent requesting
    context: str                   # Why this needs human judgment
    options: List[str] = field(default_factory=list)  # Choices presented to human
    risk_score: float = 0.0
    
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str = ""
    decided_at: float = 0.0
    comment: str = ""
    
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1h

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


@dataclass
class AuditExport:
    """Exportable audit trail for enterprise compliance."""
    export_id: str
    project_id: str
    format: str  # "json", "pdf", "csv"
    data: Dict = field(default_factory=dict)
    exported_at: float = field(default_factory=time.time)


class HumanCollaborationRuntime:
    """
    Human-in-the-loop collaboration for enterprise customers.
    
    Features:
    - Approval workflows with timeouts
    - Comment threads on decisions
    - Override capability (with audit trail)
    - Compliance-grade audit exports
    """
    
    def __init__(self):
        self.requests: Dict[str, ApprovalRequest] = {}
        self.audits: List[AuditExport] = []
        self._counter: int = 0
    
    def request_approval(
        self, action: str, requested_by: str, context: str,
        options: List[str] = None, risk_score: float = 0.0,
        timeout_minutes: int = 60,
    ) -> ApprovalRequest:
        """Request human approval for an action."""
        self._counter += 1
        req = ApprovalRequest(
            request_id=f"APR-{self._counter:04d}",
            action=action, requested_by=requested_by,
            context=context, options=options or ["Approve", "Reject"],
            risk_score=risk_score,
            expires_at=time.time() + (timeout_minutes * 60),
        )
        self.requests[req.request_id] = req
        return req
    
    def approve(self, request_id: str, decided_by: str = "operator", comment: str = "") -> bool:
        """Approve a pending request."""
        req = self.requests.get(request_id)
        if not req or req.is_expired or req.status != ApprovalStatus.PENDING:
            return False
        req.status = ApprovalStatus.APPROVED
        req.decided_by = decided_by
        req.decided_at = time.time()
        req.comment = comment
        return True
    
    def reject(self, request_id: str, decided_by: str = "operator", reason: str = "") -> bool:
        """Reject a pending request."""
        req = self.requests.get(request_id)
        if not req or req.is_expired or req.status != ApprovalStatus.PENDING:
            return False
        req.status = ApprovalStatus.REJECTED
        req.decided_by = decided_by
        req.decided_at = time.time()
        req.comment = reason
        return True
    
    def override(self, request_id: str, decided_by: str, reason: str) -> bool:
        """Override a rejected/expired decision (with audit trail)."""
        req = self.requests.get(request_id)
        if not req:
            return False
        req.status = ApprovalStatus.OVERRIDDEN
        req.decided_by = decided_by
        req.decided_at = time.time()
        req.comment = f"OVERRIDE by {decided_by}: {reason}"
        return True
    
    def export_audit(self, project_id: str, format: str = "json") -> AuditExport:
        """Generate compliance audit export."""
        project_requests = [r for r in self.requests.values() 
                          if r.action.startswith(project_id) or project_id == "*"]
        
        audit = AuditExport(
            export_id=f"AUDIT-{len(self.audits):04d}",
            project_id=project_id, format=format,
            data={
                "project": project_id,
                "total_decisions": len(project_requests),
                "approved": len([r for r in project_requests if r.status == ApprovalStatus.APPROVED]),
                "rejected": len([r for r in project_requests if r.status == ApprovalStatus.REJECTED]),
                "overridden": len([r for r in project_requests if r.status == ApprovalStatus.OVERRIDDEN]),
                "decisions": [
                    {"action": r.action, "status": r.status.value, "decided_by": r.decided_by,
                     "context": r.context, "comment": r.comment, "risk": r.risk_score}
                    for r in project_requests
                ],
            },
        )
        self.audits.append(audit)
        return audit
    
    def stats(self) -> Dict:
        return {
            "pending_approvals": len([r for r in self.requests.values() if r.status == ApprovalStatus.PENDING]),
            "expired": len([r for r in self.requests.values() if r.is_expired]),
            "total_decisions": len([r for r in self.requests.values() if r.status != ApprovalStatus.PENDING]),
            "audits_exported": len(self.audits),
        }
