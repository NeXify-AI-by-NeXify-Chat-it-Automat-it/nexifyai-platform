"""NeXifyAI Core: Reconciliation Engine v4.8
AIC-49 Phase 1 — Enterprise Reconciliation

Post-ingestion reconciliation: ensures Oracle ↔ Brain ↔ Qdrant consistency.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


class ReconciliationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RECONCILED = "reconciled"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass
class ReconciliationEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    oracle_state: Optional[dict] = None
    brain_state: Optional[dict] = None
    qdrant_state: Optional[dict] = None
    status: ReconciliationStatus = ReconciliationStatus.PENDING
    conflicts: list = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None


class ReconciliationEngine:
    """
    Governed reconciliation engine.
    After every operation: verify Oracle, Brain, and Qdrant are consistent.
    """

    STORES = ["oracle", "brain", "qdrant"]

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._pending: list[ReconciliationEntry] = []
        self._history: list[ReconciliationEntry] = []
        self._stats = {
            "reconciled": 0,
            "conflicts_found": 0,
            "conflicts_resolved": 0,
            "failed": 0,
        }

    def schedule(self, entity_type: str, entity_id: str,
                 oracle_state: dict = None, brain_state: dict = None,
                 qdrant_state: dict = None) -> ReconciliationEntry:
        """Schedule an entity for reconciliation."""
        entry = ReconciliationEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            oracle_state=oracle_state,
            brain_state=brain_state,
            qdrant_state=qdrant_state,
        )
        self._pending.append(entry)
        return entry

    def reconcile(self, entry: ReconciliationEntry) -> ReconciliationEntry:
        """Reconcile a single entry across all stores."""
        entry.status = ReconciliationStatus.IN_PROGRESS
        entry.attempts += 1

        try:
            conflicts = self._find_conflicts(entry)

            if conflicts:
                entry.conflicts = conflicts
                entry.status = ReconciliationStatus.CONFLICT
                self._stats["conflicts_found"] += 1
            else:
                entry.status = ReconciliationStatus.RECONCILED
                entry.resolved_at = datetime.now(timezone.utc).isoformat()
                self._stats["reconciled"] += 1

        except Exception as e:
            entry.conflicts.append({"error": str(e)})
            entry.status = ReconciliationStatus.FAILED
            self._stats["failed"] += 1

        self._history.append(entry)
        return entry

    def reconcile_all(self) -> dict:
        """Reconcile all pending entries."""
        results = {"reconciled": 0, "conflicts": 0, "failed": 0}

        for entry in list(self._pending):
            result = self.reconcile(entry)
            if result.status == ReconciliationStatus.RECONCILED:
                results["reconciled"] += 1
                self._pending.remove(entry)
            elif result.status == ReconciliationStatus.CONFLICT:
                results["conflicts"] += 1
            else:
                results["failed"] += 1

        return results

    def _find_conflicts(self, entry: ReconciliationEntry) -> list:
        """Find conflicts between stores for an entity."""
        conflicts = []
        states = {
            "oracle": entry.oracle_state,
            "brain": entry.brain_state,
            "qdrant": entry.qdrant_state,
        }

        # Compare each pair of stores
        stores_with_state = [(k, v) for k, v in states.items() if v is not None]

        for i in range(len(stores_with_state)):
            for j in range(i + 1, len(stores_with_state)):
                store_a, state_a = stores_with_state[i]
                store_b, state_b = stores_with_state[j]

                diffs = self._diff_states(state_a, state_b)
                if diffs:
                    conflicts.append({
                        "store_a": store_a,
                        "store_b": store_b,
                        "differences": diffs,
                        "severity": self._severity(diffs),
                    })

        return conflicts

    def _diff_states(self, state_a: dict, state_b: dict) -> dict:
        """Find differences between two state dicts."""
        diffs = {}
        all_keys = set(state_a.keys()) | set(state_b.keys())

        for key in all_keys:
            val_a = state_a.get(key)
            val_b = state_b.get(key)
            if val_a != val_b:
                diffs[key] = {"a": val_a, "b": val_b}

        return diffs

    def _severity(self, diffs: dict) -> str:
        """Classify severity of differences."""
        critical_fields = {"content", "content_hash", "status", "governance_tags"}
        if any(k in critical_fields for k in diffs):
            return "critical"
        if len(diffs) > 3:
            return "high"
        if len(diffs) > 0:
            return "low"
        return "none"

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    def get_unresolved(self) -> list[ReconciliationEntry]:
        """Get all pending reconciliation entries."""
        return list(self._pending)
