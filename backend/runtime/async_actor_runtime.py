"""
NeXifyAI — Async Epistemic Actor Runtime (R3)
asyncio-based actor system replacing ThreadPoolExecutor.

Each actor is a lightweight async task with:
- async mailbox (asyncio.Queue) — cooperative, not thread-blocking
- deterministic state transitions — message-order-dependent, not timing-dependent
- zero global locks — actors own their state exclusively

Why async over threads:
  - 10k actors on one event loop vs 10k threads (GIL, context switching)
  - Deterministic replay: same message order = same outcome
  - IO-heavy workloads (probes, HTTP, DB) benefit from cooperative scheduling
  - Counterfactual reproducibility requires deterministic concurrency

Architecture:
  EventBus
   ├── AsyncActor(mailbox) — "backend"
   ├── AsyncActor(mailbox) — "qdrant-primary"
   ├── AsyncActor(mailbox) — "redis"
   └── AsyncActor(mailbox) — "supabase-db"
  
  await mailbox.get()  — cooperative, non-blocking
  NOT thread.submit() — preemptive, non-deterministic
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Coroutine
from enum import Enum


class AsyncActorState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"       # Waiting for external probe result
    DEGRADED = "degraded"
    RECOVERING = "recovering"


@dataclass  
class AsyncMessage:
    """Immutable async message between actors."""
    msg_id: str
    msg_type: str
    sender: str
    target: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None  # For tracing causal chains


@dataclass
class AsyncActor:
    """
    Async actor — owns its state, communicates via mailbox.
    
    Like Erlang processes or Akka actors, but Python-native asyncio.
    No shared state. No global locks. Deterministic per message ordering.
    """
    service: str
    local_confidence: float = 1.0
    effective_confidence: float = 1.0
    state: AsyncActorState = AsyncActorState.IDLE
    
    # Local memory (actor-owned, never shared)
    parents: Dict[str, float] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    contradictions: List[Dict] = field(default_factory=list)
    recovery_history: List[Dict] = field(default_factory=list)
    
    # Async mailbox (cooperative — not thread-blocking)
    mailbox: asyncio.Queue = field(default_factory=asyncio.Queue)
    
    # Version tracking (for cache invalidation + deterministic replay)
    version: int = 0
    epoch: int = 0
    
    # Stats
    messages_processed: int = 0
    total_processing_time_ms: float = 0.0
    
    async def run(self, bus: 'AsyncEventBus'):
        """
        Main actor loop. Runs until stopped.
        
        Cooperative: yields at `await mailbox.get()` — other actors run while waiting.
        NOT preemptive: no thread switching mid-computation.
        """
        while True:
            msg = await self.mailbox.get()
            self.state = AsyncActorState.PROCESSING
            start = time.time()
            
            try:
                if msg.msg_type == "confidence_update":
                    await self._handle_confidence_update(msg, bus)
                elif msg.msg_type == "contradiction":
                    await self._handle_contradiction(msg, bus)
                elif msg.msg_type == "recovery":
                    await self._handle_recovery(msg, bus)
                elif msg.msg_type == "propagate":
                    await self._handle_propagate(msg, bus)
                elif msg.msg_type == "stop":
                    break
            except Exception as e:
                self.contradictions.append({
                    "diagnosis": f"Actor error: {e}",
                    "timestamp": time.time(),
                })
            finally:
                elapsed = (time.time() - start) * 1000
                self.total_processing_time_ms += elapsed
                self.messages_processed += 1
                self.state = AsyncActorState.IDLE
                self.mailbox.task_done()
    
    async def _handle_confidence_update(self, msg: AsyncMessage, bus: 'AsyncEventBus'):
        """Parent confidence changed — recompute and propagate to children."""
        old = self.effective_confidence
        
        parent_product = 1.0
        for parent_id, weight in self.parents.items():
            parent_confidence = msg.data.get(f"{parent_id}_confidence", 1.0)
            parent_product *= parent_confidence * weight
        
        new_confidence = round(self.local_confidence * parent_product, 2)
        
        if abs(old - new_confidence) > 0.001:
            self.effective_confidence = new_confidence
            self.version += 1
            
            # Propagate to children (non-blocking publish)
            for child_id in self.children:
                await bus.publish(AsyncMessage(
                    msg_id=f"prop-{self.version}",
                    msg_type="confidence_update",
                    sender=self.service,
                    target=child_id,
                    data={f"{self.service}_confidence": self.effective_confidence},
                    correlation_id=msg.correlation_id,
                ))
    
    async def _handle_contradiction(self, msg: AsyncMessage, bus: 'AsyncEventBus'):
        """Log a contradiction and notify dependents."""
        self.contradictions.append({
            "diagnosis": msg.data.get("diagnosis", ""),
            "observer": msg.data.get("observer", ""),
            "timestamp": time.time(),
        })
        
        if len(self.contradictions) > 10:
            self.contradictions = self.contradictions[-10:]
        
        # Contradictions degrade confidence
        self.local_confidence *= 0.8
        self.version += 1
    
    async def _handle_recovery(self, msg: AsyncMessage, bus: 'AsyncEventBus'):
        """Execute recovery and propagate result."""
        self.state = AsyncActorState.RECOVERING
        action = msg.data.get("action", "unknown")
        
        # Recovery restores confidence
        self.local_confidence = min(1.0, self.local_confidence + 0.3)
        self.version += 1
        self.state = AsyncActorState.IDLE
        
        self.recovery_history.append({
            "action": action,
            "timestamp": time.time(),
            "new_confidence": self.local_confidence,
        })
        
        # Notify children of recovery
        for child_id in self.children:
            await bus.publish(AsyncMessage(
                msg_id=f"rec-{self.version}",
                msg_type="confidence_update",
                sender=self.service,
                target=child_id,
                data={f"{self.service}_confidence": self.effective_confidence},
                correlation_id=msg.correlation_id,
            ))
    
    async def _handle_propagate(self, msg: AsyncMessage, bus: 'AsyncEventBus'):
        """Propagation request — same as confidence update."""
        await self._handle_confidence_update(msg, bus)
    
    async def send(self, msg: AsyncMessage):
        """Send a message to this actor's mailbox."""
        await self.mailbox.put(msg)
    
    def stats(self) -> Dict:
        return {
            "service": self.service,
            "state": self.state.value,
            "version": self.version,
            "local_confidence": self.local_confidence,
            "effective_confidence": self.effective_confidence,
            "children": len(self.children),
            "contradictions": len(self.contradictions),
            "messages_processed": self.messages_processed,
            "mailbox_size": self.mailbox.qsize(),
            "avg_processing_ms": round(self.total_processing_time_ms / max(1, self.messages_processed), 2),
        }


# ══════════════════════════════════════════════
# ASYNC EVENT BUS
# ══════════════════════════════════════════════

class AsyncEventBus:
    """
    Asynchronous event bus for actor messaging.
    
    NOT a central orchestrator — just message routing infrastructure.
    Each actor has its own mailbox. The bus only routes messages.
    
    Deterministic guarantee: messages to the same actor are delivered in order.
    Cross-actor ordering is non-deterministic (by design — actors are independent).
    """
    
    def __init__(self):
        self.actors: Dict[str, AsyncActor] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._load_actors()
    
    def _load_actors(self):
        """Create actors from canonical service registry."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        for svc_id, svc in CANONICAL_REGISTRY.items():
            actor = AsyncActor(service=svc_id)
            for dep_id in svc.depends_on:
                actor.parents[dep_id] = 0.8
            self.actors[svc_id] = actor
        
        # Wire children
        for svc_id, actor in self.actors.items():
            for parent_id in actor.parents:
                if parent_id in self.actors:
                    self.actors[parent_id].children.append(svc_id)
    
    async def publish(self, msg: AsyncMessage):
        """Publish a message to the target actor's mailbox. Non-blocking."""
        target = self.actors.get(msg.target)
        if target:
            await target.send(msg)
    
    async def broadcast(self, msg_type: str, data: Dict = None, exclude: str = None, correlation_id: str = None):
        """Publish a message to ALL actors."""
        tasks = []
        for svc_id, actor in self.actors.items():
            if svc_id == exclude:
                continue
            tasks.append(self.publish(AsyncMessage(
                msg_id=f"bc-{int(time.time())}",
                msg_type=msg_type,
                sender="system",
                target=svc_id,
                data=data or {},
                correlation_id=correlation_id,
            )))
        await asyncio.gather(*tasks)  # Parallel publish
    
    async def start(self):
        """Start all actors. Each runs as an independent async task."""
        self._running = True
        for svc_id, actor in self.actors.items():
            task = asyncio.create_task(actor.run(self))
            self._tasks[svc_id] = task
    
    async def stop(self):
        """Gracefully stop all actors."""
        await self.broadcast("stop")
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
    
    async def inject_and_measure(self, service: str, action: str, correlation_id: str = None) -> Dict:
        """
        Inject a recovery action and measure the cascade.
        
        This is the E9 substrate: deterministic simulation of a counterfactual.
        Returns pre/post confidence deltas across the system.
        """
        cid = correlation_id or f"sim-{int(time.time())}"
        
        # Snapshot pre-action state
        pre_snapshot = {svc: a.effective_confidence for svc, a in self.actors.items()}
        
        # Inject recovery action
        await self.publish(AsyncMessage(
            msg_id=f"inject-{int(time.time())}",
            msg_type="recovery",
            sender="simulator",
            target=service,
            data={"action": action},
            correlation_id=cid,
        ))
        
        # Wait for cascade to settle (all actors idle)
        await self._wait_idle()
        
        # Snapshot post-action state
        post_snapshot = {svc: a.effective_confidence for svc, a in self.actors.items()}
        
        # Compute deltas
        gains = {}
        total_gain = 0.0
        for svc in pre_snapshot:
            delta = post_snapshot.get(svc, 0) - pre_snapshot[svc]
            gains[svc] = round(delta, 2)
            total_gain += delta
        
        avg_gain = total_gain / max(1, len(gains))
        
        return {
            "correlation_id": cid,
            "action": action,
            "service": service,
            "average_confidence_gain": round(avg_gain, 3),
            "per_service_gains": gains,
            "pre_avg_confidence": round(sum(pre_snapshot.values()) / len(pre_snapshot), 2),
            "post_avg_confidence": round(sum(post_snapshot.values()) / len(post_snapshot), 2),
            "convergence": "converged" if avg_gain > 0.05 else "regressed",
            "actor_count": len(self.actors),
        }
    
    async def simulate_parallel(self, service: str, plans: List[Dict]) -> List[Dict]:
        """
        Speculative parallelism: simulate multiple recovery plans concurrently.
        
        Each plan runs in a forked actor system (snapshot clone),
        then results are ranked by epistemic utility.
        
        This is E9: counterfactual simulation, NOT LLM speculation.
        """
        async def simulate_one(plan: Dict) -> Dict:
            """Simulate one plan in isolation."""
            # Fork: create new bus with same initial state
            fork = AsyncEventBus()
            # Copy current confidences
            for svc, actor in self.actors.items():
                if svc in fork.actors:
                    fork.actors[svc].local_confidence = actor.local_confidence
                    fork.actors[svc].effective_confidence = actor.effective_confidence
            
            await fork.start()
            result = await fork.inject_and_measure(service, plan["action"])
            await fork.stop()
            return {**result, "plan": plan}
        
        # Run all simulations concurrently
        tasks = [simulate_one(plan) for plan in plans]
        results = await asyncio.gather(*tasks)
        
        # Rank by expected gain
        results.sort(key=lambda r: (-r["average_confidence_gain"], r.get("blast_radius", 999)))
        
        return results
    
    async def _wait_idle(self, timeout: float = 5.0):
        """Wait until all actors are idle (mailboxes empty, not processing)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            all_idle = all(
                a.state == AsyncActorState.IDLE and a.mailbox.empty()
                for a in self.actors.values()
            )
            if all_idle:
                return
            await asyncio.sleep(0.01)
    
    def system_stats(self) -> Dict:
        """Synchronous snapshot of actor system state."""
        actor_stats = {svc: a.stats() for svc, a in self.actors.items()}
        return {
            "total_actors": len(self.actors),
            "active_tasks": len(self._tasks),
            "running": self._running,
            "total_messages": sum(a.messages_processed for a in self.actors.values()),
            "actors": actor_stats,
        }


# ══════════════════════════════════════════════
# SYNC WRAPPER (for non-async contexts)
# ══════════════════════════════════════════════

def run_async(coro):
    """Run an async coroutine in a sync context."""
    try:
        loop = asyncio.get_running_loop()
        # Already in async context — use nested event loop
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No running loop — create one
        return asyncio.run(coro)
