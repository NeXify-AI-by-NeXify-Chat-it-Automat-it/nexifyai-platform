"""
NeXifyAI Brain Connector — Agent Discovery via Qdrant Semantic Search.
Allows any agent to find other agents by capability query.
"""
import os
import httpx
from typing import List, Optional

BRAIN_URL = os.environ.get("HERMES_BRAIN_URL", "http://localhost:6333")
BRAIN_KEY = os.environ.get("HERMES_BRAIN_KEY", os.environ.get("DS_HERMES_FFCEF39C__BRAIN_KEY", ""))
COLLECTION = os.environ.get("BRAIN_COLLECTION", "nexifyai_brain")

# Embedding model — sentence-transformers/all-MiniLM-L6-v2 (384-dim)
# For production, use a hosted embedding service or pre-computed vectors.
# Fallback: simple keyword match if embedding unavailable.

_embedding_model = None


def _get_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _embedding_model = False
    return _embedding_model


async def search_agents(query: str, limit: int = 3, category: str = None) -> List[str]:
    """
    Search for agents by capability description.
    Uses Qdrant HNSW Cosine search with category filter.
    Falls back to keyword matching if embedding unavailable.
    
    Returns list of agent_ids sorted by relevance.
    """
    model = _get_model()
    
    if model:
        try:
            vector = model.encode(query).tolist()
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{BRAIN_URL}/collections/{COLLECTION}/points/search",
                    headers={"api-key": BRAIN_KEY, "Content-Type": "application/json"},
                    json={
                        "vector": vector,
                        "limit": limit,
                        "with_payload": True,
                        "with_vector": False,
                        "filter": {
                            "must": [
                                {"key": "category", "match": {"value": category}}
                            ]
                        }
                    }
                )
                r.raise_for_status()
                results = r.json().get("result", [])
                agents = []
                for res in results:
                    agent_id = res.get("payload", {}).get("agent_id", "")
                    score = res.get("score", 0)
                    if agent_id and score > 0.05:
                        agents.append(agent_id)
                return agents
        except Exception as e:
            pass  # Fall through to keyword fallback
    
    # Keyword fallback
    query_lower = query.lower()
    agents = []
    
    # Known agent keywords
    agent_keywords = {
        "ai-engineer": ["ki", "ai", "engineer", "architekt", "agent", "bauen", "design", "system"],
        "project-manager": ["projekt", "manager", "plan", "koordination", "timeline", "deadline"],
        "task-decomposition-expert": ["task", "zerlegen", "breakdown", "subtaks", "decomposition"],
        "monitoring-specialist": ["monitor", "alert", "metrik", "health", "uptime", "observability"],
        "deployment-engineer": ["deploy", "ci/cd", "pipeline", "github action", "vercel", "docker"],
        "cloud-architect": ["cloud", "infrastruktur", "architektur", "scaling", "multi-tenant"],
        "supabase-schema-architect": ["datenbank", "schema", "postgres", "sql", "migration", "rls"],
        "nextjs-architecture-expert": ["next.js", "frontend", "react", "design", "ui", "tailwind"],
        "fullstack-developer": ["fullstack", "feature", "implementieren", "entwickeln", "code", "api"],
        "security-engineer": ["security", "sicherheit", "devsecops", "trivy", "gitleaks", "secret"],
        "security-auditor": ["audit", "pentest", "compliance", "dsgvo", "prüfung"],
        "review-agent": ["review", "prüfen", "qualität", "code-review", "pr"],
        "research-coordinator": ["recherche", "research", "analyse", "untersuchen"],
        "data-analyst": ["daten", "analyse", "statistik", "metriken", "trend"],
        "data-engineer": ["pipeline", "etl", "daten", "transformieren"],
        "documentation-expert": ["doku", "dokumentation", "readme", "docs", "docusaurus"],
        "context-manager": ["kontext", "brain", "retrieval", "memory", "session"],
        "search-specialist": ["suche", "search", "finden", "qdrant"],
        "llms-maintainer": ["llm", "model", "token", "provider", "nexify_provider"],
        "agent-expert": ["agent", "prompt", "optimieren"],
        "dependency-manager": ["dependency", "npm", "package", "update", "renovate"],
        "metadata-agent": ["metadata", "tag", "tagging"],
        "document-structure-analyzer": ["pdf", "scan", "dokument", "ocr"],
        "project-supervisor-orchestrator": ["supervisor", "übersicht", "velocity"],
        "architecture-modernizer": ["modernisieren", "migration", "legacy"],
        "business-analyst": ["business", "anforderung", "requirement", "kpi"],
        "fact-checker": ["fakt", "validieren", "widerspruch", "check"],
    }
    
    scores = {}
    for agent, keywords in agent_keywords.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[agent] = score
    
    return sorted(scores, key=scores.get, reverse=True)[:limit]


async def get_agent_context(agent_id: str) -> Optional[dict]:
    """Get full context for a specific agent from Brain."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll",
                headers={"api-key": BRAIN_KEY, "Content-Type": "application/json"},
                json={
                    "limit": 5,
                    "with_payload": True,
                    "with_vector": False,
                    "filter": {
                        "must": [
                            {"key": "agent_id", "match": {"value": agent_id}},
                            {"key": "category", "match": {"value": "agent_registry"}},
                        ]
                    }
                }
            )
            r.raise_for_status()
            points = r.json().get("result", {}).get("points", [])
            if points:
                return points[0]["payload"]
    except Exception:
        pass
    return None


HERMES_URL = os.environ.get("HERMES_GATEWAY_URL", "http://localhost:8642")

async def dispatch_to_hermes(agent_id: str, task: str, context: dict = None) -> dict:
    """Execute agent task — uses Brain+LLM for real agent execution."""
    from .agent_executor import execute_agent_task
    return await execute_agent_task(agent_id, task, context)
