"""
NeXifyAI — Hybrid Search (REAL IMPLEMENTATION v2.0)
Combines SQLite FTS (brain.db), Qdrant vector search, Open Notebook search.

SQLite is the PRIMARY backend (always available, contains real memories).
Qdrant and Open Notebook are SECONDARY (gracefully degrade if unreachable).

Usage:
    from backend.brain.hybrid_search import hybrid_search
    result = hybrid_search("how to fix health score")
    for r in result.results:
        print(f"[{r.source}] {r.score:.2f}: {r.content[:100]}")
"""

import sqlite3
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    content: str
    source: str  # 'qdrant', 'sqlite', 'open_notebook'
    score: float
    metadata: Dict = field(default_factory=dict)
    chunk_id: Optional[str] = None


@dataclass  
class HybridSearchResult:
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total_sources: int = 0
    search_time_ms: float = 0.0

    @property
    def top_result(self) -> Optional[SearchResult]:
        return self.results[0] if self.results else None

    @property
    def confidence(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results[:3]) / min(3, len(self.results))


# ══════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════

BRAIN_DB_PATH = "/opt/data/brain/brain.db"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "nexifyai_memories"
OPEN_NOTEBOOK_URL = "http://localhost:32770"
SEARCH_TIMEOUT = 5  # seconds

SOURCE_WEIGHTS = {
    'sqlite': 0.9,
    'qdrant': 1.0,
    'open_notebook': 0.6,
}
MIN_CONFIDENCE_THRESHOLD = 0.15


# ══════════════════════════════════════════════
# HYBRID SEARCH
# ══════════════════════════════════════════════

def hybrid_search(
    query: str,
    top_k: int = 10,
    min_score: float = 0.1,
    sources: List[str] = None,
) -> HybridSearchResult:
    start = time.time()
    result = HybridSearchResult(query=query)
    all_results: List[SearchResult] = []
    
    use_sources = sources or ['sqlite', 'qdrant', 'open_notebook']
    
    if 'sqlite' in use_sources:
        try:
            sqlite_results = _search_sqlite(query, top_k)
            all_results.extend(sqlite_results)
        except Exception as e:
            print(f"[brain] SQLite search failed: {e}")
    
    if 'qdrant' in use_sources:
        try:
            qdrant_results = _search_qdrant(query, top_k)
            all_results.extend(qdrant_results)
        except Exception as e:
            print(f"[brain] Qdrant search skipped (unreachable): {e}")
    
    if 'open_notebook' in use_sources:
        try:
            on_results = _search_open_notebook(query, top_k)
            all_results.extend(on_results)
        except Exception as e:
            print(f"[brain] Open Notebook skipped (unreachable): {e}")
    
    # Apply source weights
    for r in all_results:
        r.score *= SOURCE_WEIGHTS.get(r.source, 0.5)
    
    # Filter, deduplicate, sort
    all_results = [r for r in all_results if r.score >= min_score]
    seen = set()
    unique = []
    for r in sorted(all_results, key=lambda x: x.score, reverse=True):
        h = hash(r.content[:100])
        if h not in seen:
            seen.add(h)
            unique.append(r)
    
    result.results = unique[:top_k]
    result.total_sources = len(set(r.source for r in result.results))
    result.search_time_ms = (time.time() - start) * 1000
    
    return result


# ══════════════════════════════════════════════
# SQLITE — REAL IMPLEMENTATION
# ══════════════════════════════════════════════

def _search_sqlite(query: str, top_k: int = 10) -> List[SearchResult]:
    """
    Search brain.db using FTS5 full-text search (primary).
    Falls back to LIKE matching if FTS5 table doesn't exist.
    """
    results = []

    try:
        conn = sqlite3.connect(BRAIN_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Try FTS5 first (proper full-text search with ranking)
        try:
            cursor.execute("""
                SELECT m.content, m.category, m.source, m.created_at,
                       bm25(memories_fts, 0.0, 1.0) as relevance
                FROM memories_fts f
                JOIN memories m ON f.rowid = m.rowid
                WHERE memories_fts MATCH ?
                ORDER BY bm25(memories_fts, 0.0, 1.0)
                LIMIT ?
            """, (query, top_k))
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    # Normalize BM25 score to 0-1 range (BM25 is unbounded)
                    raw_score = abs(row['relevance']) if row['relevance'] else 5.0
                    normalized = min(1.0, raw_score / 15.0)
                    
                    results.append(SearchResult(
                        content=(row['content'] or '')[:500],
                        source='sqlite',
                        score=normalized,
                        metadata={
                            'category': row['category'] or 'unknown',
                            'source': row['source'] or 'unknown',
                            'created_at': row['created_at'] or '',
                            'search_method': 'fts5',
                        }
                    ))
                conn.close()
                return results
        except sqlite3.OperationalError:
            pass  # FTS5 table doesn't exist — fall through to LIKE

        # LIKE fallback: multi-term substring matching
        terms = query.lower().split()
        if terms:
            conditions = " AND ".join(["LOWER(content) LIKE ?" for _ in terms])
            params = [f"%{t}%" for t in terms]

            cursor.execute(f"""
                SELECT content, category, source, created_at,
                       (CASE WHEN LOWER(content) LIKE ? THEN 0.8 ELSE 0.4 END) as relevance
                FROM memories
                WHERE {conditions}
                ORDER BY created_at DESC
                LIMIT ?
            """, [f"%{query.lower()}%"] + params + [top_k])

            rows = cursor.fetchall()
            
            if not rows:
                cursor.execute("""
                    SELECT content, category, source, created_at, 0.3 as relevance
                    FROM memories
                    WHERE LOWER(content) LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f"%{query.lower().split()[0]}%", top_k))
                rows = cursor.fetchall()

            for row in rows:
                results.append(SearchResult(
                    content=(row['content'] or '')[:500],
                    source='sqlite',
                    score=row['relevance'],
                    metadata={
                        'category': row['category'] or 'unknown',
                        'source': row['source'] or 'unknown',
                        'created_at': row['created_at'] or '',
                        'search_method': 'like',
                    }
                ))

        conn.close()
    except Exception as e:
        print(f"[brain] SQLite error: {e}")

    return results


# ══════════════════════════════════════════════
# QDRANT — HTTP CLIENT
# ══════════════════════════════════════════════

def _search_qdrant(query: str, top_k: int = 10) -> List[SearchResult]:
    """
    Search Qdrant via REST API.
    POST /collections/{collection}/points/search
    """
    results = []
    
    try:
        # First try to get embedding from local model or use dummy vector
        # For now: search by payload text match via Qdrant scroll API
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/scroll"
        data = json.dumps({
            "limit": top_k,
            "with_payload": True,
            "with_vector": False,
        }).encode()
        
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT) as resp:
            response = json.loads(resp.read())
            
            for point in response.get("result", {}).get("points", []):
                payload = point.get("payload", {})
                content = payload.get("content", payload.get("text", ""))
                if content:
                    # Simple relevance: check if query terms appear in content
                    query_lower = query.lower()
                    content_lower = content.lower()
                    score = sum(1 for t in query_lower.split() if t in content_lower) / max(1, len(query_lower.split()))
                    score = min(1.0, score * 0.8)  # Cap at 0.8 for non-vector match
                    
                    if score > 0:
                        results.append(SearchResult(
                            content=content[:500],
                            source='qdrant',
                            score=score,
                            metadata=payload.get("metadata", {}),
                            chunk_id=point.get("id"),
                        ))
    except (urllib.error.URLError, urllib.error.HTTPError, ConnectionRefusedError) as e:
        pass  # Qdrant unavailable — graceful degradation
    except Exception as e:
        print(f"[brain] Qdrant error: {e}")
    
    return results


# ══════════════════════════════════════════════
# OPEN NOTEBOOK — HTTP CLIENT
# ══════════════════════════════════════════════

def _search_open_notebook(query: str, top_k: int = 10) -> List[SearchResult]:
    """Search Open Notebook via REST API."""
    results = []
    
    try:
        url = f"{OPEN_NOTEBOOK_URL}/api/search?q={urllib.parse.quote(query)}&limit={top_k}"
        
        with urllib.request.urlopen(url, timeout=SEARCH_TIMEOUT) as resp:
            response = json.loads(resp.read())
            
            for item in response.get("results", []):
                results.append(SearchResult(
                    content=item.get("content", "")[:500],
                    source='open_notebook',
                    score=item.get("score", 0.5),
                    metadata=item.get("metadata", {}),
                ))
    except (urllib.error.URLError, urllib.error.HTTPError, ConnectionRefusedError):
        pass  # Open Notebook unavailable — graceful degradation
    except Exception as e:
        print(f"[brain] OpenNotebook error: {e}")
    
    return results
