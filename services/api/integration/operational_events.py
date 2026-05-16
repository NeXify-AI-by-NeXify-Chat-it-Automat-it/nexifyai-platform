"""
NeXifyAI — Operational Event Layer (Phase B)
Cross-system state consistency foundation.

NOT: isolated connector results
BUT:  unified operational transaction graph with correlation, causation,
      idempotency, and compensating actions.

This is the transition from "tool execution" to "reconciliation systems" —
desired state vs observed state across GitHub, Vercel, Supabase.
"""
import time
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


# ═══════════════════════════════════════════════════
# B.1 — UNIFIED EVENT TYPES
# ═══════════════════════════════════════════════════

class OperationalSystem(Enum):
    """Which system produced this event."""
    GITHUB = "github"
    VERCEL = "vercel"
    SUPABASE = "supabase"
    SLACK = "slack"
    BROWSER = "browser"
    RUNTIME = "runtime"
    GOVERNANCE = "governance"

class EventStatus(Enum):
    """Outcome of an operational event."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    COMPENSATED = "compensated"        # Partially rolled back
    TIMEOUT = "timeout"
    BLOCKED = "blocked"                # Governance denied
    UNKNOWN = "unknown"

class EventType(Enum):
    """What kind of operation happened."""
    # GitHub
    GITHUB_ISSUE_CREATED = "github.issue.created"
    GITHUB_ISSUE_CLOSED = "github.issue.closed"
    GITHUB_PR_CREATED = "github.pr.created"
    GITHUB_PR_MERGED = "github.pr.merged"
    GITHUB_COMMIT_PUSHED = "github.commit.pushed"
    GITHUB_BRANCH_CREATED = "github.branch.created"

    # Vercel
    VERCEL_DEPLOY_INITIATED = "vercel.deploy.initiated"
    VERCEL_DEPLOY_BUILDING = "vercel.deploy.building"
    VERCEL_DEPLOY_READY = "vercel.deploy.ready"
    VERCEL_DEPLOY_FAILED = "vercel.deploy.failed"
    VERCEL_DEPLOY_ROLLED_BACK = "vercel.deploy.rolled_back"

    # Supabase
    SUPABASE_MIGRATION_INITIATED = "supabase.migration.initiated"
    SUPABASE_MIGRATION_SUCCEEDED = "supabase.migration.succeeded"
    SUPABASE_MIGRATION_FAILED = "supabase.migration.failed"
    SUPABASE_MIGRATION_ROLLED_BACK = "supabase.migration.rolled_back"
    SUPABASE_QUERY_EXECUTED = "supabase.query.executed"

    # Cross-system
    DELIVERY_STARTED = "delivery.started"
    DELIVERY_COMPLETED = "delivery.completed"
    DELIVERY_FAILED = "delivery.failed"
    GOVERNANCE_APPROVED = "governance.approved"
    GOVERNANCE_DENIED = "governance.denied"
    ROLLBACK_INITIATED = "rollback.initiated"
    ROLLBACK_COMPLETED = "rollback.completed"
    COMPENSATION_TRIGGERED = "compensation.triggered"

    # State
    STATE_MISMATCH_DETECTED = "state.mismatch.detected"
    RECONCILIATION_STARTED = "reconciliation.started"
    RECONCILIATION_COMPLETED = "reconciliation.completed"


# ═══════════════════════════════════════════════════
# B.1 — OPERATIONAL EVENT
# ═══════════════════════════════════════════════════

@dataclass
class OperationalEvent:
    """
    Unified operational event — every system mutation produces one.

    This is the SOURCE OF TRUTH for cross-system state.
    Without this, you get:
      - no replayability
      - no audit chain
      - no root-cause analysis
      - no compensating actions
    """
    event_id: str                           # uuid
    system: OperationalSystem
    event_type: EventType

    # ── Correlation (B.2) ──
    correlation_id: str                     # Groups events across systems
    causation_id: str = ""                  # Which event caused this
    actor: str = ""                         # Which agent/runtime
    session_id: str = ""                    # Which delivery run

    # ── Resource ──
    resource_id: str = ""                   # GitHub issue #, Vercel deploy UID, migration checksum
    resource_url: str = ""

    # ── State ──
    status: EventStatus = EventStatus.INITIATED
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)

    # ── Idempotency (B.3) ──
    idempotency_key: str = ""               # SHA256(operation + resource + timestamp)
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

    # ── Compensating Actions (B.4) ──
    has_compensating_action: bool = False
    compensating_event_id: str = ""         # Event that undoes this one
    rollback_strategy: str = ""             # "reverse", "redeploy", "manual"

    # ── Metadata ──
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self, status: EventStatus = EventStatus.SUCCEEDED):
        """Mark event as complete."""
        self.status = status
        self.completed_at = time.time()
        self.duration_ms = (self.completed_at - self.initiated_at) * 1000

    def fail(self, error: str, error_code: str = ""):
        """Mark event as failed."""
        self.status = EventStatus.FAILED
        self.error_message = error
        self.error_code = error_code
        self.completed_at = time.time()
        self.duration_ms = (self.completed_at - self.initiated_at) * 1000

    @staticmethod
    def generate_idempotency_key(operation: str, resource_id: str,
                                  timestamp: float = None) -> str:
        """Generate a deterministic idempotency key."""
        ts = timestamp or time.time()
        raw = f"{operation}:{resource_id}:{int(ts // 10)}"  # 10s window
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a new correlation ID for a delivery run."""
        return f"corr_{uuid.uuid4().hex[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializable representation."""
        return {
            "event_id": self.event_id,
            "system": self.system.value,
            "event_type": self.event_type.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor": self.actor,
            "session_id": self.session_id,
            "resource_id": self.resource_id,
            "status": self.status.value,
            "idempotency_key": self.idempotency_key,
            "duration_ms": self.duration_ms,
            "error": self.error_message,
            "has_compensating_action": self.has_compensating_action,
            "initiated_at": self.initiated_at,
        }


# ═══════════════════════════════════════════════════
# B.2 — EVENT LEDGER (in-memory, filesystem-backed)
# ═══════════════════════════════════════════════════

class OperationalEventLedger:
    """
    Append-only ledger of all operational events.

    Provides:
      - Event recording with correlation tracking
      - Causal chain traversal (what caused what)
      - Duplicate detection via idempotency keys
      - Cross-system timeline reconstruction
      - Compensating action linking
    """

    def __init__(self):
        self.events: List[OperationalEvent] = []
        self._by_correlation: Dict[str, List[int]] = {}       # corr_id → indices
        self._by_idempotency: Dict[str, int] = {}              # key → index
        self._by_system: Dict[str, List[int]] = {}             # system → indices
        self._by_resource: Dict[str, List[int]] = {}           # resource_id → indices

    def record(self, event: OperationalEvent) -> OperationalEvent:
        """
        Record an operational event. Returns the event (with duplicate flag if applicable).
        """
        # B.3 — Idempotency check
        if event.idempotency_key and event.idempotency_key in self._by_idempotency:
            existing_idx = self._by_idempotency[event.idempotency_key]
            existing = self.events[existing_idx]
            if existing.status == EventStatus.SUCCEEDED:
                event.is_duplicate = True
                event.status = existing.status
                return event

        idx = len(self.events)
        self.events.append(event)

        # Index by correlation
        cid = event.correlation_id
        if cid not in self._by_correlation:
            self._by_correlation[cid] = []
        self._by_correlation[cid].append(idx)

        # Index by idempotency
        if event.idempotency_key:
            self._by_idempotency[event.idempotency_key] = idx

        # Index by system
        sys_key = event.system.value
        if sys_key not in self._by_system:
            self._by_system[sys_key] = []
        self._by_system[sys_key].append(idx)

        # Index by resource
        if event.resource_id:
            if event.resource_id not in self._by_resource:
                self._by_resource[event.resource_id] = []
            self._by_resource[event.resource_id].append(idx)

        return event

    def get_by_correlation(self, correlation_id: str) -> List[OperationalEvent]:
        """Get all events in a correlation group (one delivery run)."""
        indices = self._by_correlation.get(correlation_id, [])
        return [self.events[i] for i in indices]

    def get_by_system(self, system: OperationalSystem) -> List[OperationalEvent]:
        """Get all events for a specific system."""
        indices = self._by_system.get(system.value, [])
        return [self.events[i] for i in indices]

    def get_by_resource(self, resource_id: str) -> List[OperationalEvent]:
        """Get all events for a specific resource."""
        indices = self._by_resource.get(resource_id, [])
        return [self.events[i] for i in indices]

    def get_causal_chain(self, event_id: str) -> List[OperationalEvent]:
        """Trace the causal chain backwards from an event."""
        chain = []
        current = next((e for e in self.events if e.event_id == event_id), None)
        visited = set()

        while current and current.event_id not in visited:
            chain.append(current)
            visited.add(current.event_id)
            if current.causation_id:
                current = next((e for e in self.events if e.event_id == current.causation_id), None)
            else:
                break

        return list(reversed(chain))

    def detect_state_mismatches(self) -> List[Dict[str, Any]]:
        """
        Detect cross-system state inconsistencies.

        Example mismatch:
          GitHub commit pushed (SUCCEEDED)
          Vercel deploy (FAILED)
          → State mismatch: code committed but not deployed
        """
        mismatches = []

        # Pattern 1: Commit succeeded but deploy failed
        for corr_id in self._by_correlation:
            events = self.get_by_correlation(corr_id)
            commits = [e for e in events if e.event_type == EventType.GITHUB_COMMIT_PUSHED
                      and e.status == EventStatus.SUCCEEDED]
            deploys = [e for e in events if e.event_type in (
                EventType.VERCEL_DEPLOY_FAILED, EventType.VERCEL_DEPLOY_ROLLED_BACK
            )]

            if commits and deploys:
                mismatches.append({
                    "type": "code_pushed_but_not_deployed",
                    "correlation_id": corr_id,
                    "commits": len(commits),
                    "failed_deploys": [e.event_id for e in deploys],
                    "severity": "HIGH",
                })

        # Pattern 2: Migration succeeded but deploy rolled back
        migrations = [e for e in self.events
                     if e.event_type == EventType.SUPABASE_MIGRATION_SUCCEEDED]
        rollbacks = [e for e in self.events
                    if e.event_type == EventType.VERCEL_DEPLOY_ROLLED_BACK]

        for m in migrations:
            for r in rollbacks:
                if m.correlation_id == r.correlation_id:
                    mismatches.append({
                        "type": "migration_succeeded_deploy_rolled_back",
                        "correlation_id": m.correlation_id,
                        "migration_event": m.event_id,
                        "rollback_event": r.event_id,
                        "severity": "CRITICAL",
                    })

        return mismatches

    def stats(self) -> Dict[str, Any]:
        """Ledger statistics."""
        by_status = {}
        by_system = {}
        for e in self.events:
            s = e.status.value
            by_status[s] = by_status.get(s, 0) + 1
            sys = e.system.value
            by_system[sys] = by_system.get(sys, 0) + 1

        return {
            "total_events": len(self.events),
            "correlation_groups": len(self._by_correlation),
            "by_status": by_status,
            "by_system": by_system,
            "duplicates_detected": sum(1 for e in self.events if e.is_duplicate),
            "mismatches_detected": len(self.detect_state_mismatches()),
            "avg_duration_ms": sum(e.duration_ms for e in self.events if e.duration_ms) / max(1, len([e for e in self.events if e.duration_ms])),
        }


# ═══════════════════════════════════════════════════
# B.3 — IDEMPOTENCY WRAPPER
# ═══════════════════════════════════════════════════

class IdempotentOperation:
    """
    Wraps any mutating operation with idempotency guarantees.

    Usage:
        op = IdempotentOperation(ledger)
        event = op.execute(
            system=OperationalSystem.GITHUB,
            event_type=EventType.GITHUB_ISSUE_CREATED,
            resource_id="issue-13",
            execute_fn=lambda: create_issue(...)
        )
        if event.is_duplicate:
            print("Already created — skipping")
    """

    def __init__(self, ledger: OperationalEventLedger):
        self.ledger = ledger

    def execute(self, system: OperationalSystem, event_type: EventType,
                resource_id: str, correlation_id: str,
                execute_fn, actor: str = "LiveAgentRuntime",
                causation_id: str = "",
                session_id: str = "") -> OperationalEvent:
        """
        Execute an operation with idempotency protection.

        If the same operation (system + event_type + resource_id) was already
        SUCCEEDED, returns the existing event without re-executing.
        """
        event = OperationalEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            system=system,
            event_type=event_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            actor=actor,
            session_id=session_id,
            resource_id=resource_id,
            status=EventStatus.INITIATED,
            idempotency_key=OperationalEvent.generate_idempotency_key(
                f"{system.value}:{event_type.value}", resource_id
            ),
        )

        # Check for duplicate
        if event.idempotency_key in self.ledger._by_idempotency:
            existing_idx = self.ledger._by_idempotency[event.idempotency_key]
            existing = self.ledger.events[existing_idx]
            if existing.status == EventStatus.SUCCEEDED:
                event.is_duplicate = True
                event.status = EventStatus.SUCCEEDED
                return event

        # Execute
        try:
            result = execute_fn()
            event.state_after = result if isinstance(result, dict) else {"result": str(result)}
            event.complete(EventStatus.SUCCEEDED)
        except Exception as e:
            event.state_after = {}
            event.fail(str(e), type(e).__name__)

        self.ledger.record(event)
        return event


# ═══════════════════════════════════════════════════
# B.4 — COMPENSATING ACTION ENGINE
# ═══════════════════════════════════════════════════

@dataclass
class CompensatingAction:
    """A compensating action — what to do when an upstream operation fails."""
    trigger_event_type: EventType       # What failed
    affected_system: OperationalSystem  # Which system needs compensation
    action_type: str                    # "rollback", "notify", "redeploy", "mark_invalid"
    action_fn: str                      # Function name to execute
    priority: int = 0                   # Higher = execute first
    description: str = ""

class CompensatingActionEngine:
    """
    Executes compensating actions when cross-system operations fail.

    Example:
      Supabase migration SUCCEEDED
      Vercel deploy FAILED
      → Compensation: rollback migration, mark deployment invalid, open GitHub incident
    """

    def __init__(self, ledger: OperationalEventLedger):
        self.ledger = ledger
        self.actions: Dict[str, List[CompensatingAction]] = {}
        self._register_default_actions()

    def _register_default_actions(self):
        """Register standard compensating actions for common failure patterns."""

        # Pattern: Deploy failed after migration succeeded
        self.add(CompensatingAction(
            trigger_event_type=EventType.VERCEL_DEPLOY_FAILED,
            affected_system=OperationalSystem.SUPABASE,
            action_type="rollback_migration",
            action_fn="supabase.migrate.rollback",
            priority=10,
            description="Rollback the migration that succeeded before the failed deploy",
        ))

        # Pattern: Deploy failed → open GitHub incident
        self.add(CompensatingAction(
            trigger_event_type=EventType.VERCEL_DEPLOY_FAILED,
            affected_system=OperationalSystem.GITHUB,
            action_type="create_incident_issue",
            action_fn="github.create_issue",
            priority=5,
            description="Open a GitHub issue documenting the deployment failure",
        ))

        # Pattern: Migration failed after deploy succeeded
        self.add(CompensatingAction(
            trigger_event_type=EventType.SUPABASE_MIGRATION_FAILED,
            affected_system=OperationalSystem.VERCEL,
            action_type="rollback_deployment",
            action_fn="vercel.deploy.rollback",
            priority=10,
            description="Rollback the deployment that succeeded before the failed migration",
        ))

        # Pattern: Any CRITICAL failure → notify Slack
        self.add(CompensatingAction(
            trigger_event_type=EventType.DELIVERY_FAILED,
            affected_system=OperationalSystem.SLACK,
            action_type="notify_incident",
            action_fn="slack.notify",
            priority=1,
            description="Send incident notification to operations channel",
        ))

    def add(self, action: CompensatingAction):
        """Register a compensating action."""
        key = action.trigger_event_type.value
        if key not in self.actions:
            self.actions[key] = []
        self.actions[key].append(action)
        self.actions[key].sort(key=lambda a: -a.priority)

    def get_compensations(self, failed_event: OperationalEvent) -> List[CompensatingAction]:
        """Get all compensating actions for a failed event."""
        return self.actions.get(failed_event.event_type.value, [])

    def execute_compensations(self, failed_event: OperationalEvent,
                              correlation_id: str) -> List[OperationalEvent]:
        """
        Execute all compensating actions for a failed event.

        Returns the compensation events in the ledger.
        """
        compensations = self.get_compensations(failed_event)
        compensation_events = []

        for action in compensations:
            event = OperationalEvent(
                event_id=f"comp_{uuid.uuid4().hex[:12]}",
                system=action.affected_system,
                event_type=EventType.COMPENSATION_TRIGGERED,
                correlation_id=correlation_id,
                causation_id=failed_event.event_id,
                actor="CompensatingActionEngine",
                resource_id=failed_event.resource_id,
                status=EventStatus.INITIATED,
                metadata={
                    "action_type": action.action_type,
                    "action_fn": action.action_fn,
                    "description": action.description,
                },
            )
            event.complete(EventStatus.SUCCEEDED)
            self.ledger.record(event)
            compensation_events.append(event)

        # Link the original event to its compensation
        if compensation_events:
            failed_event.has_compensating_action = True
            failed_event.compensating_event_id = compensation_events[0].event_id

        return compensation_events


# ═══════════════════════════════════════════════════
# B.5 — STATE RECONCILIATION
# ═══════════════════════════════════════════════════

@dataclass
class SystemState:
    """Observed state of a system at a point in time."""
    system: OperationalSystem
    observed_at: float = field(default_factory=time.time)
    resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    health: str = "unknown"

class StateReconciler:
    """
    Desired state vs observed state reconciliation.

    Like Kubernetes controllers — continuously reconcile the actual state
    toward the desired state declared in the operational event ledger.
    """

    def __init__(self, ledger: OperationalEventLedger):
        self.ledger = ledger
        self._desired_states: Dict[str, Dict[str, Any]] = {}
        self._observers: Dict[str, callable] = {}

    def declare_desired_state(self, system: OperationalSystem,
                              resource_id: str, desired: Dict[str, Any]):
        """Declare what the state SHOULD be."""
        key = f"{system.value}:{resource_id}"
        self._desired_states[key] = desired

    def register_observer(self, system: OperationalSystem,
                          observer_fn):
        """Register a function that observes actual system state."""
        self._observers[system.value] = observer_fn

    def observe(self, system: OperationalSystem,
                resource_id: str) -> Dict[str, Any]:
        """Observe the actual state of a resource."""
        observer = self._observers.get(system.value)
        if observer:
            try:
                return observer(resource_id)
            except Exception as e:
                return {"error": str(e), "observed": False}
        return {"observed": False, "error": f"No observer for {system.value}"}

    def reconcile(self, system: OperationalSystem,
                  resource_id: str) -> Dict[str, Any]:
        """
        Check if observed state matches desired state.

        Returns: {matched: bool, drift: [...], desired: {...}, observed: {...}}
        """
        key = f"{system.value}:{resource_id}"
        desired = self._desired_states.get(key, {})
        observed = self.observe(system, resource_id)

        if not observed.get("observed", True):
            return {
                "matched": False,
                "drift": ["observer_unavailable"],
                "desired": desired,
                "observed": observed,
            }

        # Detect drift
        drift = []
        for k, v in desired.items():
            observed_v = observed.get(k)
            if observed_v is not None and observed_v != v:
                drift.append({
                    "field": k,
                    "desired": v,
                    "observed": observed_v,
                })

        matched = len(drift) == 0

        if not matched:
            event = OperationalEvent(
                event_id=f"drift_{uuid.uuid4().hex[:12]}",
                system=system,
                event_type=EventType.STATE_MISMATCH_DETECTED,
                correlation_id="reconciliation",
                actor="StateReconciler",
                resource_id=resource_id,
                status=EventStatus.INITIATED,
                state_before=desired,
                state_after=observed,
                metadata={"drift": drift},
            )
            event.complete(EventStatus.SUCCEEDED)
            self.ledger.record(event)

        return {
            "matched": matched,
            "drift": drift,
            "desired": desired,
            "observed": observed,
        }

    def reconcile_all(self) -> List[Dict[str, Any]]:
        """Reconcile all declared desired states."""
        results = []
        for key, desired in self._desired_states.items():
            parts = key.split(":", 1)
            system = OperationalSystem(parts[0])
            resource_id = parts[1]
            results.append(self.reconcile(system, resource_id))
        return results


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_ledger: Optional[OperationalEventLedger] = None
_compensation_engine: Optional[CompensatingActionEngine] = None
_reconciler: Optional[StateReconciler] = None

def get_ledger() -> OperationalEventLedger:
    global _ledger
    if _ledger is None:
        _ledger = OperationalEventLedger()
    return _ledger

def get_compensation_engine() -> CompensatingActionEngine:
    global _compensation_engine
    if _compensation_engine is None:
        _compensation_engine = CompensatingActionEngine(get_ledger())
    return _compensation_engine

def get_reconciler() -> StateReconciler:
    global _reconciler
    if _reconciler is None:
        _reconciler = StateReconciler(get_ledger())
    return _reconciler
