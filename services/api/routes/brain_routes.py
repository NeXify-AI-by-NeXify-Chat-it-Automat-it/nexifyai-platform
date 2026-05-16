"""
Brain API Router — Central Qdrant Brain endpoints.
Provides health check and search for the central knowledge oracle.
"""
from fastapi import APIRouter, Query, Depends
from routes.shared import get_current_admin
import httpx

brain_router = APIRouter(prefix="/api/brain", tags=["brain"])

@brain_router.get("/health")
async def brain_health(_admin=Depends(get_current_admin)):
    """Brain (Qdrant) health check."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:6333/collections", timeout=5)
            cols = r.json()["result"]["collections"]
        return {
            "status": "healthy",
            "collections": [
                {"name": c["name"], "vectors": c.get("vectors_count", c.get("points_count", "?"))}
                for c in cols
            ],
            "total_points": sum(c.get("vectors_count", c.get("points_count", 0)) for c in cols),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@brain_router.get("/search")
async def brain_search(
    q: str = Query("", description="Search query text"),
    category: str = Query("", description="Filter by category"),
    limit: int = Query(10, ge=1, le=50),
    _admin=Depends(get_current_admin)):
    """Query the Brain for relevant knowledge. Returns matching points."""
    filter_terms = []
    if category:
        filter_terms.append({"key": "category", "match": {"value": category}})
    if q:
        # Text match on content field
        words = q.split()
        filter_terms.append({
            "should": [{"key": "content", "match": {"text": w}} for w in words[:5]]
        })
    
    body = {
        "limit": limit,
        "with_payload": True,
        "with_vector": False,
    }
    if filter_terms:
        body["filter"] = {"must": filter_terms}
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:6333/collections/nexifyai_brain/points/scroll",
                json=body, timeout=10
            )
            points = r.json().get("result", {}).get("points", [])
            results = []
            for p in points:
                pl = p["payload"]
                results.append({
                    "id": p["id"],
                    "category": pl.get("category", "?"),
                    "content": (pl.get("content", "") or "")[:300],
                    "title": pl.get("title", ""),
                    "timestamp": pl.get("timestamp"),
                })
        return {"query": q, "matches": results, "count": len(results), "status": "ok"}
    except Exception as e:
        return {"query": q, "matches": [], "error": str(e), "status": "error"}

@brain_router.get("/categories")
async def brain_categories():
    """List all categories in the Brain with counts."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:6333/collections/nexifyai_brain/points/scroll",
                json={"limit": 1000, "with_payload": True, "with_vector": False},
                timeout=15
            )
            points = r.json().get("result", {}).get("points", [])
            cats = {}
            for p in points:
                cat = p["payload"].get("category", "?")
                cats[cat] = cats.get(cat, 0) + 1
        return {
            "total_points": len(points),
            "categories": dict(sorted(cats.items(), key=lambda x: -x[1])),
            "status": "ok"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
