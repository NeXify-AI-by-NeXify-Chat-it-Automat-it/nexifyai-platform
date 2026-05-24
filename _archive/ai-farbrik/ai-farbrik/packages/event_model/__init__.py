"""
NeXifyAI — Global Event Contract (Package: event-model)

UNIFIED schema for ALL operational events across:
  - Skills (skill.* events)
  - Agents (agent.* events)
  - Governance (governance.* events)
  - Runtime (runtime.* events)
  - Delivery (delivery.* events)
  - Memory (memory.* events)
  - Knowledge (knowledge.* events)

NOT: isolated event types per system
BUT:  single typed event taxonomy with causal linking

This is the SOURCE OF TRUTH for the entire AI Fabrik.
Every system emits and consumes these event types.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import uuid
import hashlib
import json


# ═══════════════════════════════════════════════════
# EVENT TAXONOMY
# ═══════════════════════════════════════════════════

class EventDomain(Enum):
    """Top-level event domains."""
    SKILL = "skill"               # Tool/skill execution
    AGENT = "agent"               # Agent lifecycle
    GOVERNANCE = "governance"     # Policy, approval, risk
    RUNTIME = "runtime"           # System operations
    DELIVERY = "delivery"         # Transaction coordination
    MEMORY = "memory"             # Cognitive operations
    KNOWLEDGE = "knowledge"       # Ingestion, embedding, graph
    INFRA = "infra"               # Infrastructure, deployment

class EventStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    COMPENSATED = "compensated"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"

class EventRisk(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ═══════════════════════════════════════════════════
# GLOBAL EVENT
# ═══════════════════════════════════════════════════

@dataclass
class GlobalEvent:
    """
    Universal operational event — every system action produces one.

    Mandatory fields: event_id, domain, event_type, correlation_id, status
    Correlation fields: correlation_id, causation_id, session_id
    Idempotency: idempotency_key (SHA256 based)
    Compensation: compensating_event_id, rollback_strategy
    """

    # ── Identity ──
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    domain: EventDomain = EventDomain.RUNTIME
    event_type: str = ""                     # e.g., "skill.github.issue.created"
    version: str = "1.0.0"

    # ── Correlation ──
    correlation_id: str = ""                 # Groups related events
    causation_id: str = ""                   # Which event caused this
    session_id: str = ""                     # Session/run identifier
    actor: str = "system"                    # Who/what triggered this

    # ── Resource ──
    resource_type: str = ""                  # "issue", "deployment", "migration"
    resource_id: str = ""
    resource_url: str = ""

    # ── State ──
    status: EventStatus = EventStatus.INITIATED
    risk: EventRisk = EventRisk.LOW
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)

    # ── Idempotency ──
    idempotency_key: str = ""
    retry_count: int = 0
    is_duplicate: bool = False

    # ── Timing ──
    initiated_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    duration_ms: float = 0.0

    # ── Error ──
    error_message: str = ""
    error_code: str = ""
    retryable: bool = True

    # ── Compensation ──
    has_compensation: bool = False
    compensating_event_id: str = ""
    rollback_strategy: str = ""

    # ── Observability ──
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    span_id: str = ""                        # Distributed tracing
    trace_id: str = ""

    # ── Lineage ──
    source_system: str = ""                  # "live_agent_runtime", "paperclip"
    schema_hash: str = ""                    # Schema version fingerprint

    @staticmethod
    def generate_idempotency_key(domain: str, event_type: str,
                                  resource_id: str) -> str:
        raw = f"{domain}:{event_type}:{resource_id}:{int(time.time() // 10)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def generate_correlation_id() -> str:
        return f"corr_{uuid.uuid4().hex[:12]}"

    def complete(self, status: EventStatus = EventStatus.SUCCEEDED):
        self.status = status
        self.completed_at = time.time()
        self.duration_ms = (self.completed_at - self.initiated_at) * 1000

    def fail(self, error: str, code: str = ""):
        self.status = EventStatus.FAILED
        self.error_message = error
        self.error_code = code
        self.completed_at = time.time()
        self.duration_ms = (self.completed_at - self.initiated_at) * 1000

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "domain": self.domain.value,
            "event_type": self.event_type,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "status": self.status.value,
            "risk": self.risk.value,
            "resource_id": self.resource_id,
            "duration_ms": self.duration_ms,
            "error": self.error_message,
        }


# ═══════════════════════════════════════════════════
# STANDARD EVENT TYPES
# ═══════════════════════════════════════════════════

STANDARD_EVENT_TYPES = {
    # ── Skill Events ──
    "skill.initialized": {"domain": "skill", "risk": "LOW"},
    "skill.executed": {"domain": "skill", "risk": "LOW"},
    "skill.failed": {"domain": "skill", "risk": "MEDIUM"},
    "skill.compensated": {"domain": "skill", "risk": "MEDIUM"},

    # ── Agent Events ──
    "agent.spawned": {"domain": "agent", "risk": "LOW"},
    "agent.task.started": {"domain": "agent", "risk": "LOW"},
    "agent.task.completed": {"domain": "agent", "risk": "LOW"},
    "agent.task.failed": {"domain": "agent", "risk": "MEDIUM"},
    "agent.terminated": {"domain": "agent", "risk": "LOW"},

    # ── Governance Events ──
    "governance.approved": {"domain": "governance", "risk": "LOW"},
    "governance.denied": {"domain": "governance", "risk": "LOW"},
    "governance.risk.escalated": {"domain": "governance", "risk": "HIGH"},
    "governance.policy.violated": {"domain": "governance", "risk": "CRITICAL"},

    # ── Runtime Events ──
    "runtime.started": {"domain": "runtime", "risk": "LOW"},
    "runtime.stopped": {"domain": "runtime", "risk": "LOW"},
    "runtime.error": {"domain": "runtime", "risk": "HIGH"},
    "runtime.recovered": {"domain": "runtime", "risk": "MEDIUM"},

    # ── Delivery Events ──
    "delivery.started": {"domain": "delivery", "risk": "LOW"},
    "delivery.step.succeeded": {"domain": "delivery", "risk": "LOW"},
    "delivery.step.failed": {"domain": "delivery", "risk": "HIGH"},
    "delivery.completed": {"domain": "delivery", "risk": "LOW"},
    "delivery.failed": {"domain": "delivery", "risk": "CRITICAL"},
    "delivery.compensated": {"domain": "delivery", "risk": "HIGH"},

    # ── Memory Events ──
    "memory.retrieved": {"domain": "memory", "risk": "LOW"},
    "memory.stored": {"domain": "memory", "risk": "LOW"},
    "memory.consolidated": {"domain": "memory", "risk": "LOW"},
    "memory.expired": {"domain": "memory", "risk": "LOW"},

    # ── Knowledge Events ──
    "knowledge.ingested": {"domain": "knowledge", "risk": "LOW"},
    "knowledge.embedded": {"domain": "knowledge", "risk": "LOW"},
    "knowledge.indexed": {"domain": "knowledge", "risk": "LOW"},
    "knowledge.linked": {"domain": "knowledge", "risk": "LOW"},

    # ── Infra Events ──
    "infra.deploy.started": {"domain": "infra", "risk": "MEDIUM"},
    "infra.deploy.completed": {"domain": "infra", "risk": "LOW"},
    "infra.deploy.failed": {"domain": "infra", "risk": "HIGH"},
    "infra.deploy.rolled_back": {"domain": "infra", "risk": "HIGH"},
}


# ═══════════════════════════════════════════════════
# EVENT CONTRACT VALIDATOR
# ═══════════════════════════════════════════════════

def validate_event(event: GlobalEvent) -> List[str]:
    """Validate an event against the global contract. Returns list of violations."""
    violations = []

    if not event.event_id:
        violations.append("event_id is required")
    if not event.event_type:
        violations.append("event_type is required")
    if not event.correlation_id:
        violations.append("correlation_id is required")
    if not event.domain:
        violations.append("domain is required")

    if event.event_type not in STANDARD_EVENT_TYPES:
        violations.append(f"Unknown event_type: {event.event_type}")

    expected = STANDARD_EVENT_TYPES.get(event.event_type, {})
    if expected and expected["domain"] != event.domain.value:
        violations.append(
            f"Domain mismatch: {event.event_type} expects {expected['domain']}, "
            f"got {event.domain.value}"
        )

    return violations
