"""
NeXifyAI — Hierarchical Memory Compaction (R1.3)
Reduces LLM context from 400K to structured summaries.

NOT: full conversational replay
BUT:  raw events → distilled causal summaries → indexed operational memory → retrieval only when needed

Layers:
  L0: Raw operational events (append-only, never in LLM context)
  L1: Compressed causal summaries (1-2 sentences per incident/recovery)
  L2: Indexed patterns (categorized, searchable, confidence-scored)
  L3: Active context (only what's relevant RIGHT NOW — <5% of total memory)
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import defaultdict


# ══════════════════════════════════════════════
# COMPACTION LAYERS
# ══════════════════════════════════════════════

@dataclass
class CompressedEvent:
    """L1: A single compressed operational event (1-2 sentences)."""
    id: str
    timestamp: float
    category: str        # incident, recovery, observation, decision, deployment
    service: str
    summary: str         # 1-2 sentence distilled version of what happened
    outcome: str         # converged, regressed, partial, unknown
    confidence: float
    evidence_hash: str   # Links to raw L0 events for audit


@dataclass
class IndexedPattern:
    """L2: A recognized operational pattern."""
    pattern_id: str
    pattern_name: str    # e.g., "port_binding_127.0.0.1_causes_container_isolation"
    occurrences: int
    first_seen: float
    last_seen: float
    services_affected: List[str]
    typical_recovery: str
    success_rate: float  # How often recovery works
    compressed_events: List[str] = field(default_factory=list)  # Event IDs


@dataclass  
class ActiveContext:
    """L3: Only what's relevant RIGHT NOW."""
    current_incident: Optional[str] = None
    recent_recoveries: List[str] = field(default_factory=list)
    active_contradictions: List[str] = field(default_factory=list)
    pending_decisions: List[str] = field(default_factory=list)
    total_tokens_estimate: int = 0


class MemoryCompactor:
    """
    Hierarchical memory compaction engine.
    
    Transforms 400K of raw context into:
      L0: Raw events (stored, never in LLM)
      L1: <5K of compressed summaries
      L2: <2K of indexed patterns  
      L3: <1K of active context
    
    Total LLM context: <8K instead of 400K — 50x reduction.
    """
    
    MAX_ACTIVE_EVENTS = 20       # Only keep most recent in L3
    MAX_COMPRESSED_EVENTS = 200  # L1 capacity
    PATTERN_MIN_OCCURRENCES = 2  # Min occurrences to become a pattern
    
    def __init__(self):
        self.compressed_events: List[CompressedEvent] = []
        self.patterns: Dict[str, IndexedPattern] = {}
        self.active_context = ActiveContext()
        self._compaction_count = 0
    
    def compact(self, raw_event: Dict[str, Any]) -> CompressedEvent:
        """
        Compress a raw operational event into a 1-2 sentence summary.
        
        Raw:  full JSON with 20+ fields, timestamps, observer data, probe results
        L1:   "Qdrant unreachable from Hermes: 127.0.0.1 port binding. Recovery: restart → CONVERGED (conf=0.95)"
        """
        category = raw_event.get("type", "observation")
        service = raw_event.get("service", "unknown")
        data = raw_event.get("data", {})
        
        # Build compressed summary based on event type
        if category == "recovery":
            convergence = data.get("convergence", "unknown")
            confidence = data.get("confidence", 0)
            action = data.get("action", "unknown")
            summary = f"{service}: {action} → {convergence.upper()} (conf={confidence:.2f})"
            outcome = convergence
        
        elif category == "contradiction":
            diagnosis = data.get("diagnosis", "")
            summary = f"{service} contradiction: {diagnosis[:100]}"
            outcome = "contradictory"
        
        elif category == "observation":
            confidence = data.get("effective_confidence", data.get("confidence", 0))
            level = data.get("level", "unknown")
            summary = f"{service} confidence={confidence:.2f} [{level}]"
            outcome = "converged" if confidence > 0.8 else "degraded"
        
        elif category == "deployment":
            confidence = data.get("confidence", 1.0)
            summary = f"Deploy {service}: confidence={confidence:.2f}"
            outcome = "converged" if confidence > 0.8 else "pending"
        
        else:
            summary = f"{service}: {str(data)[:100]}"
            outcome = "unknown"
        
        event = CompressedEvent(
            id=f"cmp-{self._compaction_count}",
            timestamp=raw_event.get("timestamp", time.time()),
            category=category,
            service=service,
            summary=summary,
            outcome=outcome,
            confidence=data.get("confidence", 0.5),
            evidence_hash=hashlib.sha256(str(raw_event).encode()).hexdigest()[:12],
        )
        
        self._compaction_count += 1
        self.compressed_events.append(event)
        
        # Prune old compressed events
        if len(self.compressed_events) > self.MAX_COMPRESSED_EVENTS:
            self.compressed_events = self.compressed_events[-self.MAX_COMPRESSED_EVENTS:]
        
        # Update patterns
        self._update_patterns(event)
        
        # Update active context
        self._update_active_context(event)
        
        return event
    
    def _update_patterns(self, event: CompressedEvent):
        """Recognize and index recurring operational patterns."""
        # Pattern: recovery outcomes per service
        if event.category == "recovery":
            pattern_name = f"recovery_{event.service}_{event.outcome}"
            if pattern_name not in self.patterns:
                self.patterns[pattern_name] = IndexedPattern(
                    pattern_id=pattern_name,
                    pattern_name=pattern_name,
                    occurrences=0,
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    services_affected=[event.service],
                    typical_recovery="unknown",
                    success_rate=0.0,
                )
            
            p = self.patterns[pattern_name]
            p.occurrences += 1
            p.last_seen = event.timestamp
            if event.service not in p.services_affected:
                p.services_affected.append(event.service)
            p.compressed_events.append(event.id)
            
            # Update success rate
            if event.outcome == "converged":
                converged = len([e for e in self.compressed_events 
                               if e.service == event.service and e.outcome == "converged"])
                total = len([e for e in self.compressed_events 
                           if e.service == event.service and e.category == "recovery"])
                p.success_rate = round(converged / max(1, total), 2)
        
        # Pattern: port binding issues
        if "127.0.0.1" in event.summary or "port binding" in event.summary.lower():
            pattern_name = "port_binding_causes_isolation"
            if pattern_name not in self.patterns:
                self.patterns[pattern_name] = IndexedPattern(
                    pattern_id=pattern_name,
                    pattern_name=pattern_name,
                    occurrences=0,
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    services_affected=[],
                    typical_recovery="Change port binding from 127.0.0.1 to 0.0.0.0",
                    success_rate=0.0,
                )
            self.patterns[pattern_name].occurrences += 1
            self.patterns[pattern_name].last_seen = event.timestamp
            if event.service not in self.patterns[pattern_name].services_affected:
                self.patterns[pattern_name].services_affected.append(event.service)
    
    def _update_active_context(self, event: CompressedEvent):
        """Update L3 active context — only the most relevant recent events."""
        # Only keep last N events in active context
        recent = self.compressed_events[-self.MAX_ACTIVE_EVENTS:]
        
        self.active_context.recent_recoveries = [
            e.summary for e in recent if e.category == "recovery"
        ][-5:]
        
        self.active_context.active_contradictions = [
            e.summary for e in recent if e.outcome == "contradictory"
        ][-3:]
        
        # Estimate token count (rough: ~1.3 tokens per character)
        total_chars = sum(len(e.summary) for e in recent)
        self.active_context.total_tokens_estimate = int(total_chars * 0.4)
    
    def get_llm_context(self) -> str:
        """
        Generate compact LLM context from L1+L2+L3.
        
        Max ~8K characters, ~3K tokens.
        vs. 400K raw context → 50x reduction.
        """
        lines = [
            "═══ OPERATIONAL CONTEXT (compacted) ═══",
            "",
            "RECENT EVENTS:",
        ]
        
        for e in self.compressed_events[-10:]:
            age_min = round((time.time() - e.timestamp) / 60)
            lines.append(f"  [{age_min}m ago] [{e.category}] {e.summary}")
        
        if self.active_context.active_contradictions:
            lines.append("")
            lines.append("ACTIVE CONTRADICTIONS:")
            for c in self.active_context.active_contradictions:
                lines.append(f"  ⚡ {c}")
        
        lines.append("")
        lines.append("RECOGNIZED PATTERNS:")
        
        for p in sorted(self.patterns.values(), key=lambda x: -x.occurrences)[:5]:
            lines.append(f"  📋 {p.pattern_name}: {p.occurrences}×, success={p.success_rate}")
        
        lines.append("")
        lines.append(f"Context size: ~{self.active_context.total_tokens_estimate} tokens (compacted from raw events)")
        
        return "\n".join(lines)
    
    def query(self, service: str = None, category: str = None, limit: int = 10) -> List[CompressedEvent]:
        """Query compressed events."""
        results = self.compressed_events
        if service:
            results = [e for e in results if e.service == service]
        if category:
            results = [e for e in results if e.category == category]
        return results[-limit:]
    
    def stats(self) -> Dict:
        """Compaction statistics."""
        raw_events_estimate = self._compaction_count
        compressed_size = sum(len(e.summary) for e in self.compressed_events)
        
        return {
            "compaction_count": self._compaction_count,
            "compressed_events": len(self.compressed_events),
            "recognized_patterns": len(self.patterns),
            "active_context_tokens": self.active_context.total_tokens_estimate,
            "compression_ratio": round(
                raw_events_estimate * 500 / max(1, compressed_size), 1
            ),  # ~500 chars per raw event vs compressed
            "estimated_savings": f"~{raw_events_estimate * 500 // 1000}K → ~{compressed_size // 1000}K ({round(compressed_size / max(1, raw_events_estimate * 5), 1)}%)",
        }
