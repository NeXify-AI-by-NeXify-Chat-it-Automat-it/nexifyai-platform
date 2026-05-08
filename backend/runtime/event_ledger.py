"""
NeXifyAI — Global Event Ledger (Sprint E.1)
Single Source of Truth for ALL runtime events.

Deterministic, append-only, causal-chain-aware.
NOT print() or logger.info() — structured operational memory.

Fields:
  event_id        — deterministic reference
  logical_time    — monotonic event counter (NEVER datetime.now())
  causal_parent   — event that caused this one (lineage)
  actor_id        — which actor/service generated this
  snapshot_id     — state snapshot at time of event
  event_type      — typed operational event
  payload         — serialized event data
  confidence_before/after — epistemic state change
  topology_hash   — for consistency validation

Principle: NO wall-clock time. NO random(). NO hidden mutation.
          Everything is event-derived for deterministic replay.
"""

import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class LedgerEventType(Enum):
    OBSERVATION = "observation"
    CONFIDENCE_UPDATE = "confidence_update"
    CONTRADICTION = "contradiction"
    RECOVERY_START = "recovery_start"
    RECOVERY_COMPLETE = "recovery_complete"
    POLICY_CHECK = "policy_check"
    POLICY_REJECTION = "policy_rejection"
    ACTION_APPLIED = "action_applied"
    PROPAGATION = "propagation"
    SNAPSHOT = "snapshot"
    TOPOLOGY_CHANGE = "topology_change"


@dataclass
class LedgerEvent:
    """Immutable, deterministic event in the global ledger."""
    event_id: str
    logical_time: int               # Monotonic counter — NEVER wall-clock
    causal_parent: Optional[str]     # Event that caused this (lineage)
    actor_id: str                    # Which service/actor
    event_type: LedgerEventType
    snapshot_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    confidence_before: float = 1.0
    confidence_after: float = 1.0
    topology_hash: str = ""
    timestamp: float = field(default_factory=time.time)  # Wall-clock for human reference only
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "logical_time": self.logical_time,
            "causal_parent": self.causal_parent,
            "actor_id": self.actor_id,
            "event_type": self.event_type.value,
            "snapshot_id": self.snapshot_id,
            "payload": self.payload,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "topology_hash": self.topology_hash,
        }


class EventLedger:
    """
    Deterministic global event ledger.
    
    Append-only. Every event has a causal parent.
    Logical time increases monotonically.
    Topology hash validates consistency.
    """
    
    def __init__(self):
        self.events: List[LedgerEvent] = []
        self._logical_clock: int = 0
        self._topology_hash: str = ""
        self._update_topology_hash()
    
    def _update_topology_hash(self):
        """Recompute topology fingerprint."""
        try:
            from backend.runtime.service_registry import CANONICAL_REGISTRY
            deps = json.dumps(
                {svc: svc.depends_on for svc in CANONICAL_REGISTRY.values()},
                sort_keys=True
            )
            self._topology_hash = hashlib.sha256(deps.encode()).hexdigest()[:16]
        except Exception:
            self._topology_hash = "unknown"
    
    def record(
        self,
        event_type: LedgerEventType,
        actor_id: str,
        causal_parent: str = None,
        payload: Dict = None,
        confidence_before: float = 1.0,
        confidence_after: float = 1.0,
        snapshot_id: str = None,
    ) -> LedgerEvent:
        """Append a deterministic event to the ledger."""
        self._logical_clock += 1
        
        event = LedgerEvent(
            event_id=f"evt-{self._logical_clock:06d}",
            logical_time=self._logical_clock,
            causal_parent=causal_parent,
            actor_id=actor_id,
            event_type=event_type,
            snapshot_id=snapshot_id,
            payload=payload or {},
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            topology_hash=self._topology_hash,
        )
        
        self.events.append(event)
        return event
    
    def causal_chain(self, event_id: str) -> List[LedgerEvent]:
        """Trace the full causal chain backwards from an event."""
        chain = []
        current_id = event_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            event = self.get_event(current_id)
            if not event:
                break
            chain.append(event)
            current_id = event.causal_parent
        
        return list(reversed(chain))  # Root cause first
    
    def get_event(self, event_id: str) -> Optional[LedgerEvent]:
        for e in self.events:
            if e.event_id == event_id:
                return e
        return None
    
    def query_window(
        self,
        logical_from: int = 0,
        logical_to: int = None,
        actor_id: str = None,
        event_type: LedgerEventType = None,
    ) -> List[LedgerEvent]:
        """Query events by logical time window."""
        logical_to = logical_to or self._logical_clock
        
        results = []
        for e in self.events:
            if e.logical_time < logical_from:
                continue
            if e.logical_time > logical_to:
                break
            if actor_id and e.actor_id != actor_id:
                continue
            if event_type and e.event_type != event_type:
                continue
            results.append(e)
        
        return results
    
    def topology_consistency_check(self) -> List[Dict]:
        """Check if any events were recorded under a different topology."""
        inconsistencies = []
        current_hash = self._topology_hash
        
        for e in self.events:
            if e.topology_hash and e.topology_hash != current_hash:
                inconsistencies.append({
                    "event_id": e.event_id,
                    "recorded_hash": e.topology_hash,
                    "current_hash": current_hash,
                    "logical_time": e.logical_time,
                })
        
        return inconsistencies
    
    def stats(self) -> Dict:
        return {
            "total_events": len(self.events),
            "logical_clock": self._logical_clock,
            "topology_hash": self._topology_hash,
            "by_type": {
                t.value: len([e for e in self.events if e.event_type == t])
                for t in LedgerEventType
            },
            "topology_inconsistencies": len(self.topology_consistency_check()),
        }
