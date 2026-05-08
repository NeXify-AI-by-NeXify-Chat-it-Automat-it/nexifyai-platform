"""
NeXifyAI — Deterministic Replay Engine (Sprint E.2)
Replays events from the Event Ledger to reconstruct any past state.

Core operations:
  replay_until(logical_time)  — rebuild state at any point in time
  replay_event(event)         — apply a single event to state
  reconstruct_snapshot(id)    — rebuild snapshot from events
  fork_from_event(event_id)   — branch a new simulation from any past event

CRITICAL: NO datetime.now(), NO random(), NO hidden mutation state.
          Everything must be event-derived for deterministic reproducibility.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from backend.runtime.event_ledger import EventLedger, LedgerEvent, LedgerEventType


@dataclass
class ReplayState:
    """Mutable state accumulator during replay."""
    confidences: Dict[str, float] = field(default_factory=dict)
    contradictions: List[Dict] = field(default_factory=list)
    recoveries: List[Dict] = field(default_factory=list)
    current_logical_time: int = 0
    events_replayed: int = 0


class ReplayEngine:
    """
    Deterministic replay from event ledger.
    
    Rebuilds any past state by replaying events in logical-time order.
    Every replay of the same event sequence produces IDENTICAL state.
    
    This is the foundation for:
    - Audit: "What was the state at event #42?"
    - Counterfactuals: "What if event #23 had been different?"
    - Debugging: "When exactly did confidence drop?"
    """
    
    def __init__(self, ledger: EventLedger):
        self.ledger = ledger
        self.state = ReplayState()
    
    def replay_until(self, logical_time: int) -> ReplayState:
        """
        Rebuild state at a specific logical time.
        
        Replays all events with logical_time <= target.
        Returns the reconstructed state.
        
        Deterministic: same events → same state, every time.
        """
        state = ReplayState()
        
        for event in self.ledger.events:
            if event.logical_time > logical_time:
                break
            
            self._apply_event(state, event)
        
        return state
    
    def replay_all(self) -> ReplayState:
        """Replay entire event history."""
        return self.replay_until(self.ledger._logical_clock)
    
    def replay_event(self, event: LedgerEvent) -> ReplayState:
        """Apply a single event to the current state."""
        self._apply_event(self.state, event)
        return self.state
    
    def _apply_event(self, state: ReplayState, event: LedgerEvent):
        """Apply one event to a replay state. Pure function — no side effects."""
        state.current_logical_time = event.logical_time
        state.events_replayed += 1
        
        if event.event_type == LedgerEventType.CONFIDENCE_UPDATE:
            state.confidences[event.actor_id] = event.confidence_after
        
        elif event.event_type == LedgerEventType.OBSERVATION:
            state.confidences[event.actor_id] = event.confidence_after
        
        elif event.event_type == LedgerEventType.CONTRADICTION:
            state.contradictions.append({
                "actor": event.actor_id,
                "event_id": event.event_id,
                "logical_time": event.logical_time,
                "diagnosis": event.payload.get("diagnosis", ""),
            })
            state.confidences[event.actor_id] = event.confidence_after
        
        elif event.event_type == LedgerEventType.RECOVERY_COMPLETE:
            state.recoveries.append({
                "actor": event.actor_id,
                "action": event.payload.get("action", ""),
                "logical_time": event.logical_time,
            })
            state.confidences[event.actor_id] = event.confidence_after
        
        elif event.event_type == LedgerEventType.PROPAGATION:
            for svc, conf in event.payload.get("propagated_confidences", {}).items():
                state.confidences[svc] = conf
        
        elif event.event_type == LedgerEventType.SNAPSHOT:
            state.confidences.update(event.payload.get("confidences", {}))
    
    def reconstruct_snapshot(self, snapshot_id: str) -> Optional[Dict[str, float]]:
        """Reconstruct a snapshot from the event ledger."""
        for event in self.ledger.events:
            if event.snapshot_id == snapshot_id:
                return dict(event.payload.get("confidences", {}))
        return None
    
    def fork_from_event(self, event_id: str) -> 'ReplayEngine':
        """
        Create a new replay engine forked at a specific event.
        
        This is the basis for counterfactual branching:
        1. Replay up to event N
        2. Fork
        3. Inject a different event at N+1
        4. Compare outcomes
        
        Like git branch from a commit.
        """
        # Find the event
        fork_point = None
        for e in self.ledger.events:
            if e.event_id == event_id:
                fork_point = e
                break
        
        if not fork_point:
            return None
        
        # Replay up to that point
        fork_state = self.replay_until(fork_point.logical_time)
        
        # Create new engine with replayed state
        new_engine = ReplayEngine(self.ledger)
        new_engine.state = fork_state
        
        return new_engine
    
    def diff(self, logical_a: int, logical_b: int) -> Dict[str, float]:
        """Compute confidence delta between two logical times."""
        state_a = self.replay_until(logical_a)
        state_b = self.replay_until(logical_b)
        
        all_services = set(state_a.confidences.keys()) | set(state_b.confidences.keys())
        diffs = {}
        
        for svc in all_services:
            c_a = state_a.confidences.get(svc, 1.0)
            c_b = state_b.confidences.get(svc, 1.0)
            diffs[svc] = round(c_b - c_a, 2)
        
        return diffs
