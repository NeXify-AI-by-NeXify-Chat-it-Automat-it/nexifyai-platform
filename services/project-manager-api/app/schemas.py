"""Pydantic schemas for tasks, callbacks, and responses."""
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class TaskMode(str, Enum):
    readonly = "readonly"
    plan = "plan"
    implement = "implement"
    review = "review"
    deploy = "deploy"

class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"
    rejected = "rejected"
    needs_review = "needs_review"
    blocked_skill_registry = "blocked_skill_registry"
    blocked_tracker_parse_error = "blocked_tracker_parse_error"

class TaskInput(BaseModel):
    goal: str = Field(..., min_length=10, max_length=10000)
    mode: TaskMode = TaskMode.readonly
    priority: TaskPriority = TaskPriority.P2
    project: str = ""
    repo: str = ""
    branch_strategy: str = ""
    context: str = ""
    allowed_actions: list[str] = []
    denied_actions: list[str] = []
    acceptance_criteria: list[str] = []
    evidence_required: list[str] = []
    abort_conditions: list[str] = []
    brain_context_required: bool = True
    callback_url: str = ""

class TaskRecord(BaseModel):
    task_id: str = ""
    status: TaskStatus = TaskStatus.queued
    created_at: str = ""
    updated_at: str = ""
    created_by: str = "api"
    goal: str = ""
    mode: TaskMode = TaskMode.readonly
    priority: TaskPriority = TaskPriority.P2
    project: str = ""
    repo: str = ""
    branch_strategy: str = ""
    context: str = ""
    allowed_actions: list[str] = []
    denied_actions: list[str] = []
    acceptance_criteria: list[str] = []
    evidence_required: list[str] = []
    abort_conditions: list[str] = []
    brain_context_required: bool = True
    callback_url: str = ""
    result: dict[str, Any] | None = None
    evidence_path: str = ""
    error: str = ""
    external_event_id: str = ""
    skill_evidence: list[dict] = []
    warning_findings: list[dict] = []

class WorkerCallback(BaseModel):
    task_id: str
    status: TaskStatus
    summary: str = ""
    actions_taken: list[str] = []
    files_changed: list[str] = []
    branch: str = ""
    commit: str = ""
    evidence: list[str] = []
    blockers: list[str] = []
    risks: list[str] = []

class HealthResponse(BaseModel):
    api: str = "ok"
    brain: str = "unknown"
    registry: str = "unknown"
    skill_registry: str = "unknown"
    project_tracker: str = "unknown"
    worker_enabled: bool = False
    dry_run: bool = False
    version: str = ""
    total_skills: int = 0
