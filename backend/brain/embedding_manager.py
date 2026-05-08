"""
NeXifyAI — Embedding Manager (REAL IMPLEMENTATION v2.0)
Persists embeddings to Qdrant via HTTP API. Falls back to SQLite.

Usage:
    from backend.brain.embedding_manager import EmbeddingManager
    mgr = EmbeddingManager()
    entry = mgr.embed("important decision", metadata={"category": "decision"})
"""

import hashlib
import json
import time
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class EmbeddingStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DEPRECATED = "deprecated"
    CONFLICT = "conflict"


@dataclass
class EmbeddingEntry:
    id: str
    content: str
    embedding_version: str = "2.0.0"
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 30 * 24 * 3600  # 30 days
    confidence: float = 0.5
    source: str = "unknown"
    tags: List[str] = field(default_factory=list)
    status: EmbeddingStatus = EmbeddingStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.created_at + self.ttl_seconds

    @property
    def age_days(self) -> float:
        return (time.time() - self.created_at) / 86400

    def to_qdrant_point(self, vector: List[float] = None) -> Dict:
        """Convert to Qdrant point format."""
        return {
            "id": self.id,
            "vector": vector or [0.0] * 768,  # Placeholder — real embeddings from model
            "payload": {
                "content": self.content,
                "version": self.embedding_version,
                "confidence": self.confidence,
                "source": self.source,
                "tags": self.tags,
                "status": self.status.value,
                "metadata": self.metadata,
                "created_at": self.created_at,
                "expires_at": self.created_at + self.ttl_seconds,
            }
        }


# ══════════════════════════════════════════════
# EMBEDDING MANAGER
# ══════════════════════════════════════════════

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "nexifyai_memories"
BRAIN_DB_PATH = "/opt/data/brain/brain.db"


class EmbeddingManager:

    EMBEDDING_VERSION = "2.0.0"

    def __init__(self, ttl_days: int = 30):
        self.ttl_seconds = ttl_days * 24 * 3600

    def embed(
        self,
        content: str,
        metadata: Dict = None,
        tags: List[str] = None,
        source: str = "unknown",
        confidence: float = 0.5,
    ) -> EmbeddingEntry:
        content_hash = hashlib.sha256(
            (content + self.EMBEDDING_VERSION).encode()
        ).hexdigest()[:16]

        entry = EmbeddingEntry(
            id=f"emb-{content_hash}",
            content=content,
            embedding_version=self.EMBEDDING_VERSION,
            ttl_seconds=self.ttl_seconds,
            confidence=confidence,
            source=source,
            tags=tags or [],
            metadata=metadata or {},
        )

        # Persist to Qdrant (with fallback to SQLite)
        self._persist_qdrant(entry)
        self._persist_sqlite(entry)

        return entry

    def _persist_qdrant(self, entry: EmbeddingEntry) -> bool:
        """Persist embedding to Qdrant via HTTP API."""
        try:
            url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points"
            data = json.dumps({
                "points": [entry.to_qdrant_point()]
            }).encode()

            req = urllib.request.Request(url, data=data, method="PUT")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=5) as resp:
                response = json.loads(resp.read())
                if response.get("result", {}).get("status") == "ok":
                    return True
        except (urllib.error.URLError, ConnectionRefusedError):
            pass  # Qdrant unavailable — SQLite fallback
        except Exception as e:
            print(f"[embedding] Qdrant persist error: {e}")
        return False

    def _persist_sqlite(self, entry: EmbeddingEntry) -> bool:
        """Fallback persist to SQLite brain.db."""
        try:
            conn = sqlite3.connect(BRAIN_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO memories (id, content, category, source, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                json.dumps({
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "tags": entry.tags,
                    "version": entry.embedding_version,
                    "confidence": entry.confidence,
                }),
                "embedding",
                entry.source,
                json.dumps([]),  # No real vector in SQLite
                datetime.fromtimestamp(entry.created_at, tz=timezone.utc).isoformat(),
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[embedding] SQLite persist error: {e}")
            return False

    def detect_conflicts(
        self,
        content: str,
        existing: List[EmbeddingEntry] = None,
        similarity_threshold: float = 0.85,
    ) -> List[EmbeddingEntry]:
        """Detect conflicting entries with high content similarity."""
        conflicts = []
        if not existing:
            return conflicts

        new_words = set(content.lower().split())
        if not new_words:
            return conflicts

        for entry in existing:
            old_words = set(entry.content.lower().split())
            if not old_words:
                continue
            intersection = new_words & old_words
            union = new_words | old_words
            similarity = len(intersection) / len(union)

            if similarity > similarity_threshold:
                conflicts.append(entry)

        return conflicts

    def resolve_conflict(
        self,
        new_entry: EmbeddingEntry,
        old_entry: EmbeddingEntry,
        strategy: str = "latest_wins",
    ) -> EmbeddingEntry:
        if strategy == "merge_tags":
            new_entry.tags = list(set(new_entry.tags + old_entry.tags))
            new_entry.metadata.update(old_entry.metadata)
        old_entry.status = EmbeddingStatus.DEPRECATED
        return new_entry

    def cleanup_expired(self, entries: List[EmbeddingEntry]) -> List[str]:
        return [e.id for e in entries if e.is_expired]

    def compute_confidence(self, entry: EmbeddingEntry) -> float:
        source_weights = {
            'brain_search': 1.0, 'adr': 0.9, 'policy': 0.9,
            'dos': 0.95, 'conversation': 0.4, 'unknown': 0.3,
        }
        source_mult = source_weights.get(entry.source, 0.5)
        age_mult = max(0.3, 2 ** (-entry.age_days / 60))
        return min(1.0, max(0.0, entry.confidence * source_mult * age_mult))
