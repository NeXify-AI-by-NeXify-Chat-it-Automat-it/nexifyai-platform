"""Shared data classes for Temporal Workflows and Activities."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class AgentTask:
    """A task to be executed by an agent."""
    task_id: str
    description: str
    agent: str
    team: str = "default"
    capability: str = "general"
    priority: int = 5
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent execution."""
    task_id: str
    agent: str
    status: str  # completed, failed, partial
    summary: str
    result: Any = None
    execution_time_ms: int = 0
    quality_gate: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class QualityGateResult:
    """Quality gate check result."""
    gate_type: str
    passed: bool
    score: float
    criteria: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class WorkflowResult:
    """Complete workflow result."""
    workflow_id: str
    workflow_type: str
    status: str  # completed, failed, running
    steps: List[AgentResult] = field(default_factory=list)
    quality_gates: List[QualityGateResult] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    total_time_ms: int = 0
