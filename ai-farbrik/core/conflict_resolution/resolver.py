"""NeXifyAI Core: Conflict Resolution v4.8
AIC-49 Phase 1 — Enterprise Conflict Resolution

Detects and resolves conflicts between knowledge sources.
Truth arbitration with governance validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib
import uuid


class ConflictType(Enum):
    DUPLICATE = "duplicate"
    DIVERGENT = "divergent"
    STALE = "stale"
    MISSING = "missing"
    INVALID = "invalid"
    CONTRADICTION = "contradiction"


class ResolutionStrategy(Enum):
    MERGE = "merge"
    SOURCE_A_WINS = "source_a_wins"
    SOURCE_B_WINS = "source_b_wins"
    KEEP_BOTH = "keep_both"
    MANUAL = "manual"
    LATEST_WINS = "latest_wins"
    GOVERNED_WINS = "governed_wins"


@dataclass
class Conflict:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    source_a: str = ""
    source_b: str = ""
    conflict_type: ConflictType = ConflictType.DUPLICATE
    description: str = ""
    field_diffs: dict = field(default_factory=dict)
    resolution: Optional[ResolutionStrategy] = None
    resolved_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None


@dataclass
class ResolutionResult:
    conflict_id: str
    resolved: bool
    strategy: Optional[ResolutionStrategy] = None
    merged_entity: Optional[dict] = None
    audit_event: dict = field(default_factory=dict)


class ConflictResolver:
    """Governed conflict detection and resolution."""

    # Resolution priority: which source wins by default
    SOURCE_PRIORITY = {
        "supabase_oracle": 100,
        "brain_bot": 90,
        "governance_kernel": 85,
        "adr": 80,
        "policy": 75,
        "directive": 70,
        "runtime_config": 60,
        "chat": 30,
        "unknown": 10,
    }

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._conflicts: list[Conflict] = []
        self._resolved: list[ResolutionResult] = []
        self._stats = {
            "conflicts_detected": 0,
            "resolved_auto": 0,
            "resolved_manual": 0,
            "pending": 0,
        }

    def detect(self, entity_a: dict, entity_b: dict,
               entity_type: str) -> Optional[Conflict]:
        """Detect conflicts between two entities."""
        entity_id = entity_a.get("id", entity_b.get("id", ""))
        source_a = entity_a.get("source", "unknown")
        source_b = entity_b.get("source", "unknown")

        field_diffs = self._diff_fields(entity_a, entity_b)

        if not field_diffs:
            return None  # Entities are identical

        conflict_type = self._classify_conflict(field_diffs, entity_a, entity_b)

        conflict = Conflict(
            entity_type=entity_type,
            entity_id=entity_id,
            source_a=source_a,
            source_b=source_b,
            conflict_type=conflict_type,
            description=f"{conflict_type.value}: {len(field_diffs)} fields differ",
            field_diffs=field_diffs,
        )

        self._conflicts.append(conflict)
        self._stats["conflicts_detected"] += 1
        self._stats["pending"] += 1

        return conflict

    def resolve(self, conflict: Conflict,
                strategy: ResolutionStrategy = None,
                entity_a: dict = None,
                entity_b: dict = None) -> ResolutionResult:
        """Resolve a conflict using the specified or default strategy."""
        if strategy is None:
            strategy = self._auto_strategy(conflict)

        merged = None

        if strategy == ResolutionStrategy.MERGE and entity_a and entity_b:
            merged = self._merge_entities(entity_a, entity_b)
        elif strategy == ResolutionStrategy.SOURCE_A_WINS:
            merged = entity_a
        elif strategy == ResolutionStrategy.SOURCE_B_WINS:
            merged = entity_b
        elif strategy == ResolutionStrategy.LATEST_WINS:
            merged = self._latest_entity(entity_a, entity_b)
        elif strategy == ResolutionStrategy.GOVERNED_WINS:
            merged = self._governed_winner(entity_a, entity_b)

        result = ResolutionResult(
            conflict_id=conflict.id,
            resolved=strategy != ResolutionStrategy.MANUAL,
            strategy=strategy,
            merged_entity=merged,
            audit_event={
                "event": "conflict_resolved",
                "conflict_id": conflict.id,
                "strategy": strategy.value,
                "resolved_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        conflict.resolution = strategy
        conflict.resolved_at = datetime.now(timezone.utc).isoformat()
        conflict.resolved_by = "ai-ceo"

        if strategy == ResolutionStrategy.MANUAL:
            self._stats["resolved_manual"] += 1
        else:
            self._stats["resolved_auto"] += 1

        self._stats["pending"] = max(0, self._stats["pending"] - 1)
        self._resolved.append(result)

        return result

    def _diff_fields(self, a: dict, b: dict) -> dict:
        """Compute field-level differences."""
        diffs = {}
        all_keys = set(a.keys()) | set(b.keys())

        for key in all_keys:
            val_a = a.get(key)
            val_b = b.get(key)

            if key in ("id", "source", "created_at", "updated_at"):
                continue

            if val_a != val_b:
                diffs[key] = {"a": val_a, "b": val_b}

        return diffs

    def _classify_conflict(self, diffs: dict, a: dict, b: dict) -> ConflictType:
        """Classify the type of conflict."""
        if not diffs:
            return ConflictType.DUPLICATE

        # Check for contradiction (same field, opposite values)
        for key, vals in diffs.items():
            if isinstance(vals["a"], bool) and isinstance(vals["b"], bool):
                if vals["a"] != vals["b"]:
                    return ConflictType.CONTRADICTION

        # Check for stale (one entity much older)
        ts_a = a.get("updated_at") or a.get("created_at", "")
        ts_b = b.get("updated_at") or b.get("created_at", "")
        if ts_a and ts_b and ts_a != ts_b:
            return ConflictType.STALE

        return ConflictType.DIVERGENT

    def _auto_strategy(self, conflict: Conflict) -> ResolutionStrategy:
        """Determine automatic resolution strategy."""
        priority_a = self.SOURCE_PRIORITY.get(conflict.source_a, 10)
        priority_b = self.SOURCE_PRIORITY.get(conflict.source_b, 10)

        if conflict.conflict_type == ConflictType.DUPLICATE:
            return ResolutionStrategy.KEEP_BOTH
        if conflict.conflict_type == ConflictType.CONTRADICTION:
            return ResolutionStrategy.MANUAL  # Needs human review

        if priority_a >= priority_b:
            return ResolutionStrategy.SOURCE_A_WINS
        else:
            return ResolutionStrategy.SOURCE_B_WINS

    def _merge_entities(self, a: dict, b: dict) -> dict:
        """Merge two entities, preferring non-null values."""
        merged = dict(b)  # Start with b as base
        for key, val in a.items():
            if val is not None and (key not in merged or merged[key] is None):
                merged[key] = val
        merged["merged_from"] = [a.get("id"), b.get("id")]
        merged["merged_at"] = datetime.now(timezone.utc).isoformat()
        return merged

    def _latest_entity(self, a: dict, b: dict) -> dict:
        """Return the most recently updated entity."""
        ts_a = a.get("updated_at") or a.get("created_at", "")
        ts_b = b.get("updated_at") or b.get("created_at", "")
        return a if ts_a > ts_b else b

    def _governed_winner(self, a: dict, b: dict) -> dict:
        """Select winner based on governance priority."""
        priority_a = self.SOURCE_PRIORITY.get(a.get("source", "unknown"), 10)
        priority_b = self.SOURCE_PRIORITY.get(b.get("source", "unknown"), 10)
        return a if priority_a >= priority_b else b

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def pending_conflicts(self) -> list[Conflict]:
        return [c for c in self._conflicts if c.resolution is None]
