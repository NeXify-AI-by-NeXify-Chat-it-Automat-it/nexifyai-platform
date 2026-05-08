"""
NeXifyAI — Memory Confidence Index (E8)
Epistemically versioned operational memory.

Every stored memory gets:
- confidence_at_capture: how confident were we when this was saved?
- current_estimated_validity: how likely is this still true?
- topology_version: which dependency graph was this recorded under?
- dependency_hash: checksum of the dependency graph at capture time
- stale_after: hours until this memory expires without revalidation
- contradicted_by: list of observations that contradict this memory

Principle:
  "A memory is not truth. A memory is a time-bound, topology-bound,
   confidence-scored observation that decays without revalidation."

Without this, old rollback candidates appear "high confidence" forever,
even when the topology they were recorded under no longer exists.
That is temporal epistemic drift — and it destroys autonomous governance.
"""

import time
import hashlib
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum


class MemoryValidity(Enum):
    FRESH = "fresh"               # < 24h, topology matches
    VALID = "valid"               # < 72h, topology close
    AGING = "aging"               # 72h-7d, topology drifted
    STALE = "stale"               # 7d-30d, requires revalidation
    EXPIRED = "expired"           # > 30d, should not be used
    CONTRADICTED = "contradicted" # Actively contradicted by current observations


@dataclass
class IndexedMemory:
    """A memory entry with epistemic metadata."""
    id: str
    content: str
    category: str                      # incident, recovery, decision, observation, topology
    
    # Temporal-epistemic metadata
    captured_at: float = field(default_factory=time.time)
    confidence_at_capture: float = 1.0    # Original confidence when saved
    current_estimated_validity: float = 1.0  # Decayed estimate of current truth
    last_validated_at: Optional[float] = None
    
    # Topology binding
    topology_version: int = 0
    dependency_hash: str = ""
    dependency_count: int = 0
    
    # Lifecycle
    stale_after_hours: int = 72        # Hours until this memory goes stale
    validity: MemoryValidity = MemoryValidity.FRESH
    
    # Contradiction tracking
    contradicted_by: List[str] = field(default_factory=list)
    contradiction_count: int = 0
    
    # Revalidation
    requires_revalidation: bool = False
    revalidation_attempts: int = 0
    max_revalidation_attempts: int = 3
    
    # Source
    observer: str = "hermes"
    evidence_hash: str = ""            # Content hash for deduplication
    
    def __post_init__(self):
        if not self.evidence_hash:
            self.evidence_hash = hashlib.sha256(
                (self.content + str(self.captured_at)).encode()
            ).hexdigest()[:16]
        self._recompute_validity()
    
    @property
    def age_hours(self) -> float:
        return (time.time() - self.captured_at) / 3600
    
    @property
    def hours_since_validation(self) -> float:
        if self.last_validated_at:
            return (time.time() - self.last_validated_at) / 3600
        return self.age_hours
    
    def _recompute_validity(self):
        """Recompute current estimated validity with decay."""
        hours = self.age_hours
        decay = 0.95 ** (hours / 24)  # Daily decay, not hourly (memory ages slower)
        
        self.current_estimated_validity = round(
            self.confidence_at_capture * decay, 2
        )
        
        # Contradiction penalty
        if self.contradiction_count > 0:
            self.current_estimated_validity *= (0.5 ** self.contradiction_count)
            self.validity = MemoryValidity.CONTRADICTED
            return
        
        # Staleness
        if hours > self.stale_after_hours * 2:  # > 2x stale_after = 144h
            self.validity = MemoryValidity.EXPIRED
        elif hours > self.stale_after_hours:    # > stale_after
            self.validity = MemoryValidity.STALE
        elif hours > self.stale_after_hours / 2:  # > 36h
            self.validity = MemoryValidity.AGING
        elif hours > 24:
            self.validity = MemoryValidity.VALID
        else:
            self.validity = MemoryValidity.FRESH
        
        # Revalidation trigger
        if self.validity in (MemoryValidity.STALE, MemoryValidity.EXPIRED):
            if self.revalidation_attempts < self.max_revalidation_attempts:
                self.requires_revalidation = True
    
    def can_be_used_for(self, purpose: str) -> Tuple[bool, str]:
        """
        Check if this memory can be used for a specific purpose.
        
        Purposes: 'rollback', 'counterfactual', 'deploy-gate', 'recovery'
        """
        if self.validity == MemoryValidity.EXPIRED:
            return False, f"Memory expired ({self.age_hours:.0f}h old)"
        
        if self.validity == MemoryValidity.CONTRADICTED:
            return False, f"Memory contradicted by {self.contradiction_count} observations"
        
        if self.validity == MemoryValidity.STALE:
            if purpose in ('rollback', 'counterfactual'):
                return False, f"Memory stale ({self.age_hours:.0f}h) — cannot use for critical {purpose}"
            return True, "Stale but acceptable for non-critical use"
        
        if self.current_estimated_validity < 0.5:
            return False, f"Validity too low: {self.current_estimated_validity}"
        
        if purpose == 'rollback' and self.current_estimated_validity < 0.8:
            return False, "Rollback requires validity ≥ 0.8"
        
        return True, "Valid"


# ══════════════════════════════════════════════
# MEMORY CONFIDENCE ENGINE
# ══════════════════════════════════════════════

class MemoryConfidenceEngine:
    """
    Indexes and manages epistemic metadata for operational memories.
    
    Integrates with brain.db for persistence, adds temporal-epistemic
    indexing layer for autonomous governance decisions.
    """
    
    DECAY_RATE = 0.95  # Per 24h (memories decay slower than runtime confidence)
    BRAIN_DB = "/opt/data/brain/brain.db"
    
    def __init__(self):
        self.memories: Dict[str, IndexedMemory] = {}
        self._current_topology_version = self._compute_topology_version()
        self._current_dependency_hash = self._compute_dependency_hash()
    
    def _compute_topology_version(self) -> int:
        """Compute current topology version from service registry."""
        try:
            from backend.runtime.service_registry import CANONICAL_REGISTRY
            return len(CANONICAL_REGISTRY)
        except Exception:
            return 0
    
    def _compute_dependency_hash(self) -> str:
        """Compute checksum of current dependency graph."""
        try:
            from backend.runtime.service_registry import CANONICAL_REGISTRY
            deps = json.dumps(
                {svc: svc.depends_on for svc in CANONICAL_REGISTRY.values()},
                sort_keys=True
            )
            return hashlib.sha256(deps.encode()).hexdigest()[:16]
        except Exception:
            return "unknown"
    
    def index(
        self,
        content: str,
        category: str,
        confidence: float = 1.0,
        observer: str = "hermes",
        stale_after_hours: int = 72,
    ) -> IndexedMemory:
        """Index a new memory with epistemic metadata."""
        memory = IndexedMemory(
            id=f"mem-{int(time.time())}-{hashlib.sha256(content.encode()).hexdigest()[:8]}",
            content=content,
            category=category,
            confidence_at_capture=confidence,
            captured_at=time.time(),
            topology_version=self._current_topology_version,
            dependency_hash=self._current_dependency_hash,
            dependency_count=self._current_topology_version,
            stale_after_hours=stale_after_hours,
            observer=observer,
        )
        
        self.memories[memory.id] = memory
        self._persist(memory)
        
        return memory
    
    def revalidate(self, memory_id: str, new_confidence: float = None) -> Optional[IndexedMemory]:
        """Revalidate a memory against current topology and observations."""
        memory = self.memories.get(memory_id)
        if not memory:
            return None
        
        memory.last_validated_at = time.time()
        memory.revalidation_attempts += 1
        memory.requires_revalidation = False
        
        # Update topology binding
        memory.topology_version = self._current_topology_version
        memory.dependency_hash = self._current_dependency_hash
        memory.dependency_count = self._current_topology_version
        
        # Update confidence if provided
        if new_confidence is not None:
            memory.confidence_at_capture = max(0.1, min(1.0, new_confidence))
        
        memory._recompute_validity()
        self._persist(memory)
        
        return memory
    
    def contradict(self, memory_id: str, contradiction_source: str):
        """Mark a memory as contradicted by a current observation."""
        memory = self.memories.get(memory_id)
        if not memory:
            return
        
        memory.contradicted_by.append(contradiction_source)
        memory.contradiction_count = len(memory.contradicted_by)
        memory._recompute_validity()
        self._persist(memory)
    
    def decay_all(self) -> Dict[str, MemoryValidity]:
        """Apply temporal decay to all indexed memories."""
        updates = {}
        for memory in self.memories.values():
            old_validity = memory.validity
            memory._recompute_validity()
            if memory.validity != old_validity:
                updates[memory.id] = memory.validity
        return updates
    
    def find_usable_memories(
        self,
        category: str = None,
        purpose: str = "recovery",
        min_validity: float = 0.5,
    ) -> List[IndexedMemory]:
        """Find memories that are valid for a specific purpose."""
        self.decay_all()
        
        usable = []
        for memory in self.memories.values():
            if category and memory.category != category:
                continue
            
            can_use, _ = memory.can_be_used_for(purpose)
            if can_use and memory.current_estimated_validity >= min_validity:
                usable.append(memory)
        
        return sorted(usable, key=lambda m: -m.current_estimated_validity)
    
    def topology_drift_report(self) -> Dict:
        """Report on memories whose topology has drifted from current state."""
        drifted = []
        for memory in self.memories.values():
            if memory.topology_version != self._current_topology_version:
                drifted.append({
                    "id": memory.id,
                    "category": memory.category,
                    "captured_topology_v": memory.topology_version,
                    "current_topology_v": self._current_topology_version,
                    "dependency_hash_match": memory.dependency_hash == self._current_dependency_hash,
                    "age_hours": round(memory.age_hours, 1),
                    "validity": memory.validity.value,
                })
        
        return {
            "current_topology_version": self._current_topology_version,
            "current_dependency_hash": self._current_dependency_hash,
            "total_memories": len(self.memories),
            "drifted_memories": len(drifted),
            "drift_ratio": len(drifted) / max(1, len(self.memories)),
            "memories": drifted,
        }
    
    def report(self) -> Dict:
        """Full memory confidence report."""
        self.decay_all()
        
        by_validity = {}
        for v in MemoryValidity:
            count = len([m for m in self.memories.values() if m.validity == v])
            if count > 0:
                by_validity[v.value] = count
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_memories": len(self.memories),
            "topology_version": self._current_topology_version,
            "dependency_hash": self._current_dependency_hash,
            "by_validity": by_validity,
            "average_validity": round(
                sum(m.current_estimated_validity for m in self.memories.values()) / max(1, len(self.memories)),
                2
            ),
            "requiring_revalidation": len([m for m in self.memories.values() if m.requires_revalidation]),
            "contradicted": len([m for m in self.memories.values() if m.validity == MemoryValidity.CONTRADICTED]),
            "memories": [
                {
                    "id": m.id[:20],
                    "category": m.category,
                    "confidence_at_capture": m.confidence_at_capture,
                    "current_validity": m.current_estimated_validity,
                    "age_hours": round(m.age_hours, 1),
                    "validity": m.validity.value,
                    "contradictions": m.contradiction_count,
                }
                for m in sorted(self.memories.values(), key=lambda m: -m.age_hours)[:20]
            ],
        }
    
    def _persist(self, memory: IndexedMemory):
        """Persist indexed memory to brain.db."""
        try:
            conn = sqlite3.connect(self.BRAIN_DB)
            conn.execute("""
                INSERT OR REPLACE INTO memories (id, content, category, source, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                memory.id,
                json.dumps({
                    "content": memory.content,
                    "confidence_at_capture": memory.confidence_at_capture,
                    "current_validity": memory.current_estimated_validity,
                    "topology_version": memory.topology_version,
                    "dependency_hash": memory.dependency_hash,
                    "validity": memory.validity.value,
                    "contradicted_by": memory.contradicted_by,
                    "captured_at": memory.captured_at,
                    "observer": memory.observer,
                }),
                f"indexed_{memory.category}",
                "memory_confidence_engine",
                datetime.fromtimestamp(memory.captured_at, tz=timezone.utc).isoformat(),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[E8] Persist error: {e}")
