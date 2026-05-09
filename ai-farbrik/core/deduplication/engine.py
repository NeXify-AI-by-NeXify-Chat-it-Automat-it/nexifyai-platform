"""NeXifyAI Core: Deduplication Engine v4.8
AIC-49 Phase 1 — Enterprise Deduplication

Hash-based + semantic deduplication for document ingestion.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
import hashlib
import re


@dataclass
class DedupResult:
    is_duplicate: bool
    content_hash: str
    fuzzy_hash: str = ""
    matched_existing_id: Optional[str] = None
    similarity_score: float = 0.0
    dedup_method: str = "none"
    metadata: dict = field(default_factory=dict)


class DeduplicationEngine:
    """Governed deduplication with exact and fuzzy matching."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._known_hashes: set = set()
        self._known_fuzzy_hashes: dict[str, str] = {}  # fuzzy_hash -> doc_id
        self._stats = {
            "checked": 0,
            "duplicates_found": 0,
            "unique_accepted": 0,
        }

    def check(self, content: str, document_id: str = None,
              title: str = "") -> DedupResult:
        """Check if content is a duplicate."""
        self._stats["checked"] += 1

        content_hash = self._compute_hash(content)
        fuzzy_hash = self._compute_fuzzy_hash(content)

        # Exact match
        if content_hash in self._known_hashes:
            self._stats["duplicates_found"] += 1
            return DedupResult(
                is_duplicate=True,
                content_hash=content_hash,
                fuzzy_hash=fuzzy_hash,
                matched_existing_id=document_id,
                similarity_score=1.0,
                dedup_method="exact_hash",
            )

        # Fuzzy match
        if fuzzy_hash in self._known_fuzzy_hashes:
            existing_id = self._known_fuzzy_hashes[fuzzy_hash]
            self._stats["duplicates_found"] += 1
            return DedupResult(
                is_duplicate=True,
                content_hash=content_hash,
                fuzzy_hash=fuzzy_hash,
                matched_existing_id=existing_id,
                similarity_score=0.95,
                dedup_method="fuzzy_hash",
            )

        # Accept as unique
        self._known_hashes.add(content_hash)
        self._known_fuzzy_hashes[fuzzy_hash] = document_id or content_hash
        self._stats["unique_accepted"] += 1

        return DedupResult(
            is_duplicate=False,
            content_hash=content_hash,
            fuzzy_hash=fuzzy_hash,
            dedup_method="none",
        )

    def register(self, content: str, document_id: str):
        """Register content hash as known (for pre-seeding the engine)."""
        content_hash = self._compute_hash(content)
        fuzzy_hash = self._compute_fuzzy_hash(content)
        self._known_hashes.add(content_hash)
        self._known_fuzzy_hashes[fuzzy_hash] = document_id

    def _compute_hash(self, content: str) -> str:
        """Compute exact content hash."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _compute_fuzzy_hash(self, content: str) -> str:
        """Compute fuzzy hash (normalized, stop words removed)."""
        # Normalize: lowercase, strip punctuation, remove extra whitespace
        normalized = content.lower()
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Remove common stop words for fuzzy matching
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'shall', 'can',
            'der', 'die', 'das', 'und', 'ist', 'sind', 'war', 'in', 'zu',
            'von', 'mit', 'auf', 'für', 'nicht', 'ein', 'eine', 'einen',
        }
        words = [w for w in normalized.split() if w not in stop_words]

        # Hash the remaining significant words
        return hashlib.sha256(' '.join(sorted(words[:100])).encode()).hexdigest()[:12]

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def reset(self):
        """Reset the deduplication state."""
        self._known_hashes.clear()
        self._known_fuzzy_hashes.clear()
        self._stats = {
            "checked": 0,
            "duplicates_found": 0,
            "unique_accepted": 0,
        }
