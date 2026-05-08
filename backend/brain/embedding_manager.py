"""
NeXifyAI — Embedding Manager
Embedding versioning, TTL, confidence scoring, conflict resolution.

Usage:
    from backend.brain.embedding_manager import EmbeddingManager
    mgr = EmbeddingManager()
    mgr.embed("content text", metadata={"category": "decision"})
"""

import hashlib
import time
from datetime import datetime, timezone, timedelta
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
    """A versioned embedding entry."""
    id: str
    content: str
    embedding_version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    ttl_seconds: int = 30 * 24 * 3600  # 30 days default
    confidence: float = 0.5
    source: str = "unknown"
    tags: List[str] = field(default_factory=list)
    status: EmbeddingStatus = EmbeddingStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return time.time() > self.expires_at
        return time.time() > self.created_at + self.ttl_seconds
    
    @property
    def age_days(self) -> float:
        return (time.time() - self.created_at) / 86400


# ══════════════════════════════════════════════
# EMBEDDING MANAGER
# ══════════════════════════════════════════════

class EmbeddingManager:
    """
    Manages embedding lifecycle: versioning, TTL, confidence, deduplication.
    Integrates with Qdrant for storage and retrieval.
    """
    
    EMBEDDING_VERSION = "2.0.0"  # Current embedding model version
    
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
        """Create a versioned embedding entry."""
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
        
        # TODO: Actually store in Qdrant
        # qdrant_client.upsert(collection_name="brain", points=[entry.to_point()])
        
        return entry
    
    def detect_conflicts(
        self,
        content: str,
        existing: List[EmbeddingEntry],
        similarity_threshold: float = 0.85,
    ) -> List[EmbeddingEntry]:
        """
        Detect conflicting entries with high content similarity but different metadata.
        Returns list of conflicting entries.
        """
        conflicts = []
        for entry in existing:
            # Simple Jaccard similarity on word sets
            new_words = set(content.lower().split())
            old_words = set(entry.content.lower().split())
            if not new_words or not old_words:
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
        """
        Resolve conflict between two embedding entries.
        
        Strategies:
        - 'latest_wins': Newer entry replaces older
        - 'merge_tags': Keep both, merge tags
        - 'new_version': Deprecate old, create new version
        """
        if strategy == "latest_wins":
            new_entry.status = EmbeddingStatus.ACTIVE
            old_entry.status = EmbeddingStatus.DEPRECATED
            return new_entry
        
        elif strategy == "merge_tags":
            new_entry.tags = list(set(new_entry.tags + old_entry.tags))
            new_entry.metadata.update(old_entry.metadata)
            old_entry.status = EmbeddingStatus.DEPRECATED
            return new_entry
        
        elif strategy == "new_version":
            old_entry.status = EmbeddingStatus.DEPRECATED
            return new_entry
        
        return new_entry
    
    def cleanup_expired(self, entries: List[EmbeddingEntry]) -> List[str]:
        """Remove expired entries, return IDs of removed entries."""
        removed = []
        for entry in entries:
            if entry.is_expired:
                entry.status = EmbeddingStatus.EXPIRED
                removed.append(entry.id)
        return removed
    
    def compute_confidence(self, entry: EmbeddingEntry) -> float:
        """
        Compute confidence score for an embedding entry.
        Based on: source weight, age, corroboration count.
        """
        base_confidence = entry.confidence
        
        # Source weight
        source_weights = {
            'brain_search': 1.0,
            'adr': 0.9,
            'policy': 0.9,
            'dos': 0.95,
            'conversation': 0.4,
            'unknown': 0.3,
        }
        source_multiplier = source_weights.get(entry.source, 0.5)
        
        # Age decay (exponential, half-life 60 days)
        age_days = entry.age_days
        age_multiplier = max(0.3, 2 ** (-age_days / 60))
        
        # Compute final score
        final_confidence = base_confidence * source_multiplier * age_multiplier
        
        return min(1.0, max(0.0, final_confidence))
