"""
NeXifyAI — Epistemic Actor Runtime (R2)
Each service is an independent EpistemicActor with:
- local memory (confidence, contradictions, recovery history)
- local propagation (only recomputes own + children)
- event-driven communication (not global orchestration)

Pattern: Actor Model (Akka/Orleans/Ray-style)
  Events propagate between actors instead of central orchestration.
  Each actor owns its state. No shared mutable state.

Benefits:
  - Parallel execution: actors process events independently
  - Isolation: one service's degradation doesn't block others
  - Scalability: add actors without central bottleneck
  - Speculative parallelism: simulate multiple recovery plans concurrently
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed


class ActorState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    DEGRADED = "degraded"
    RECOVERING = "recovering"


@dataclass
class ActorMessage:
    """Immutable message between actors."""
    msg_id: str
    msg_type: str         # "confidence_update", "contradiction", "recovery", "propagate"
    sender: str
    target: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass  
class EpistemicActor:
    """
    Independent actor for one service.
    
    Owns its state. Communicates via messages.
    No central orchestrator controls it.
    """
    service: str
    local_confidence: float = 1.0
    effective_confidence: float = 1.0
    state: ActorState = ActorState.IDLE
    
    # Local memory
    parents: Dict[str, float] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    contradictions: List[Dict] = field(default_factory=list)
    recovery_history: List[Dict] = field(default_factory=list)
    
    # Messaging
    inbox: deque = field(default_factory=deque)
    outbox: deque = field(default_factory=deque)
    
    # Performance
    messages_processed: int = 0
    last_active: float = field(default_factory=time.time)
    
    def receive(self, msg: ActorMessage):
        """Receive a message from another actor."""
        self.inbox.append(msg)
        self.last_active = time.time()
    
    def process(self, registry: Dict[str, 'EpistemicActor'] = None):
        """
        Process all pending messages.
        
        Each message type triggers specific behavior:
        - confidence_update: recompute effective confidence
        - contradiction: log and propagate to children
        - recovery: execute recovery, re-observe, propagate result
        """
        while self.inbox:
            msg = self.inbox.popleft()
            self.state = ActorState.PROCESSING
            self.messages_processed += 1
            
            if msg.msg_type == "confidence_update":
                self._handle_confidence_update(msg)
            elif msg.msg_type == "contradiction":
                self._handle_contradiction(msg)
            elif msg.msg_type == "propagate":
                self._handle_propagate(msg, registry)
            elif msg.msg_type == "recovery":
                self._handle_recovery(msg, registry)
            
            self.state = ActorState.IDLE
    
    def _handle_confidence_update(self, msg: ActorMessage):
        """Parent confidence changed — recompute and propagate to children."""
        old = self.effective_confidence
        
        # Recompute from parent confidences (simplified — real version uses full propagation)
        parent_product = 1.0
        for parent_id, weight in self.parents.items():
            parent_confidence = msg.data.get(f"{parent_id}_confidence", 1.0)
            parent_product *= parent_confidence * weight
        
        self.effective_confidence = round(self.local_confidence * parent_product, 2)
        
        if abs(old - self.effective_confidence) > 0.01:
            # Propagate to children
            for child_id in self.children:
                self.outbox.append(ActorMessage(
                    msg_id=f"prop-{int(time.time())}",
                    msg_type="confidence_update",
                    sender=self.service,
                    target=child_id,
                    data={f"{self.service}_confidence": self.effective_confidence},
                ))
    
    def _handle_contradiction(self, msg: ActorMessage):
        """Log a contradiction."""
        self.contradictions.append({
            "diagnosis": msg.data.get("diagnosis", ""),
            "observer": msg.data.get("observer", ""),
            "timestamp": time.time(),
        })
        
        if len(self.contradictions) > 10:
            self.contradictions = self.contradictions[-10:]
    
    def _handle_propagate(self, msg: ActorMessage, registry: Dict[str, 'EpistemicActor']):
        """Propagation request — recompute and forward."""
        self._handle_confidence_update(msg)
    
    def _handle_recovery(self, msg: ActorMessage, registry: Dict[str, 'EpistemicActor']):
        """Execute recovery and propagate result."""
        self.state = ActorState.RECOVERING
        action = msg.data.get("action", "unknown")
        
        # Simulate recovery (in production: actual restart/probe)
        self.local_confidence = 0.9  # Recovery typically restores confidence
        self.state = ActorState.IDLE
        
        self.recovery_history.append({
            "action": action,
            "result": "simulated",
            "timestamp": time.time(),
        })
        
        # Propagate recovery to children
        for child_id in self.children:
            self.outbox.append(ActorMessage(
                msg_id=f"rec-prop-{int(time.time())}",
                msg_type="confidence_update",
                sender=self.service,
                target=child_id,
                data={f"{self.service}_confidence": self.effective_confidence},
            ))
    
    def stats(self) -> Dict:
        return {
            "service": self.service,
            "state": self.state.value,
            "local_confidence": self.local_confidence,
            "effective_confidence": self.effective_confidence,
            "children": len(self.children),
            "contradictions": len(self.contradictions),
            "messages_processed": self.messages_processed,
            "inbox_size": len(self.inbox),
            "outbox_size": len(self.outbox),
        }


# ══════════════════════════════════════════════
# ACTOR SYSTEM (Orchestrator-light)
# ══════════════════════════════════════════════

class ActorSystem:
    """
    Lightweight actor runtime.
    
    Manages actor lifecycle, message routing, and parallel execution.
    NOT a central orchestrator — just message routing infrastructure.
    """
    
    MAX_PARALLEL_ACTORS = 8
    
    def __init__(self):
        self.actors: Dict[str, EpistemicActor] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_PARALLEL_ACTORS)
        self._load_actors()
    
    def _load_actors(self):
        """Create actors from canonical service registry."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        for svc_id, svc in CANONICAL_REGISTRY.items():
            actor = EpistemicActor(service=svc_id)
            for dep_id in svc.depends_on:
                actor.parents[dep_id] = 0.8
            self.actors[svc_id] = actor
        
        # Wire children
        for svc_id, actor in self.actors.items():
            for parent_id in actor.parents:
                if parent_id in self.actors:
                    self.actors[parent_id].children.append(svc_id)
    
    def send(self, msg: ActorMessage):
        """Route a message to the target actor."""
        target = self.actors.get(msg.target)
        if target:
            target.receive(msg)
    
    def broadcast(self, msg_type: str, data: Dict = None, exclude: str = None):
        """Send a message to all actors."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        for svc_id in self.actors:
            if svc_id == exclude:
                continue
            self.send(ActorMessage(
                msg_id=f"bc-{int(time.time())}",
                msg_type=msg_type,
                sender="system",
                target=svc_id,
                data=data or {},
            ))
    
    def process_all(self, parallel: bool = True) -> Dict[str, Dict]:
        """
        Process all actors' inboxes.
        
        If parallel=True: actors process concurrently (speculative parallelism).
        If parallel=False: actors process sequentially (deterministic order).
        """
        if parallel:
            # Parallel processing via thread pool
            futures = {}
            for svc_id, actor in self.actors.items():
                if actor.inbox:
                    future = self.executor.submit(actor.process, self.actors)
                    futures[future] = svc_id
            
            for future in as_completed(futures):
                pass  # Results collected via actor state
        else:
            for actor in self.actors.values():
                if actor.inbox:
                    actor.process(self.actors)
        
        # Collect and deliver outbox messages
        for actor in self.actors.values():
            while actor.outbox:
                msg = actor.outbox.popleft()
                self.send(msg)
        
        return {svc: a.stats() for svc, a in self.actors.items()}
    
    def simulate_parallel_recovery(self, service: str, plans: List[Dict]) -> List[Dict]:
        """
        Speculative parallelism: simulate multiple recovery plans concurrently.
        
        Each plan is simulated in parallel. Results are ranked by:
        - Expected confidence gain
        - Blast radius
        - Risk level
        
        Returns ranked recovery plans.
        """
        results = []
        
        def simulate_plan(plan: Dict) -> Dict:
            """Simulate one recovery plan."""
            actor = self.actors.get(service)
            if not actor:
                return {"plan": plan, "error": "Actor not found"}
            
            # Estimate gain (simplified)
            gain = 0.9 - actor.effective_confidence
            blast = len(actor.children)
            
            return {
                "plan": plan,
                "expected_gain": round(gain, 2),
                "blast_radius": blast,
                "risk": "low" if blast <= 2 else "medium",
                "service": service,
            }
        
        # Execute all plans in parallel
        futures = [self.executor.submit(simulate_plan, plan) for plan in plans]
        for future in as_completed(futures):
            results.append(future.result())
        
        # Rank by expected gain (descending), then blast radius (ascending)
        results.sort(key=lambda r: (-r["expected_gain"], r["blast_radius"]))
        
        return results
    
    def system_stats(self) -> Dict:
        """Full actor system statistics."""
        actor_stats = {svc: a.stats() for svc, a in self.actors.items()}
        
        return {
            "total_actors": len(self.actors),
            "active_actors": len([a for a in self.actors.values() if a.state != ActorState.IDLE]),
            "total_messages_processed": sum(a.messages_processed for a in self.actors.values()),
            "actors": actor_stats,
        }
