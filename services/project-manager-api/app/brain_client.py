"""Brain API client."""
import httpx
import logging
from app.config import BRAIN_API_URL, BRAIN_API_TOKEN

logger = logging.getLogger("pm.brain")

async def check_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get(f"{BRAIN_API_URL}/health")
            return r.status_code == 200
    except Exception as e:
        logger.warning("Brain health check failed: %s", e)
        return False

async def store(category: str, content: str, source: str = "project-manager") -> dict:
    try:
        headers = {}
        if BRAIN_API_TOKEN:
            headers["Authorization"] = f"Bearer {BRAIN_API_TOKEN}"
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.post(f"{BRAIN_API_URL}/store", json={
                "category": category, "content": content, "source": source,
            }, headers=headers)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error("Brain store failed: %s", e)
        return {"error": str(e)}
