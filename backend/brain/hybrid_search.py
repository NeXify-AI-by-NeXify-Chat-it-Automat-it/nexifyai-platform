"""
NeXifyAI — Hybrid Search (Qdrant + SQLite)
Combines dense vector search with keyword matching for optimal retrieval.

Usage:
    from backend.brain.hybrid_search import hybrid_search
    results = hybrid_search("how to fix health score")
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Unified search result from any source."""
    content: str
    source: str  # 'qdrant', 'sqlite', 'open_notebook'
    score: float  # 0.0 - 1.0 (normalized)
    metadata: Dict = field(default_factory=dict)
    chunk_id: Optional[str] = None


@dataclass
class HybridSearchResult:
    """Aggregated hybrid search result with deduplication."""
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total_sources: int = 0
    search_time_ms: float = 0.0

    @property
    def top_result(self) -> Optional[SearchResult]:
        return self.results[0] if self.results else None

    @property
    def confidence(self) -> float:
        """Average confidence of top-3 results."""
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results[:3]) / min(3, len(self.results))


# ══════════════════════════════════════════════
# WEIGHT CONFIGURATION
# ══════════════════════════════════════════════

SOURCE_WEIGHTS = {
    'qdrant': 1.0,        # Vector search (highest semantic quality)
    'sqlite': 0.7,         # Keyword search (exact matches)
    'open_notebook': 0.8,   # External documents
}

# Minimum confidence threshold
MIN_CONFIDENCE_THRESHOLD = 0.35

# ══════════════════════════════════════════════
# HYBRID SEARCH
# ══════════════════════════════════════════════

def hybrid_search(
    query: str,
    top_k: int = 10,
    min_score: float = 0.3,
    sources: List[str] = None,
) -> HybridSearchResult:
    """
    Perform hybrid search across all Brain sources.
    
    - Qdrant: Dense vector semantic search
    - SQLite: Keyword/substring matching in brain.db
    - Open Notebook: External knowledge documents
    
    Results are deduplicated, weight-normalized, and sorted by score.
    """
    import time
    start = time.time()
    
    result = HybridSearchResult(query=query)
    all_results: List[SearchResult] = []
    
    # Qdrant vector search (via brain_search tool)
    try:
        qdrant_results = _search_qdrant(query, top_k)
        all_results.extend(qdrant_results)
    except Exception as e:
        print(f"[brain] Qdrant search failed: {e}")
    
    # SQLite keyword search
    try:
        sqlite_results = _search_sqlite(query, top_k)
        all_results.extend(sqlite_results)
    except Exception as e:
        print(f"[brain] SQLite search failed: {e}")
    
    # Open Notebook (if available)
    try:
        on_results = _search_open_notebook(query, top_k)
        all_results.extend(on_results)
    except Exception as e:
        print(f"[brain] Open Notebook search failed: {e}")
    
    # Apply source weights
    for r in all_results:
        r.score *= SOURCE_WEIGHTS.get(r.source, 0.5)
    
    # Filter by minimum score
    all_results = [r for r in all_results if r.score >= min_score]
    
    # Deduplicate by content hash
    seen = set()
    unique_results = []
    for r in sorted(all_results, key=lambda x: x.score, reverse=True):
        content_hash = hash(r.content[:100])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_results.append(r)
    
    result.results = unique_results[:top_k]
    result.total_sources = len(set(r.source for r in result.results))
    result.search_time_ms = (time.time() - start) * 1000
    
    return result


def _search_qdrant(query: str, top_k: int) -> List[SearchResult]:
    """Search Qdrant vector store."""
    # This would use the Qdrant client or HTTP API
    # For now, returns empty — actual implementation uses Hermes brain_search tool
    return []


def _search_sqlite(query: str, top_k: int) -> List[SearchResult]:
    """Search brain.db SQLite for keyword matches."""
    import sqlite3
    try:
        conn = sqlite3.connect('/opt/data/brain/brain.db')
        cursor = conn.cursor()
        # Simple LIKE search across known tables
        cursor.execute("""
            SELECT content, 'sqlite' as source, 0.5 as score
            FROM brain_entries
            WHERE content LIKE ?
            LIMIT ?
        """, (f'%{query}%', top_k))
        results = []
        for row in cursor.fetchall():
            results.append(SearchResult(
                content=row[0][:500],
                source='sqlite',
                score=0.5,
            ))
        conn.close()
        return results
    except Exception:
        return []


def _search_open_notebook(query: str, top_k: int) -> List[SearchResult]:
    """Search Open Notebook for external documents."""
    try:
        import requests
        resp = requests.get(
            'http://localhost:32770/api/search',
            params={'q': query, 'limit': top_k},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return [
                SearchResult(
                    content=item.get('content', '')[:500],
                    source='open_notebook',
                    score=item.get('score', 0.5),
                )
                for item in data.get('results', [])
            ]
    except Exception:
        pass
    return []
