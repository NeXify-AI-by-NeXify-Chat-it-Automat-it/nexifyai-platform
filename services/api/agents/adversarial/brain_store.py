"""
Brain Integration for Adversarial Reviews.
Stores debate history, consensus outcomes, and learned patterns.
"""
import httpx, json, time, hashlib
from typing import Optional
from .model_router import DebateResult, ModelResponse

QDRANT_URL = "http://localhost:6333"
COLLECTION = "nexifyai_brain"

async def store_debate_result(debate: DebateResult):
    """Store debate result in Brain for future learning."""
    point_id = hashlib.sha256(
        f"{debate.task}:{time.time()}".encode()
    ).hexdigest()[:16]
    
    payload = {
        "category": "adversarial_review",
        "title": debate.task[:120],
        "content": json.dumps({
            "task": debate.task,
            "models": debate.models_used,
            "rounds": debate.rounds,
            "consensus": debate.consensus,
            "total_cost": debate.total_cost,
            "duration": debate.duration_seconds,
            "final_spec_length": len(debate.final_spec or ""),
            "model_agreements": {r.model: r.agreed for r in debate.responses},
        }),
        "timestamp": time.time(),
        "source": "adversarial-review",
    }
    
    async with httpx.AsyncClient() as client:
        await client.put(
            f"{QDRANT_URL}/collections/{COLLECTION}/points",
            json={"points": [{"id": point_id, "vector": [0.0]*1536, "payload": payload}]},
            timeout=10
        )

async def get_past_reviews(task_keywords: str, limit: int = 5) -> list[dict]:
    """Query Brain for past reviews relevant to this task."""
    words = task_keywords.split()[:5]
    body = {
        "limit": limit, "with_payload": True, "with_vector": False,
        "filter": {
            "must": [
                {"key": "category", "match": {"value": "adversarial_review"}},
                {"should": [{"key": "content", "match": {"text": w}} for w in words]},
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/scroll",
            json=body, timeout=10
        )
        points = r.json().get("result", {}).get("points", [])
        return [p["payload"] for p in points]
