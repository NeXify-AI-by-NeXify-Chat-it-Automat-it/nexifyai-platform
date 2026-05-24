#!/usr/bin/env python3
"""
DEPRECATED: Wird durch services/rag_pipeline.py ersetzt.
            Nutze create_qa_chain(), create_conversational_qa(), get_vector_store().
            Migration: from services.rag_pipeline import create_qa_chain
            Entfernung geplant: 2026-06-21
"""

"""
Nexify Brain API — Live Qdrant Adapter (Phase 1)
=================================================
Connect to the existing Qdrant instance and expose a REST API
that uses the actual payload schemas and collections.

Run: uvicorn brain_api:app --host 0.0.0.0 --port 8420

Collections used:
  - nexifyai_brain (12,989+ points) — primary knowledge + memory
  - nexifyai_memories (5,852 points) — agent memory store
"""
import json, logging, time, uuid, hashlib
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import requests

log = logging.getLogger("nexify.brain-api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [brain-api] %(levelname)s: %(message)s",
)

QDRANT_URL = "http://localhost:6333"
COLLECTIONS = {
    "brain": "nexifyai_brain",
    "memory": "nexifyai_memories",
}

# ── Liveliness ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"Brain API connecting to Qdrant at {QDRANT_URL}")
    try:
        r = requests.get(f"{QDRANT_URL}/collections", timeout=5)
        cols = [c["name"] for c in r.json()["result"]["collections"]]
        log.info(f"Qdrant OK — {len(cols)} collections: {cols}")
    except Exception as e:
        log.warning(f"Qdrant unreachable at startup: {e}")
    yield

app = FastAPI(
    title="Nexify Brain API",
    version="2.0.0",
    description="Live Qdrant Brain Adapter — Phase 1",
    lifespan=lifespan,
)

# ── Models ──────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language search")
    category: Optional[str] = None
    source: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)
    score_threshold: float = Field(0.0, ge=0.0, le=1.0)

class StoreRequest(BaseModel):
    category: str = Field(..., description="Category: governance, knowledge, system_state, etc.")
    source: str = Field(default="brain-api", description="Source identifier")
    title: Optional[str] = None
    content: str = Field(..., description="The content to store")
    tags: list[str] = Field(default_factory=list)

# ── Routes ──────────────────────────────────────────────────
@app.get("/health")
async def health():
    try:
        r = requests.get(f"{QDRANT_URL}/collections", timeout=5)
        qdrant_int = [c["name"] for c in r.json()["result"]["collections"]]
        total_pts = 0
        for c_name in qdrant_int:
            ci = requests.get(f"{QDRANT_URL}/collections/{c_name}", timeout=5).json()
            total_pts += ci.get("result", {}).get("points_count", 0)
        return {
            "status": "ok",
            "qdrant": True,
            "collections": len(qdrant_int),
            "total_points": total_pts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"status": "degraded", "qdrant": False, "error": str(e)}

@app.get("/stats")
async def stats():
    results = {}
    for name, col in COLLECTIONS.items():
        try:
            r = requests.get(f"{QDRANT_URL}/collections/{col}", timeout=5)
            d = r.json().get("result", {})
            results[name] = {
                "collection": col,
                "points": d.get("points_count", 0),
                "indexed": d.get("indexed_vectors_count", 0),
                "status": d.get("status", "?"),
            }
        except Exception as e:
            results[name] = {"error": str(e)}
    return {"stats": results, "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/categories")
async def list_categories(limit: int = 500):
    """List all distinct categories and their counts."""
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTIONS['brain']}/points/scroll",
        json={"limit": limit, "with_payload": True, "with_vector": False},
        timeout=10,
    )
    pts = r.json().get("result", {}).get("points", [])
    cats = {}
    for p in pts:
        c = p.get("payload", {}).get("category", "?")
        cats[c] = cats.get(c, 0) + 1
    return {
        "categories": [{"name": k, "count": v} for k, v in sorted(cats.items(), key=lambda x: -x[1])],
        "total_scanned": len(pts),
    }

@app.post("/query")
async def query_brain(req: QueryRequest):
    """Semantic search across the brain.

    Uses scroll-based filtered search (no embedding needed for now).
    Falls back to text-based matching until embeddings are available.
    """
    must = []
    if req.category:
        must.append({"key": "category", "match": {"value": req.category}})
    if req.source:
        must.append({"key": "source", "match": {"text": req.source}})

    body = {
        "limit": req.limit,
        "with_payload": True,
        "with_vector": False,
    }
    if must:
        body["filter"] = {"must": must}

    t0 = time.time()
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTIONS['brain']}/points/scroll",
        json=body,
        timeout=15,
    )
    elapsed = round((time.time() - t0) * 1000)

    if r.status_code != 200:
        raise HTTPException(502, f"Qdrant error: {r.text[:200]}")

    pts = r.json().get("result", {}).get("points", [])

    # Basic text relevance filter if query is provided
    query_lower = req.query.lower() if req.query else ""
    if query_lower:
        scored = []
        for p in pts:
            pay = p.get("payload", {})
            text_fields = [str(pay.get(k, "")) for k in ["content", "text", "title", "data", "description"]]
            haystack = " ".join(text_fields).lower()
            score = 1.0 if query_lower in haystack else 0.0
            if score >= req.score_threshold:
                scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        results = [{
            "id": p.get("id"),
            "score": s,
            **{k: p.get("payload", {}).get(k) for k in ["category", "source", "title", "content", "text", "data", "ts", "status"]}
        } for s, p in scored[:req.limit]]
    else:
        results = [{
            "id": p.get("id"),
            **{k: p.get("payload", {}).get(k) for k in ["category", "source", "title", "content", "text", "data", "ts", "status"]}
        } for p in pts[:req.limit]]

    return {"results": results, "count": len(results), "query_time_ms": elapsed}

@app.post("/store")
async def store_brain(req: StoreRequest):
    """Store a new point in the brain."""
    point_id = str(uuid.uuid4())
    payload = {
        "category": req.category,
        "source": req.source,
        "title": req.title,
        "content": req.content,
        "data": req.content,
        "text": req.content,
        "ts": time.time(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": req.tags,
        "status": "active",
        "provenance": "brain-api-v2",
        "confidence": 0.9,
    }

    # Use a zero vector placeholder until sentence-transformers is available
    vector = [0.0] * 4096

    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTIONS['brain']}/points",
        json={"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        timeout=15,
    )

    if r.status_code != 200:
        raise HTTPException(502, f"Qdrant store error: {r.text[:200]}")

    return {"status": "stored", "point_id": point_id, "collection": COLLECTIONS["brain"]}

@app.delete("/delete/{point_id}")
async def delete_point(point_id: str):
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTIONS['brain']}/points/delete",
        json={"points": [point_id]},
        timeout=10,
    )
    return {"status": "deleted" if r.json().get("status") == "ok" else "failed"}

@app.get("/")
async def root():
    return {
        "service": "Nexify Brain API v2",
        "qdrant": QDRANT_URL,
        "collections": list(COLLECTIONS.values()),
        "endpoints": {
            "health": "GET /health",
            "stats": "GET /stats",
            "categories": "GET /categories",
            "query": "POST /query",
            "store": "POST /store",
            "delete": "DELETE /delete/{id}",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8420)
