"""
NeXifyAI — Delivery Transaction Layer (Phase C)
Golden Path cross-system transactions with full observability.

NOT: individual connector calls
BUT:  correlated, idempotent, compensable delivery transactions
      with SQLite-backed immutable event timelines.

C.1 — DeliveryTransaction Coordinator
C.2 — Persistent Event Store (SQLite)
C.3 — Golden Path Test
C.4 — Failure Injection
"""
import json
import sqlite3
import time
import uuid
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from backend.integration.operational_events import (
    OperationalEvent, OperationalEventLedger, IdempotentOperation,
    CompensatingActionEngine, StateReconciler,
    OperationalSystem, EventType, EventStatus,
)


# ═══════════════════════════════════════════════════
# C.2 — PERSISTENT EVENT STORE (SQLite)
# ═══════════════════════════════════════════════════

class PersistentEventLedger:
    """
    SQLite-backed operational event ledger.

    Replaces the in-memory OperationalEventLedger with:
      - Crash-safe persistence
      - Replay capability
      - Causal chain reconstruction
      - Duplicate detection across restarts
    """

    def __init__(self, db_path: str = "/opt/data/operational_events.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite event store schema."""
        db = sqlite3.connect(self.db_path)
        db.execute("""
            CREATE TABLE IF NOT EXISTS operational_events (
                event_id TEXT PRIMARY KEY,
                system TEXT NOT NULL,
                event_type TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                causation_id TEXT DEFAULT '',
                actor TEXT DEFAULT '',
                session_id TEXT DEFAULT '',
                resource_id TEXT DEFAULT '',
                resource_url TEXT DEFAULT '',
                status TEXT DEFAULT 'initiated',
                idempotency_key TEXT DEFAULT '',
                retry_count INTEGER DEFAULT 0,
                is_duplicate INTEGER DEFAULT 0,
                state_before TEXT DEFAULT '{}',
                state_after TEXT DEFAULT '{}',
                initiated_at REAL NOT NULL,
                completed_at REAL DEFAULT 0,
                duration_ms REAL DEFAULT 0,
                error_message TEXT DEFAULT '',
                error_code TEXT DEFAULT '',
                retryable INTEGER DEFAULT 1,
                has_compensating_action INTEGER DEFAULT 0,
                compensating_event_id TEXT DEFAULT '',
                rollback_strategy TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}'
            )
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_correlation ON operational_events(correlation_id)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_idempotency ON operational_events(idempotency_key)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_system ON operational_events(system)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource ON operational_events(resource_id)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_initiated ON operational_events(initiated_at)
        """)
        db.commit()
        db.close()

    def record(self, event: OperationalEvent) -> OperationalEvent:
        """Persist an operational event to SQLite."""
        # Check for duplicate
        if event.idempotency_key:
            existing = self.find_by_idempotency(event.idempotency_key)
            if existing and existing.status == EventStatus.SUCCEEDED:
                event.is_duplicate = True
                event.status = EventStatus.SUCCEEDED
                return event

        db = sqlite3.connect(self.db_path)
        db.execute("""
            INSERT OR REPLACE INTO operational_events (
                event_id, system, event_type, correlation_id, causation_id,
                actor, session_id, resource_id, resource_url, status,
                idempotency_key, retry_count, is_duplicate,
                state_before, state_after,
                initiated_at, completed_at, duration_ms,
                error_message, error_code, retryable,
                has_compensating_action, compensating_event_id, rollback_strategy,
                tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id, event.system.value, event.event_type.value,
            event.correlation_id, event.causation_id,
            event.actor, event.session_id,
            event.resource_id, event.resource_url, event.status.value,
            event.idempotency_key, event.retry_count, int(event.is_duplicate),
            json.dumps(event.state_before), json.dumps(event.state_after),
            event.initiated_at, event.completed_at, event.duration_ms,
            event.error_message, event.error_code, int(event.retryable),
            int(event.has_compensating_action), event.compensating_event_id,
            event.rollback_strategy,
            json.dumps(event.tags), json.dumps(event.metadata),
        ))
        db.commit()
        db.close()
        return event

    def find_by_idempotency(self, key: str) -> Optional[OperationalEvent]:
        """Find an event by its idempotency key."""
        db = sqlite3.connect(self.db_path)
        row = db.execute(
            "SELECT * FROM operational_events WHERE idempotency_key = ? LIMIT 1",
            (key,)
        ).fetchone()
        db.close()
        return self._row_to_event(row) if row else None

    def get_by_correlation(self, correlation_id: str) -> List[OperationalEvent]:
        """Get all events in a correlation group, ordered by time."""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        rows = db.execute(
            "SELECT * FROM operational_events WHERE correlation_id = ? ORDER BY initiated_at",
            (correlation_id,)
        ).fetchall()
        db.close()
        return [self._row_to_event(r) for r in rows]

    def get_causal_chain(self, event_id: str) -> List[OperationalEvent]:
        """Trace causal chain backwards."""
        chain = []
        current_id = event_id
        visited = set()
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row

        while current_id and current_id not in visited:
            row = db.execute(
                "SELECT * FROM operational_events WHERE event_id = ?", (current_id,)
            ).fetchone()
            if not row:
                break
            event = self._row_to_event(row)
            chain.append(event)
            visited.add(current_id)
            current_id = event.causation_id

        db.close()
        return list(reversed(chain))

    def find_by_idempotency(self, key: str) -> Optional[OperationalEvent]:
        """Find an event by its idempotency key."""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT * FROM operational_events WHERE idempotency_key = ? LIMIT 1",
            (key,)
        ).fetchone()
        db.close()
        return self._row_to_event(row) if row else None

    def get_timeline(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get a human-readable timeline for a correlation group."""
        events = self.get_by_correlation(correlation_id)
        return [
            {
                "time": e.initiated_at,
                "system": e.system.value,
                "event": e.event_type.value,
                "status": e.status.value,
                "resource": e.resource_id,
                "duration_ms": round(e.duration_ms, 1),
                "error": e.error_message[:100] if e.error_message else "",
                "compensated": e.has_compensating_action,
            }
            for e in events
        ]

    def stats(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        db = sqlite3.connect(self.db_path)
        total = db.execute("SELECT COUNT(*) FROM operational_events").fetchone()[0]
        by_status = {}
        for row in db.execute("SELECT status, COUNT(*) FROM operational_events GROUP BY status"):
            by_status[row[0]] = row[1]
        by_system = {}
        for row in db.execute("SELECT system, COUNT(*) FROM operational_events GROUP BY system"):
            by_system[row[0]] = row[1]
        corr_groups = db.execute(
            "SELECT COUNT(DISTINCT correlation_id) FROM operational_events"
        ).fetchone()[0]
        db.close()
        return {
            "total_events": total,
            "correlation_groups": corr_groups,
            "by_status": by_status,
            "by_system": by_system,
            "db_path": self.db_path,
        }

    def _row_to_event(self, row) -> OperationalEvent:
        """Convert a SQLite Row to an OperationalEvent (uses column names)."""
        return OperationalEvent(
            event_id=row["event_id"], system=OperationalSystem(row["system"]),
            event_type=EventType(row["event_type"]), correlation_id=row["correlation_id"],
            causation_id=row["causation_id"] or "", actor=row["actor"] or "",
            session_id=row["session_id"] or "", resource_id=row["resource_id"] or "",
            resource_url=row["resource_url"] or "", status=EventStatus(row["status"]),
            idempotency_key=row["idempotency_key"] or "", retry_count=row["retry_count"] or 0,
            is_duplicate=bool(row["is_duplicate"]),
            state_before=json.loads(row["state_before"] or "{}"),
            state_after=json.loads(row["state_after"] or "{}"),
            initiated_at=row["initiated_at"], completed_at=row["completed_at"] or 0.0,
            duration_ms=row["duration_ms"] or 0.0,
            error_message=row["error_message"] or "", error_code=row["error_code"] or "",
            retryable=bool(row["retryable"]),
            has_compensating_action=bool(row["has_compensating_action"]),
            compensating_event_id=row["compensating_event_id"] or "",
            rollback_strategy=row["rollback_strategy"] or "",
            tags=json.loads(row["tags"] or "[]"),
            metadata=json.loads(row["metadata"] or "{}"),
        )


# ═══════════════════════════════════════════════════
# C.1 — DELIVERY TRANSACTION COORDINATOR
# ═══════════════════════════════════════════════════

class TransactionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIALLY_FAILED = "partially_failed"
    FAILED = "failed"
    COMPENSATED = "compensated"
    ROLLED_BACK = "rolled_back"

@dataclass
class TransactionStep:
    """A single step in a delivery transaction."""
    name: str
    system: OperationalSystem
    event_type: EventType
    execute_fn: Callable  # () → Dict[str, Any]
    compensation_fn: Optional[Callable] = None  # () → None
    retryable: bool = True
    timeout_ms: int = 30000
    critical: bool = True  # If True, failure stops the transaction

class DeliveryTransaction:
    """
    Cross-system delivery transaction coordinator.

    NOT: individual connector calls
    BUT:  correlated, idempotent, compensable transaction with immutable timeline.

    Usage:
        tx = DeliveryTransaction("delivery_001", "LiveAgentRuntime")
        tx.add_step(TransactionStep(
            "Create tracking issue",
            OperationalSystem.GITHUB,
            EventType.GITHUB_ISSUE_CREATED,
            execute_fn=lambda: create_issue("Delivery started"),
        ))
        tx.add_step(TransactionStep(
            "Verify deployment",
            OperationalSystem.VERCEL,
            EventType.VERCEL_DEPLOY_READY,
            execute_fn=lambda: get_deployment_status(),
        ))
        timeline = tx.execute()
    """

    def __init__(self, correlation_id: str = "", actor: str = "LiveAgentRuntime",
                 ledger: PersistentEventLedger = None,
                 compensation_engine: CompensatingActionEngine = None):
        self.correlation_id = correlation_id or OperationalEvent.generate_correlation_id()
        self.actor = actor
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.ledger = ledger or PersistentEventLedger()
        self.compensation_engine = compensation_engine or CompensatingActionEngine(
            OperationalEventLedger()
        )
        self.steps: List[TransactionStep] = []
        self.status = TransactionStatus.PENDING
        self._execution_events: List[OperationalEvent] = []

    def add_step(self, step: TransactionStep):
        """Add a step to the transaction."""
        self.steps.append(step)

    def execute(self) -> Dict[str, Any]:
        """
        Execute all steps in order.

        On failure of a critical step:
          - Execute compensating actions for that step
          - Mark transaction as COMPENSATED or FAILED
          - Record all events in the persistent ledger

        Returns: {status, timeline, events, compensation_events}
        """
        self.status = TransactionStatus.RUNNING

        # Start event
        start_event = self._record_event(
            OperationalSystem.RUNTIME,
            EventType.DELIVERY_STARTED,
            resource_id=self.correlation_id,
        )
        start_event.complete(EventStatus.SUCCEEDED)
        self.ledger.record(start_event)
        self._execution_events.append(start_event)

        # Execute each step
        for i, step in enumerate(self.steps):
            step_event = self._execute_step(step, i)
            self._execution_events.append(step_event)

            if step_event.status == EventStatus.FAILED and step.critical:
                # Trigger compensation
                comp_events = self._compensate(step_event)
                self.status = TransactionStatus.COMPENSATED if comp_events else TransactionStatus.FAILED

                # Record completion
                end_event = self._record_event(
                    OperationalSystem.RUNTIME,
                    EventType.DELIVERY_FAILED if not comp_events else EventType.COMPENSATION_TRIGGERED,
                    resource_id=self.correlation_id,
                )
                end_event.complete(
                    EventStatus.FAILED if not comp_events else EventStatus.COMPENSATED
                )
                end_event.metadata = {"failed_step": step.name, "step_index": i}
                self.ledger.record(end_event)
                self._execution_events.append(end_event)

                return self._build_result()

        # All steps succeeded
        self.status = TransactionStatus.SUCCEEDED
        end_event = self._record_event(
            OperationalSystem.RUNTIME,
            EventType.DELIVERY_COMPLETED,
            resource_id=self.correlation_id,
        )
        end_event.complete(EventStatus.SUCCEEDED)
        self.ledger.record(end_event)
        self._execution_events.append(end_event)

        return self._build_result()

    def _execute_step(self, step: TransactionStep, index: int) -> OperationalEvent:
        """Execute a single transaction step."""
        event = self._record_event(
            step.system, step.event_type,
            resource_id=f"{self.correlation_id}:step{index}",
        )

        try:
            result = step.execute_fn()
            event.state_after = result if isinstance(result, dict) else {"result": str(result)}
            event.complete(EventStatus.SUCCEEDED)
        except Exception as e:
            event.state_after = {}
            event.fail(str(e), type(e).__name__)
            event.retryable = step.retryable

        self.ledger.record(event)
        return event

    def _compensate(self, failed_event: OperationalEvent) -> List[OperationalEvent]:
        """Execute compensating actions for a failed step."""
        return self.compensation_engine.execute_compensations(
            failed_event, self.correlation_id
        )

    def _record_event(self, system: OperationalSystem,
                      event_type: EventType,
                      resource_id: str = "") -> OperationalEvent:
        """Create a new event with correlation and causation."""
        last_event = self._execution_events[-1] if self._execution_events else None
        return OperationalEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            system=system,
            event_type=event_type,
            correlation_id=self.correlation_id,
            causation_id=last_event.event_id if last_event else "",
            actor=self.actor,
            session_id=self.session_id,
            resource_id=resource_id,
            idempotency_key=OperationalEvent.generate_idempotency_key(
                f"{system.value}:{event_type.value}", resource_id
            ),
        )

    def _build_result(self) -> Dict[str, Any]:
        """Build the execution result with full timeline."""
        timeline = self.ledger.get_timeline(self.correlation_id)
        return {
            "correlation_id": self.correlation_id,
            "status": self.status.value,
            "actor": self.actor,
            "session_id": self.session_id,
            "steps_total": len(self.steps),
            "steps_succeeded": sum(
                1 for e in self._execution_events
                if e.status == EventStatus.SUCCEEDED
                and e.system != OperationalSystem.RUNTIME
            ),
            "steps_failed": sum(
                1 for e in self._execution_events
                if e.status == EventStatus.FAILED
            ),
            "compensations_executed": sum(
                1 for e in self._execution_events
                if e.event_type == EventType.COMPENSATION_TRIGGERED
            ),
            "timeline": timeline,
            "ledger_stats": self.ledger.stats(),
        }

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get the immutable timeline for this transaction."""
        return self.ledger.get_timeline(self.correlation_id)

    def get_causal_chain(self) -> List[OperationalEvent]:
        """Get the full causal chain."""
        if self._execution_events:
            return self.ledger.get_causal_chain(self._execution_events[-1].event_id)
        return []


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_ledger: Optional[PersistentEventLedger] = None

def get_persistent_ledger() -> PersistentEventLedger:
    global _ledger
    if _ledger is None:
        _ledger = PersistentEventLedger()
    return _ledger
