"""
NeXifyAI — Unified Operational Memory (Fabrik: System C)

Implementiert die 5-Typen-Gedächtnistaxonomie nach dem kognitiven Modell:

  EPISODIC    — Vergangene Ereignisse, Delivery Runs, Incident History
  SEMANTIC    — Abstrahierte Fakten, Regeln, Policies, Allgemeinwissen
  PROCEDURAL  — Gelernte Abläufe, Skills, Entscheidungsstrategien
  GRAPH       — Entitätsbeziehungen, Kausalitäten, Organisationsstrukturen
  PARAMETRIC  — Wissen in Modellgewichten (via LLM/Embedding-Modelle)

NICHT: isolierte Speicher pro Typ
SONDERN: Konsolidierungspipeline mit Decay, Confidence, Cross-Type Retrieval

Kognitive Architektur:
  Sensorisch (Context Window) → Arbeitsgedächtnis (Prompt) → Langzeit (Store)
                                                              ├─ Episodic
                                                              ├─ Semantic
                                                              ├─ Procedural
                                                              └─ Graph
"""
import json
import time
import uuid
import hashlib
import sqlite3
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# MEMORY TYPE TAXONOMY
# ═══════════════════════════════════════════════════

class MemoryType(Enum):
    """Die 5 Gedächtnistypen nach dem kognitiven KI-Modell."""
    EPISODIC = "episodic"          # Vergangene Ereignisse, Dialoge, Delivery Runs
    SEMANTIC = "semantic"          # Fakten, Regeln, Policies, abstrahiertes Wissen
    PROCEDURAL = "procedural"      # Skills, Workflows, Entscheidungsmuster
    GRAPH = "graph"               # Entitätsbeziehungen, Kausalitäten
    PARAMETRIC = "parametric"     # Modellgewichte, Embeddings

class MemoryDecay(Enum):
    """Zeitlicher Verfall von Erinnerungen."""
    IMMEDIATE = 0.1     # Sekunden (Sensorisch)
    SHORT_TERM = 0.5    # Minuten (Arbeitsgedächtnis)
    MEDIUM_TERM = 0.9   # Stunden/Tage
    LONG_TERM = 0.99    # Wochen/Monate (Semantisch)
    PERMANENT = 1.0     # Nie (Policies, ADRs)

class MemoryConfidence(Enum):
    """Konfidenz/Verlässlichkeit einer Erinnerung."""
    UNVERIFIED = 0.2    # Neu, noch nicht bestätigt
    OBSERVED_ONCE = 0.4 # Einmal beobachtet
    OBSERVED_MULTIPLE = 0.7  # Mehrfach bestätigt
    CORROBORATED = 0.9  # Durch andere Quellen gestützt
    CANONICAL = 1.0     # Offizielle Dokumentation, Policy


# ═══════════════════════════════════════════════════
# MEMORY ENTRY
# ═══════════════════════════════════════════════════

@dataclass
class MemoryEntry:
    """
    Universeller Gedächtniseintrag — jeder Speichertyp nutzt dieses Schema.

    Felder:
      memory_id:     Eindeutige ID
      memory_type:   EPISODIC | SEMANTIC | PROCEDURAL | GRAPH | PARAMETRIC
      content:       Der eigentliche Inhalt (Text, JSON, strukturiert)
      embedding:     Vektor-Embedding (für semantische Suche)
      decay_factor:  Zeitlicher Verfall (0-1)
      confidence:    Verlässlichkeit (0-1)
      source:        Woher stammt diese Erinnerung?
      tags:          Kategorisierung
      causal_parent: Verweist auf verursachende Erinnerung (Kausalkette)
      graph_edges:   Verbindungen zu anderen Entitäten
      created_at:    Erstellungszeitpunkt
      last_accessed: Letzter Abruf (beeinflusst Decay)
      access_count:  Wie oft abgerufen
      version:       Version der Erinnerung
      consolidated_from: Falls durch Konsolidierung entstanden
    """
    memory_id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    memory_type: MemoryType = MemoryType.EPISODIC

    # ── Content ──
    content: str = ""
    summary: str = ""                        # Komprimierte Form
    embedding: List[float] = field(default_factory=list)
    structured_data: Dict[str, Any] = field(default_factory=dict)

    # ── Metadata ──
    source: str = ""                         # "delivery_run_001", "github_issue_12"
    source_type: str = ""                    # "delivery", "incident", "skill", "policy"
    tags: List[str] = field(default_factory=list)
    namespace: str = "default"

    # ── Confidence & Decay ──
    decay_factor: float = 0.9               # 0-1, höher = langlebiger
    confidence: float = 0.4                 # 0-1, höher = verlässlicher
    contradictions: List[str] = field(default_factory=list)
    corroborations: List[str] = field(default_factory=list)

    # ── Causal & Graph ──
    causal_parent: str = ""                  # memory_id der Ursache
    causal_children: List[str] = field(default_factory=list)
    graph_edges: List[Dict[str, str]] = field(default_factory=list)
    # [{"target": "mem_xxx", "relationship": "caused_by"}]

    # ── Lifecycle ──
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    version: int = 1
    consolidated_from: List[str] = field(default_factory=list)
    consolidated_at: float = 0.0

    # ── Agent Context ──
    agent_id: str = ""                       # Welcher Agent hat diese Erinnerung
    task_id: str = ""                        # In welchem Task entstanden
    correlation_id: str = ""                 # Delivery Run

    def effective_confidence(self) -> float:
        """Berechne effektive Konfidenz unter Berücksichtigung von Decay."""
        age_hours = (time.time() - self.created_at) / 3600
        decay = self.decay_factor ** (age_hours / 24)  # Täglicher Decay
        corroboration_bonus = min(0.3, len(self.corroborations) * 0.1)
        contradiction_penalty = min(0.5, len(self.contradictions) * 0.15)

        effective = (self.confidence * decay) + corroboration_bonus - contradiction_penalty
        return max(0.0, min(1.0, effective))

    def access(self):
        """Markiere als abgerufen (verstärkt die Erinnerung)."""
        self.last_accessed = time.time()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content[:500],
            "summary": self.summary,
            "confidence": round(self.effective_confidence(), 2),
            "source": self.source,
            "tags": self.tags,
            "age_hours": round((time.time() - self.created_at) / 3600, 1),
            "access_count": self.access_count,
        }


# ═══════════════════════════════════════════════════
# UNIFIED OPERATIONAL MEMORY
# ═══════════════════════════════════════════════════

class UnifiedMemory:
    """
    Zentrales operationales Gedächtnis — alle 5 Typen in einem Store.

    Retrieval-Strategie:
      - Semantische Suche: Embedding-Ähnlichkeit (Qdrant)
      - Causal Traversal: Kausalketten entlang causal_parent/children
      - Graph Traversal: Entitätsbeziehungen (Knowledge Graph)
      - Temporal Filter: Zeitbasierte Abfragen mit Decay-Gewichtung
      - Multi-Factor Scoring: semantic(0.35) + causal(0.25) + confidence(0.15)
                             + recency(0.15) + access_count(0.10)

    Konsolidierung:
      Episodic → Semantic: Abstraktion wiederholter Muster
      Semantic → Procedural: Extraktion von Handlungsregeln
      Episodic → Graph: Erkennung von Entitätsbeziehungen
    """

    def __init__(self, db_path: str = "/opt/ai-farbrik/memory/unified_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._memories: Dict[str, MemoryEntry] = {}
        self._by_type: Dict[MemoryType, List[str]] = defaultdict(list)
        self._by_agent: Dict[str, List[str]] = defaultdict(list)
        self._by_correlation: Dict[str, List[str]] = defaultdict(list)
        self._by_tag: Dict[str, List[str]] = defaultdict(list)
        self._causal_index: Dict[str, List[str]] = defaultdict(list)
        self._init_db()

    def _init_db(self):
        db = sqlite3.connect(self.db_path)
        db.execute("""
            CREATE TABLE IF NOT EXISTS unified_memory (
                memory_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                confidence REAL DEFAULT 0.4,
                decay_factor REAL DEFAULT 0.9,
                source TEXT DEFAULT '',
                source_type TEXT DEFAULT '',
                namespace TEXT DEFAULT 'default',
                agent_id TEXT DEFAULT '',
                task_id TEXT DEFAULT '',
                correlation_id TEXT DEFAULT '',
                causal_parent TEXT DEFAULT '',
                consolidated_from TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                version INTEGER DEFAULT 1,
                structured_data TEXT DEFAULT '{}',
                contradictions TEXT DEFAULT '[]',
                corroborations TEXT DEFAULT '[]'
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_mem_type ON unified_memory(memory_type)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_mem_agent ON unified_memory(agent_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_mem_corr ON unified_memory(correlation_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_mem_source ON unified_memory(source)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_mem_causal ON unified_memory(causal_parent)")
        db.commit()
        db.close()

    # ── CRUD ──

    def store(self, entry: MemoryEntry) -> MemoryEntry:
        """Speichere eine Erinnerung in allen Indizes."""
        self._memories[entry.memory_id] = entry
        self._by_type[entry.memory_type].append(entry.memory_id)

        if entry.agent_id:
            self._by_agent[entry.agent_id].append(entry.memory_id)
        if entry.correlation_id:
            self._by_correlation[entry.correlation_id].append(entry.memory_id)
        for tag in entry.tags:
            self._by_tag[tag].append(entry.memory_id)
        if entry.causal_parent:
            self._causal_index[entry.causal_parent].append(entry.memory_id)

        # Persist
        db = sqlite3.connect(self.db_path)
        db.execute("""
            INSERT OR REPLACE INTO unified_memory (
                memory_id, memory_type, content, summary, confidence, decay_factor,
                source, source_type, namespace, agent_id, task_id, correlation_id,
                causal_parent, consolidated_from, tags,
                created_at, last_accessed, access_count, version,
                structured_data, contradictions, corroborations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.memory_id, entry.memory_type.value,
            entry.content[:10000], entry.summary,
            entry.confidence, entry.decay_factor,
            entry.source, entry.source_type, entry.namespace,
            entry.agent_id, entry.task_id, entry.correlation_id,
            entry.causal_parent,
            json.dumps(entry.consolidated_from),
            json.dumps(entry.tags),
            entry.created_at, entry.last_accessed, entry.access_count, entry.version,
            json.dumps(entry.structured_data),
            json.dumps(entry.contradictions),
            json.dumps(entry.corroborations),
        ))
        db.commit()
        db.close()
        return entry

    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Einzelne Erinnerung abrufen."""
        entry = self._memories.get(memory_id)
        if entry:
            entry.access()
        return entry

    # ── QUERY ──

    def query(self, memory_type: MemoryType = None, agent_id: str = "",
              correlation_id: str = "", tags: List[str] = None,
              min_confidence: float = 0.0, limit: int = 50) -> List[MemoryEntry]:
        """Multi-Kriterien-Abfrage."""
        results = []

        candidates = list(self._memories.values())
        if memory_type:
            candidates = [m for m in candidates if m.memory_type == memory_type]
        if agent_id:
            candidates = [m for m in candidates if m.agent_id == agent_id]
        if correlation_id:
            candidates = [m for m in candidates if m.correlation_id == correlation_id]
        if tags:
            candidates = [m for m in candidates if any(t in m.tags for t in tags)]
        if min_confidence > 0:
            candidates = [m for m in candidates if m.effective_confidence() >= min_confidence]

        # Sort: recency + confidence
        candidates.sort(key=lambda m: (
            m.effective_confidence() * 0.6 + (1.0 / (1.0 + (time.time() - m.created_at) / 86400)) * 0.4
        ), reverse=True)

        results = candidates[:limit]
        for m in results:
            m.access()
        return results

    def get_causal_chain(self, memory_id: str, direction: str = "backward",
                         max_depth: int = 10) -> List[MemoryEntry]:
        """Kausalkette traversieren (vorwärts oder rückwärts)."""
        chain = []
        current_id = memory_id
        visited = set()

        while current_id and len(chain) < max_depth and current_id not in visited:
            entry = self._memories.get(current_id)
            if not entry:
                break
            chain.append(entry)
            visited.add(current_id)

            if direction == "backward":
                current_id = entry.causal_parent
            else:
                children = self._causal_index.get(current_id, [])
                current_id = children[0] if children else ""

        if direction == "backward":
            chain.reverse()
        return chain

    def get_delivery_memory(self, correlation_id: str) -> Dict[str, Any]:
        """Gesamtes Gedächtnis eines Delivery Runs."""
        memories = self.query(correlation_id=correlation_id)
        return {
            "correlation_id": correlation_id,
            "total_memories": len(memories),
            "by_type": {
                t.value: len([m for m in memories if m.memory_type == t])
                for t in MemoryType
            },
            "timeline": [
                {"time": m.created_at, "type": m.memory_type.value,
                 "summary": m.summary, "confidence": round(m.effective_confidence(), 2)}
                for m in sorted(memories, key=lambda x: x.created_at)
            ],
        }

    # ── CONSOLIDATION ──

    def consolidate_episodic_to_semantic(self, agent_id: str = "",
                                          min_occurrences: int = 3) -> List[MemoryEntry]:
        """
        Episodic → Semantic: Wiederholte Muster zu Fakten abstrahieren.

        Sammelt alle EPISODIC-Memories eines Agenten,
        findet wiederholte Muster und erzeugt SEMANTIC-Memories.
        """
        episodes = self.query(memory_type=MemoryType.EPISODIC, agent_id=agent_id) if agent_id \
                   else [m for m in self._memories.values() if m.memory_type == MemoryType.EPISODIC]

        # Pattern detection: group by source_type + similar content
        patterns = defaultdict(list)
        for ep in episodes:
            key = f"{ep.source_type}:{ep.namespace}"
            patterns[key].append(ep)

        new_semantic = []
        for key, group in patterns.items():
            if len(group) >= min_occurrences:
                # Abstrahieren: Summary aus allen Episoden
                summaries = [e.summary for e in group if e.summary]
                source_types = list(set(e.source_type for e in group))

                semantic = MemoryEntry(
                    memory_type=MemoryType.SEMANTIC,
                    content=f"Consolidated from {len(group)} episodes: {key}",
                    summary=f"Pattern: {key} ({len(group)} occurrences)",
                    source=key,
                    source_type=source_types[0] if source_types else "",
                    confidence=MemoryConfidence.CORROBORATED.value,
                    decay_factor=MemoryDecay.LONG_TERM.value,
                    consolidated_from=[e.memory_id for e in group],
                    consolidated_at=time.time(),
                    tags=[key.split(":")[0]],
                )
                self.store(semantic)
                new_semantic.append(semantic)

        return new_semantic

    def consolidate_semantic_to_procedural(self) -> List[MemoryEntry]:
        """
        Semantic → Procedural: Faktenwissen zu Handlungsregeln extrahieren.

        SEMANTIC-Memories mit ähnlichen Tags werden zu PROCEDURAL-Skills verdichtet.
        """
        semantic_memories = [m for m in self._memories.values()
                            if m.memory_type == MemoryType.SEMANTIC]

        # Group by tags
        tag_groups = defaultdict(list)
        for sm in semantic_memories:
            for tag in sm.tags:
                tag_groups[tag].append(sm)

        new_procedural = []
        for tag, group in tag_groups.items():
            if len(group) >= 2:
                procedural = MemoryEntry(
                    memory_type=MemoryType.PROCEDURAL,
                    content=f"Derived procedure from semantic knowledge about: {tag}",
                    summary=f"Procedure: Handle {tag} scenarios (derived from {len(group)} facts)",
                    source=f"consolidation:{tag}",
                    source_type="consolidation",
                    confidence=MemoryConfidence.OBSERVED_MULTIPLE.value,
                    decay_factor=MemoryDecay.MEDIUM_TERM.value,
                    consolidated_from=[m.memory_id for m in group],
                    consolidated_at=time.time(),
                    tags=[tag, "procedural", "auto-derived"],
                )
                self.store(procedural)
                new_procedural.append(procedural)

        return new_procedural

    def run_consolidation(self) -> Dict[str, Any]:
        """Führe die vollständige Konsolidierungspipeline aus."""
        t0 = time.time()

        e2s = self.consolidate_episodic_to_semantic()
        s2p = self.consolidate_semantic_to_procedural()

        return {
            "pipeline": "memory_consolidation_v1",
            "episodic_to_semantic": len(e2s),
            "semantic_to_procedural": len(s2p),
            "duration_ms": (time.time() - t0) * 1000,
        }

    # ── STATISTICS ──

    def stats(self) -> Dict[str, Any]:
        """Gedächtnis-Statistiken."""
        by_type = {t.value: len(self._by_type.get(t, [])) for t in MemoryType}
        total = sum(by_type.values())

        # Durchschnittliche Konfidenz pro Typ
        avg_confidence = {}
        for t in MemoryType:
            mems = [self._memories[mid] for mid in self._by_type.get(t, [])]
            if mems:
                avg_confidence[t.value] = round(
                    sum(m.effective_confidence() for m in mems) / len(mems), 2
                )

        return {
            "total_memories": total,
            "by_type": by_type,
            "avg_confidence_by_type": avg_confidence,
            "agents": len(self._by_agent),
            "correlation_groups": len(self._by_correlation),
        }


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_memory: Optional[UnifiedMemory] = None

def get_memory() -> UnifiedMemory:
    global _memory
    if _memory is None:
        _memory = UnifiedMemory()
    return _memory
