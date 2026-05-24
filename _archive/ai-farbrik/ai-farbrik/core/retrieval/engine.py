"""NeXifyAI Core: Retrieval Engine v4.8
AIC-49 Phase 1 — Governed Enterprise Retrieval

Brain-first retrieval with quality tracking and governance validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
import hashlib
import json
import time
import uuid


@dataclass
class RetrievalQuery:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_text: str = ""
    query_hash: str = ""
    session_id: Optional[str] = None
    retrieval_source: str = "brain"
    max_results: int = 10
    min_score: float = 0.5
    filters: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if self.query_text and not self.query_hash:
            self.query_hash = hashlib.sha256(self.query_text.encode()).hexdigest()[:16]


@dataclass
class RetrievalResult:
    query_id: str
    results: list = field(default_factory=list)
    total_found: int = 0
    latency_ms: int = 0
    source: str = "brain"
    quality_score: float = 0.0
    metadata: dict = field(default_factory=dict)


class RetrievalEngine:
    """Governed retrieval with quality scoring and audit trail."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._query_history: list = []
        self._stats = {
            "queries": 0,
            "total_results": 0,
            "avg_latency_ms": 0,
            "cache_hits": 0,
        }

    def retrieve(self, query: RetrievalQuery, backend=None) -> RetrievalResult:
        """
        Execute a governed retrieval.

        Args:
            query: The retrieval query (text, filters, etc.)
            backend: Optional backend client (Qdrant, Supabase, etc.)

        Returns:
            RetrievalResult with scored results and metadata.
        """
        start_time = time.time()
        self._stats["queries"] += 1

        results = []

        if backend:
            try:
                raw_results = backend.search(
                    query_text=query.query_text,
                    limit=query.max_results,
                    score_threshold=query.min_score,
                    **query.filters,
                )
                for r in raw_results:
                    results.append({
                        "id": r.get("id", ""),
                        "content": r.get("content", "")[:500],
                        "score": r.get("score", 0.0),
                        "source": r.get("source", "unknown"),
                        "metadata": r.get("metadata", {}),
                    })
            except Exception as e:
                results = [{"error": str(e), "score": 0.0}]

        latency_ms = int((time.time() - start_time) * 1000)

        # Quality score
        quality = self._compute_quality(results, latency_ms)

        result = RetrievalResult(
            query_id=query.id,
            results=results,
            total_found=len(results),
            latency_ms=latency_ms,
            source=query.retrieval_source,
            quality_score=quality,
            metadata={
                "query_hash": query.query_hash,
                "backend": type(backend).__name__ if backend else "none",
                "timestamp": query.created_at,
            },
        )

        self._query_history.append({
            "query": query.query_hash,
            "result_count": len(results),
            "latency_ms": latency_ms,
            "quality": quality,
        })

        # Keep history bounded
        if len(self._query_history) > 1000:
            self._query_history = self._query_history[-500:]

        return result

    def _compute_quality(self, results: list, latency_ms: int) -> float:
        """Compute retrieval quality score (0-1)."""
        if not results:
            return 0.0

        scores = [r.get("score", 0.0) for r in results if "error" not in r]
        if not scores:
            return 0.0

        avg_score = sum(scores) / len(scores)

        # Penalty for high latency
        latency_penalty = min(latency_ms / 5000, 0.3)

        # Bonus for high score density
        high_score_ratio = sum(1 for s in scores if s > 0.7) / len(scores)
        density_bonus = high_score_ratio * 0.2

        quality = min(avg_score - latency_penalty + density_bonus, 1.0)
        return max(quality, 0.0)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def get_recent_queries(self, limit: int = 10) -> list:
        """Get recent query history."""
        return self._query_history[-limit:]
