"""
NeXifyAI — Multi-Agent Operational Mesh (R6)
Autonomous Delivery Organization Runtime.

NOT: one big agent with a giant prompt.
BUT:  small bounded expert agents with shared cognitive store and runtime governance.

Architecture:
  Oracle / Planner
      ↓
  Program Manager Agent
      ↓
  Specialized Sub-Agent Mesh (16 agents)
      ↓
  Runtime Governance Layer (R5)
      ↓
  Execution

Principle: workflow engineering > prompt engineering.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import time
import json


# ══════════════════════════════════════════════
# R6.1 — AGENT REGISTRY
# ══════════════════════════════════════════════

class AgentDomain(Enum):
    ORACLE = "oracle"
    PROGRAM_MANAGER = "program_manager"
    ARCHITECT = "architect"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    DEVOPS = "devops"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    QA = "qa"
    BROWSER_TEST = "browser_test"
    UX = "ux"
    SEO = "seo"
    COPYWRITING = "copywriting"
    GRAPHIC = "graphic"
    ANALYTICS = "analytics"
    GOVERNANCE = "governance"


@dataclass
class AgentCapability:
    """Bounded capability declaration for a specialist agent."""
    agent_id: str
    domain: AgentDomain
    description: str
    
    # Tools this agent can use
    tools: List[str] = field(default_factory=list)  # e.g., ["vercel", "playwright", "github"]
    
    # Governance constraints
    risk_limit: float = 0.10              # Max rollback risk this agent can take
    max_blast_radius: int = 1             # Max downstream services affected
    requires_human: bool = False          # Must get human approval?
    
    # Resource limits
    max_parallel_tasks: int = 4           # Concurrent tasks
    max_tokens_per_task: int = 100000     # Token budget
    max_api_calls_per_hour: int = 50      # API rate limit
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other agents that must complete first
    
    # State
    active_tasks: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    
    def can_accept_task(self) -> bool:
        return self.active_tasks < self.max_parallel_tasks
    
    @property
    def success_rate(self) -> float:
        total = self.total_tasks_completed + self.total_tasks_failed
        return self.total_tasks_completed / max(1, total)


class AgentRegistry:
    """
    Central registry of all specialist agents.
    
    Enforces capability bounds. No agent can exceed its declared limits.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentCapability] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the full 42-agent NeXifyAI mesh (27 Brain + 15 Creative/Legacy)."""
        defaults = [
            # === CORE ORCHESTRATION (P0 Priority) ===
            AgentCapability("oracle", AgentDomain.ORACLE, "Parses intent, routes via Brain semantic search",
                          tools=["llm", "brain"], risk_limit=0.0, max_blast_radius=0, max_parallel_tasks=1),
            AgentCapability("project-manager", AgentDomain.PROGRAM_MANAGER, "Zentrale Projektkoordination — 4 Tenants, DOS v2.1",
                          tools=["llm", "brain", "registry"], risk_limit=0.0, max_blast_radius=0, max_parallel_tasks=2),
            AgentCapability("task-decomposition-expert", AgentDomain.PROGRAM_MANAGER, "Work-Breakdown mit Dependencies, Effort, Agent-Zuweisung",
                          tools=["llm", "brain", "registry"], risk_limit=0.0, max_parallel_tasks=2),
            AgentCapability("project-supervisor-orchestrator", AgentDomain.PROGRAM_MANAGER, "Multi-Projekt-Supervision — Velocity, Quality, Budget",
                          tools=["llm", "brain"], risk_limit=0.0, max_parallel_tasks=1),
            AgentCapability("business-analyst", AgentDomain.PROGRAM_MANAGER, "Business-Anforderungen → Specs, Gap-Analyse, KPIs",
                          tools=["llm", "brain"], risk_limit=0.01, max_parallel_tasks=2),
            # === AI & ARCHITECTURE ===
            AgentCapability("ai-engineer", AgentDomain.ARCHITECT, "AI Systems Architect — Agenten-Okosystem design & build",
                          tools=["dos", "adr", "brain", "llm"], risk_limit=0.05, max_parallel_tasks=2),
            AgentCapability("agent-expert", AgentDomain.ARCHITECT, "Prompt-Optimierung, Lifecycle, Inter-Agent-Protokolle",
                          tools=["llm", "brain", "policy_engine"], risk_limit=0.02, max_parallel_tasks=2),
            AgentCapability("prompt-engineer", AgentDomain.ARCHITECT, "Few-Shot, Chain-of-Thought, Prompt-Optimierung",
                          tools=["llm"], risk_limit=0.01, max_parallel_tasks=2),
            AgentCapability("documentation-expert", AgentDomain.ARCHITECT, "Docusaurus, ADR, OpenAPI, Runbooks",
                          tools=["llm", "gitbook"], risk_limit=0.01, max_parallel_tasks=2),
            AgentCapability("metadata-agent", AgentDomain.ARCHITECT, "Auto-Tagging, Brain-Metadaten",
                          tools=["brain", "qdrant"], risk_limit=0.01, max_parallel_tasks=2),
            # === DEVELOPMENT ===
            AgentCapability("fullstack-developer", AgentDomain.BACKEND, "DB→API→Frontend, TS-Strict, Zod, Supabase",
                          tools=["github", "pytest", "docker", "vercel"], risk_limit=0.08, max_parallel_tasks=3),
            AgentCapability("backend-python", AgentDomain.BACKEND, "FastAPI backend, APIs, middleware",
                          tools=["github", "pytest", "docker"], risk_limit=0.08, max_parallel_tasks=3),
            AgentCapability("frontend-react", AgentDomain.FRONTEND, "React/Next.js UI, Coral Design System",
                          tools=["vercel", "playwright", "npm"], risk_limit=0.08, max_parallel_tasks=3),
            AgentCapability("nextjs-architecture-expert", AgentDomain.FRONTEND, "Next.js 14, shadcn/ui, App Router",
                          tools=["vercel", "npm", "playwright"], risk_limit=0.08, max_parallel_tasks=2),
            # === DATABASE ===
            AgentCapability("supabase-schema-architect", AgentDomain.DATABASE, "PostgreSQL + RLS, safe Migrations",
                          tools=["supabase", "psql"], risk_limit=0.12, max_parallel_tasks=2),
            AgentCapability("database", AgentDomain.DATABASE, "Supabase, migrations, queries (legacy)",
                          tools=["supabase", "psql"], risk_limit=0.12, max_parallel_tasks=2),
            # === INFRASTRUCTURE ===
            AgentCapability("cloud-architect", AgentDomain.DEVOPS, "Multi-Cloud, ADR-013 Isolation, DR",
                          tools=["docker", "tailscale", "ssh"], risk_limit=0.15, max_blast_radius=3, requires_human=True, max_parallel_tasks=2),
            AgentCapability("deployment-engineer", AgentDomain.DEPLOYMENT, "CI/CD: GitHub Actions → Vercel/Docker",
                          tools=["vercel", "github", "docker"], risk_limit=0.10, max_blast_radius=2, max_parallel_tasks=2),
            AgentCapability("deployment", AgentDomain.DEPLOYMENT, "Vercel deploy, DNS, health checks (legacy)",
                          tools=["vercel", "curl"], risk_limit=0.10, max_blast_radius=2, max_parallel_tasks=2),
            AgentCapability("architecture-modernizer", AgentDomain.ARCHITECT, "Strangler-Fig, Monolith→Microservices",
                          tools=["dos", "adr", "docker"], risk_limit=0.10, max_blast_radius=3, requires_human=True, max_parallel_tasks=1),
            AgentCapability("monitoring-specialist", AgentDomain.DEVOPS, "4 Golden Signals, Uptime Kuma, Grafana",
                          tools=["prometheus", "grafana", "uptime-kuma"], risk_limit=0.05, max_parallel_tasks=2),
            # === SECURITY & QUALITY ===
            AgentCapability("security-engineer", AgentDomain.SECURITY, "DevSecOps, Trivy, Gitleaks, DSGVO",
                          tools=["gitleaks", "trivy", "safety"], risk_limit=0.05, max_parallel_tasks=2),
            AgentCapability("security", AgentDomain.SECURITY, "Security audits, secret scanning (legacy)",
                          tools=["gitleaks", "trivy", "safety"], risk_limit=0.05, max_parallel_tasks=2),
            AgentCapability("security-auditor", AgentDomain.GOVERNANCE, "Audit, Pentest, Compliance-Check",
                          tools=["gitleaks", "trivy", "policy_engine"], risk_limit=0.05, max_parallel_tasks=1),
            AgentCapability("review-agent", AgentDomain.QA, "Code/PR-Review, DOS v2.1-Compliance, ADR-013",
                          tools=["github", "policy_engine"], risk_limit=0.02, max_parallel_tasks=3),
            AgentCapability("dependency-manager", AgentDomain.DEVOPS, "Renovate, npm/pip/Docker-Audit",
                          tools=["github", "npm", "pip-audit"], risk_limit=0.05, max_parallel_tasks=2),
            AgentCapability("qa", AgentDomain.QA, "Unit/Integration/E2E tests, coverage gates",
                          tools=["pytest", "jest", "playwright"], risk_limit=0.05, max_parallel_tasks=4),
            AgentCapability("browser-test", AgentDomain.BROWSER_TEST, "Playwright E2E, visual regression",
                          tools=["playwright", "browserbase"], risk_limit=0.05, max_parallel_tasks=3),
            # === DATA & RESEARCH ===
            AgentCapability("data-analyst", AgentDomain.ANALYTICS, "Statistik, Trend-Analyse, Forecasting",
                          tools=["prometheus", "grafana", "llm"], risk_limit=0.02, max_parallel_tasks=2),
            AgentCapability("data-engineer", AgentDomain.ANALYTICS, "ETL: GitHub→Supabase, Brain→Analytics",
                          tools=["supabase", "github", "python"], risk_limit=0.05, max_parallel_tasks=2),
            AgentCapability("research-coordinator", AgentDomain.ORACLE, "Recherche-Delegation, Multi-Source-Synthese",
                          tools=["llm", "brain", "search"], risk_limit=0.01, max_parallel_tasks=2),
            AgentCapability("fact-checker", AgentDomain.GOVERNANCE, "Multi-Source-Validation, E3.5 Directive 3",
                          tools=["llm", "search"], risk_limit=0.01, max_parallel_tasks=2),
            AgentCapability("search-specialist", AgentDomain.ORACLE, "Qdrant Vector+Keyword, Reranking",
                          tools=["qdrant", "brain"], risk_limit=0.01, max_parallel_tasks=2),
            # === AI INFRA ===
            AgentCapability("llms-maintainer", AgentDomain.ORACLE, "LLM-Provider: NeXify AI/OpenRouter/Emergent",
                          tools=["llm", "monitoring"], risk_limit=0.02, max_parallel_tasks=1),
            AgentCapability("context-manager", AgentDomain.ORACLE, "Brain-Integration, Context-Window-Management",
                          tools=["brain", "qdrant"], risk_limit=0.01, max_parallel_tasks=2),
            # === DOCS & ANALYTICS ===
            AgentCapability("document-structure-analyzer", AgentDomain.ANALYTICS, "PDF/Scan→JSON, Risk-Flagging",
                          tools=["llm", "pdf"], risk_limit=0.02, max_parallel_tasks=2),
            AgentCapability("analytics", AgentDomain.ANALYTICS, "Telemetry, dashboards, metrics (legacy)",
                          tools=["prometheus", "grafana"], risk_limit=0.02, max_parallel_tasks=2),
            # === CREATIVE ===
            AgentCapability("ux", AgentDomain.UX, "Accessibility, design audit, component contracts",
                          tools=["axe-core", "lighthouse"], risk_limit=0.02, max_parallel_tasks=2),
            AgentCapability("seo", AgentDomain.SEO, "SEO audit, meta tags, Core Web Vitals",
                          tools=["lighthouse"], risk_limit=0.02, max_parallel_tasks=2),
            AgentCapability("copywriting", AgentDomain.COPYWRITING, "Copy, content, brand voice",
                          tools=["llm"], risk_limit=0.01, max_parallel_tasks=3),
            AgentCapability("graphic", AgentDomain.GRAPHIC, "Images, icons, OG images",
                          tools=["sharp", "figma"], risk_limit=0.01, max_parallel_tasks=2),
            # === GOVERNANCE ===
            AgentCapability("governance", AgentDomain.GOVERNANCE, "Policy enforcement, recovery, audit",
                          tools=["policy_engine", "capability_registry"], risk_limit=0.0, max_blast_radius=0, max_parallel_tasks=1),
            AgentCapability("devops", AgentDomain.DEVOPS, "CI/CD, Docker, infrastructure (legacy, requires human)",
                          tools=["docker", "github", "ssh"], risk_limit=0.15, max_blast_radius=3, requires_human=True, max_parallel_tasks=2),
        ]
        
        for agent in defaults:
            self.register(agent)
    
    def register(self, agent: AgentCapability):
        self.agents[agent.agent_id] = agent
    
    def get(self, agent_id: str) -> Optional[AgentCapability]:
        return self.agents.get(agent_id)
    
    def find_by_domain(self, domain: AgentDomain) -> List[AgentCapability]:
        return [a for a in self.agents.values() if a.domain == domain]
    
    def available_agents(self) -> List[AgentCapability]:
        return [a for a in self.agents.values() if a.can_accept_task()]
    
    def stats(self) -> Dict:
        return {
            "total_agents": len(self.agents),
            "available": len(self.available_agents()),
            "by_domain": {d.value: len(self.find_by_domain(d)) for d in AgentDomain},
            "total_completed": sum(a.total_tasks_completed for a in self.agents.values()),
            "total_failed": sum(a.total_tasks_failed for a in self.agents.values()),
        }


# ══════════════════════════════════════════════
# R6.2 — HANDOFF PROTOCOL
# ══════════════════════════════════════════════

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskContract:
    """
    Formal handoff between agents.
    
    Every task has explicit: objective, constraints, acceptance criteria, artifacts.
    NOT: "do this thing" — structured operational contract.
    """
    task_id: str
    objective: str                          # What must be achieved
    assigned_to: str                        # Agent ID
    assigned_by: str                        # Agent ID that delegated
    
    # Constraints
    constraints: List[str] = field(default_factory=list)  # "must not exceed X", "must use Y"
    max_duration_seconds: int = 600          # 10 min default
    max_retries: int = 2
    
    # Acceptance
    acceptance_criteria: List[str] = field(default_factory=list)  # Verifiable conditions
    required_artifacts: List[str] = field(default_factory=list)   # Files that must be produced
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Task IDs that must complete first
    
    # State
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    
    # Results
    artifacts_produced: List[str] = field(default_factory=list)
    acceptance_passed: bool = False
    handoff_notes: str = ""
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_tasks for dep in self.depends_on)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id, "objective": self.objective,
            "assigned_to": self.assigned_to, "status": self.status.value,
            "acceptance_passed": self.acceptance_passed,
            "artifacts": self.artifacts_produced,
        }


class HandoffProtocol:
    """
    Structured handoff protocol between agents.
    
    Tasks are explicitly contracted, not implicitly assumed.
    Every handoff has acceptance criteria that must be verified.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.tasks: Dict[str, TaskContract] = {}
        self.completed_tasks: Set[str] = set()
        self._task_counter: int = 0
    
    def create_task(
        self, objective: str, assigned_to: str, assigned_by: str,
        constraints: List[str] = None, acceptance_criteria: List[str] = None,
        required_artifacts: List[str] = None, depends_on: List[str] = None,
    ) -> TaskContract:
        """Create a new task contract."""
        agent = self.registry.get(assigned_to)
        if not agent:
            raise ValueError(f"Agent {assigned_to} not registered")
        if not agent.can_accept_task():
            raise ValueError(f"Agent {assigned_to} at capacity ({agent.active_tasks}/{agent.max_parallel_tasks})")
        
        self._task_counter += 1
        task = TaskContract(
            task_id=f"TASK-{self._task_counter:04d}",
            objective=objective,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            constraints=constraints or [],
            acceptance_criteria=acceptance_criteria or [],
            required_artifacts=required_artifacts or [],
            depends_on=depends_on or [],
        )
        
        agent.active_tasks += 1
        task.status = TaskStatus.ASSIGNED
        self.tasks[task.task_id] = task
        
        return task
    
    def start_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        if not task.is_ready(self.completed_tasks):
            task.status = TaskStatus.BLOCKED
            return False
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = time.time()
        return True
    
    def complete_task(self, task_id: str, artifacts: List[str] = None, notes: str = "") -> bool:
        """Mark task complete and verify acceptance criteria."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.artifacts_produced = artifacts or []
        task.handoff_notes = notes
        task.completed_at = time.time()
        
        # Verify acceptance criteria (in production: actual artifact inspection)
        task.acceptance_passed = len(task.artifacts_produced) >= len(task.required_artifacts)
        
        if task.acceptance_passed:
            task.status = TaskStatus.COMPLETED
            self.completed_tasks.add(task_id)
            
            agent = self.registry.get(task.assigned_to)
            if agent:
                agent.active_tasks -= 1
                agent.total_tasks_completed += 1
        else:
            task.status = TaskStatus.AWAITING_REVIEW
        
        return task.acceptance_passed
    
    def fail_task(self, task_id: str, reason: str = "") -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            return False  # Will be retried
        
        task.status = TaskStatus.FAILED
        agent = self.registry.get(task.assigned_to)
        if agent:
            agent.active_tasks -= 1
            agent.total_tasks_failed += 1
        return True
    
    def get_ready_tasks(self) -> List[TaskContract]:
        """Tasks that are ready to start (dependencies satisfied)."""
        return [t for t in self.tasks.values() 
                if t.status == TaskStatus.ASSIGNED and t.is_ready(self.completed_tasks)]
    
    def stats(self) -> Dict:
        by_status = {}
        for s in TaskStatus:
            count = len([t for t in self.tasks.values() if t.status == s])
            if count > 0:
                by_status[s.value] = count
        
        return {
            "total_tasks": len(self.tasks),
            "completed": len(self.completed_tasks),
            "by_status": by_status,
            "acceptance_rate": len([t for t in self.tasks.values() if t.acceptance_passed]) / max(1, len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])),
        }


# ══════════════════════════════════════════════
# R6.3 — SHARED WORKING MEMORY
# ══════════════════════════════════════════════

@dataclass
class WorkspaceArtifact:
    """An artifact in the collaborative workspace."""
    artifact_id: str
    artifact_type: str          # "code", "design", "test", "config", "report"
    content: str
    created_by: str
    created_at: float = field(default_factory=time.time)
    version: int = 1
    tags: List[str] = field(default_factory=list)
    reviewed_by: List[str] = field(default_factory=list)


class SharedWorkspace:
    """
    Ephemeral collaborative workspace for multi-agent collaboration.
    
    NOT: long-term brain memory (that's CognitiveStore).
    BUT:  short-term shared artifacts during a project execution.
    
    Agents read/write artifacts. Other agents review and build upon them.
    """
    
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.artifacts: Dict[str, WorkspaceArtifact] = {}
        self.task_status_board: Dict[str, TaskStatus] = {}
        self.agent_notes: Dict[str, List[str]] = {}  # agent_id → notes
        self._artifact_counter: int = 0
    
    def put_artifact(self, artifact_type: str, content: str, created_by: str, tags: List[str] = None) -> str:
        """Add an artifact to the shared workspace."""
        self._artifact_counter += 1
        artifact = WorkspaceArtifact(
            artifact_id=f"ART-{self._artifact_counter:04d}",
            artifact_type=artifact_type, content=content, created_by=created_by,
            tags=tags or [],
        )
        self.artifacts[artifact.artifact_id] = artifact
        return artifact.artifact_id
    
    def get_artifact(self, artifact_id: str) -> Optional[WorkspaceArtifact]:
        return self.artifacts.get(artifact_id)
    
    def find_by_type(self, artifact_type: str) -> List[WorkspaceArtifact]:
        return [a for a in self.artifacts.values() if a.artifact_type == artifact_type]
    
    def find_by_tag(self, tag: str) -> List[WorkspaceArtifact]:
        return [a for a in self.artifacts.values() if tag in a.tags]
    
    def update_status(self, task_id: str, status: TaskStatus):
        self.task_status_board[task_id] = status
    
    def add_note(self, agent_id: str, note: str):
        if agent_id not in self.agent_notes:
            self.agent_notes[agent_id] = []
        self.agent_notes[agent_id].append(f"[{time.strftime('%H:%M:%S')}] {note}")
    
    def stats(self) -> Dict:
        return {
            "workspace_id": self.workspace_id,
            "total_artifacts": len(self.artifacts),
            "by_type": {
                t: len(self.find_by_type(t))
                for t in set(a.artifact_type for a in self.artifacts.values())
            },
            "agents_contributed": len(set(a.created_by for a in self.artifacts.values())),
        }


# ══════════════════════════════════════════════
# R6.4 — MULTI-AGENT SCHEDULER
# ══════════════════════════════════════════════

@dataclass
class ResourceBudget:
    """Global resource budget for the agent mesh."""
    max_concurrent_tasks: int = 20
    max_tokens_per_minute: int = 500000
    max_api_calls_per_minute: int = 30
    max_browser_sessions: int = 4
    max_deployment_actions_per_hour: int = 5
    
    # Current usage
    active_tasks: int = 0
    tokens_used_this_minute: int = 0
    api_calls_this_minute: int = 0
    browser_sessions_active: int = 0
    deployments_this_hour: int = 0


class MultiAgentScheduler:
    """
    Global resource governance for the agent mesh.
    
    Prevents: token explosion, API rate limits, browser storms, cost overruns.
    
    Scheduling policy:
    1. Governance tasks ALWAYS get priority
    2. Security tasks next
    3. Then by dependency depth (fewer deps = earlier)
    4. Then FIFO
    """
    
    def __init__(self, registry: AgentRegistry, budget: ResourceBudget = None):
        self.registry = registry
        self.budget = budget or ResourceBudget()
        self.queue: List[TaskContract] = []
        self.running: Dict[str, TaskContract] = {}
    
    def enqueue(self, task: TaskContract):
        """Add task to scheduling queue."""
        self.queue.append(task)
    
    def schedule(self) -> List[TaskContract]:
        """
        Schedule ready tasks within resource budget.
        Returns list of tasks that can start now.
        
        Priority: governance > security > low-deps > FIFO.
        """
        self.queue.sort(key=lambda t: (
            0 if t.assigned_to == "governance" else
            1 if t.assigned_to == "security" else
            2 + len(t.depends_on)
        ))
        
        scheduled = []
        for task in list(self.queue):
            if self.budget.active_tasks >= self.budget.max_concurrent_tasks:
                break
            
            agent = self.registry.get(task.assigned_to)
            if not agent or not agent.can_accept_task():
                continue
            
            if task.assigned_to == "browser-test" and self.budget.browser_sessions_active >= self.budget.max_browser_sessions:
                continue
            
            if task.assigned_to == "deployment" and self.budget.deployments_this_hour >= self.budget.max_deployment_actions_per_hour:
                continue
            
            # Allocate
            self.queue.remove(task)
            self.running[task.task_id] = task
            self.budget.active_tasks += 1
            agent.active_tasks += 1
            
            if task.assigned_to == "browser-test":
                self.budget.browser_sessions_active += 1
            if task.assigned_to == "deployment":
                self.budget.deployments_this_hour += 1
            
            scheduled.append(task)
        
        return scheduled
    
    def release(self, task_id: str):
        """Release resources after task completion."""
        task = self.running.pop(task_id, None)
        if not task:
            return
        
        self.budget.active_tasks -= 1
        agent = self.registry.get(task.assigned_to)
        if agent:
            agent.active_tasks = max(0, agent.active_tasks - 1)
        
        if task.assigned_to == "browser-test":
            self.budget.browser_sessions_active = max(0, self.budget.browser_sessions_active - 1)
    
    def stats(self) -> Dict:
        return {
            "queue_depth": len(self.queue),
            "running": len(self.running),
            "budget": {
                "tasks": f"{self.budget.active_tasks}/{self.budget.max_concurrent_tasks}",
                "browser_sessions": f"{self.budget.browser_sessions_active}/{self.budget.max_browser_sessions}",
                "deployments": f"{self.budget.deployments_this_hour}/{self.budget.max_deployment_actions_per_hour}",
            },
        }


# ══════════════════════════════════════════════
# R6.5 — DETERMINISTIC EXECUTION PLANS
# ══════════════════════════════════════════════

@dataclass
class ExecutionStep:
    """A single step in an execution plan."""
    step_id: str
    action: str               # "create_task", "wait_for", "parallel", "review", "handoff"
    agent_id: str
    task_objective: str = ""
    depends_on: List[str] = field(default_factory=list)
    rollback_action: str = ""


@dataclass
class ExecutionPlan:
    """
    Deterministic execution plan.
    
    LLM creates the plan. Runtime executes it.
    NOT: LLM executes step-by-step.
    
    Like a Makefile or DAG: dependencies resolved, steps parallelized.
    """
    plan_id: str
    objective: str
    steps: List[ExecutionStep] = field(default_factory=list)
    rollback_strategy: str = ""
    created_by: str = "planner"
    created_at: float = field(default_factory=time.time)
    
    # Execution state
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)
    
    def ready_steps(self) -> List[ExecutionStep]:
        """Steps whose dependencies are all satisfied."""
        ready = []
        for step in self.steps:
            if step.step_id in self.completed_steps or step.step_id in self.failed_steps:
                continue
            if all(dep in self.completed_steps for dep in step.depends_on):
                ready.append(step)
        return ready
    
    def can_parallelize(self, steps: List[ExecutionStep]) -> List[List[ExecutionStep]]:
        """Group independent steps that can run in parallel."""
        groups = []
        remaining = list(steps)
        
        while remaining:
            group = [remaining[0]]
            remaining = remaining[1:]
            
            for step in list(remaining):
                # Step can join group if it doesn't depend on any step in the group
                group_deps = set()
                for s in group:
                    group_deps.update(s.depends_on)
                
                if step.step_id not in group_deps and not any(
                    s.step_id in step.depends_on for s in group
                ):
                    group.append(step)
                    remaining.remove(step)
            
            groups.append(group)
        
        return groups
    
    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id, "objective": self.objective,
            "steps": [{"id": s.step_id, "agent": s.agent_id, "action": s.action,
                       "objective": s.task_objective, "depends_on": s.depends_on}
                      for s in self.steps],
            "completed": len(self.completed_steps), "failed": len(self.failed_steps),
            "total": len(self.steps),
        }
