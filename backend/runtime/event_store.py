"""
NeXifyAI — Event Sourcing Engine (R1.2)
Append-only operational events with snapshot+delta recomputation.

Instead of mutable state, every change is an event:
  ObservationEvent  — new confidence data from a probe
  PropagationEvent  — confidence change from dependency
  ContradictionEvent — observer disagreement detected
  RecoveryEvent     — recovery action executed
  ReconciliationEvent — autonomous reconciliation applied

Benefits:
  - Deterministic replay: rebuild any past state
  - Parallel processing: events are immutable
  - Better temporal queries: "what was confidence at T-2h?"
  - Cheaper counterfactuals: replay from snapshot, not full history
  - Snapshot + delta: don't replay 1M events, replay from last snapshot
"""

import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum


class EventType(Enum):
    OBSERVATION = "observation"
    PROPAGATION = "propagation"
    CONTRADICTION = "contradiction"
    RECOVERY = "recovery"
    RECONCILIATION = "reconciliation"
    SNAPSHOT = "snapshot"
    TOPOLOGY_CHANGE = "topology_change"


@dataclass
class OperationalEvent:
    """Immutable operational event. Append-only."""
    event_id: str
    event_type: EventType
    service: str
    timestamp: float = field(default_factory=time.time)
    
    # Payload (varies by event type)
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Ordering
    sequence_number: int = 0
    
    # Metadata
    observer: str = "system"
    correlation_id: Optional[str] = None  # Links related events
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "type": self.event_type.value,
            "service": self.service,
            "timestamp": self.timestamp,
            "data": self.data,
            "sequence": self.sequence_number,
            "observer": self.observer,
            "correlation_id": self.correlation_id,
        }


@dataclass
class StateSnapshot:
    """Point-in-time state snapshot for fast replay."""
    snapshot_id: str
    timestamp: float
    sequence_number: int
    confidences: Dict[str, float]  # service → effective_confidence
    topology_hash: str
    event_count_at_snapshot: int


class EventStore:
    """
    Append-only event store with snapshot+delta replay.
    
    Events are NEVER mutated. State is rebuilt by replaying events.
    Snapshots provide fast-forward to recent state.
    
    Pattern:
      Write:  append_event() — O(1)
      Read:   replay_from_snapshot() — O(k) where k = events since last snapshot
      Snapshot: create_snapshot() — O(N), done periodically
    """
    
    SNAPSHOT_INTERVAL = 100  # Create snapshot every N events
    
    def __init__(self):
        self.events: List[OperationalEvent] = []
        self.snapshots: List[StateSnapshot] = []
        self._sequence = 0
        self._current_state: Dict[str, float] = {}
    
    def append_event(
        self,
        event_type: EventType,
        service: str,
        data: Dict[str, Any] = None,
        observer: str = "system",
        correlation_id: str = None,
    ) -> OperationalEvent:
        """Append an immutable event to the store."""
        self._sequence += 1
        
        event = OperationalEvent(
            event_id=f"evt-{self._sequence}-{int(time.time())}",
            event_type=event_type,
            service=service,
            data=data or {},
            sequence_number=self._sequence,
            observer=observer,
            correlation_id=correlation_id,
        )
        
        self.events.append(event)
        
        # Update current state incrementally
        if event_type == EventType.OBSERVATION:
            if "effective_confidence" in event.data:
                self._current_state[service] = event.data["effective_confidence"]
        
        # Auto-snapshot
        if self._sequence % self.SNAPSHOT_INTERVAL == 0:
            self.create_snapshot()
        
        return event
    
    def create_snapshot(self) -> StateSnapshot:
        """Create a point-in-time snapshot for fast replay."""
        snapshot = StateSnapshot(
            snapshot_id=f"snap-{self._sequence}",
            timestamp=time.time(),
            sequence_number=self._sequence,
            confidences=dict(self._current_state),
            topology_hash="current",
            event_count_at_snapshot=len(self.events),
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    def replay_from_snapshot(self, target_sequence: int = None) -> Dict[str, float]:
        """
        Rebuild state from the latest snapshot + delta events.
        
        If no target specified, replays to current state.
        Much faster than replaying all events from the beginning.
        """
        if target_sequence is None:
            target_sequence = self._sequence
        
        # Find latest snapshot before target
        snapshot = None
        for s in reversed(self.snapshots):
            if s.sequence_number <= target_sequence:
                snapshot = s
                break
        
        if snapshot:
            state = dict(snapshot.confidences)
            start_seq = snapshot.sequence_number + 1
        else:
            state = {}
            start_seq = 1
        
        # Replay only delta events
        events_replayed = 0
        for event in self.events:
            if event.sequence_number < start_seq:
                continue
            if event.sequence_number > target_sequence:
                break
            
            events_replayed += 1
            
            if event.event_type == EventType.OBSERVATION:
                if "effective_confidence" in event.data:
                    state[event.service] = event.data["effective_confidence"]
        
        return state
    
    def replay_full(self) -> Dict[str, float]:
        """Full replay from event 0 (for debugging/audit)."""
        state = {}
        for event in self.events:
            if event.event_type == EventType.OBSERVATION:
                if "effective_confidence" in event.data:
                    state[event.service] = event.data["effective_confidence"]
        return state
    
    def query_window(
        self,
        start_time: float,
        end_time: float = None,
        service: str = None,
        event_type: EventType = None,
    ) -> List[OperationalEvent]:
        """Query events in a time window."""
        end_time = end_time or time.time()
        
        results = []
        for event in self.events:
            if event.timestamp < start_time:
                continue
            if event.timestamp > end_time:
                break
            if service and event.service != service:
                continue
            if event_type and event.event_type != event_type:
                continue
            results.append(event)
        
        return results
    
    def correlation_chain(self, correlation_id: str) -> List[OperationalEvent]:
        """Get all events linked by correlation ID (causal chain)."""
        return [e for e in self.events if e.correlation_id == correlation_id]
    
    def stats(self) -> Dict:
        """Event store statistics."""
        return {
            "total_events": len(self.events),
            "total_snapshots": len(self.snapshots),
            "current_sequence": self._sequence,
            "events_by_type": {
                t.value: len([e for e in self.events if e.event_type == t])
                for t in EventType
            },
            "latest_snapshot_seq": self.snapshots[-1].sequence_number if self.snapshots else 0,
            "events_since_snapshot": len(self.events) - (self.snapshots[-1].event_count_at_snapshot if self.snapshots else 0),
            "snapshot_replay_speedup": round(
                len(self.events) / max(1, len(self.events) - (self.snapshots[-1].event_count_at_snapshot if self.snapshots else 0)), 1
            ),
        }
