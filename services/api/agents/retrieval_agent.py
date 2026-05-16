"""Retrieval Agent — Real Brain health check via brain.db + hybrid_search."""

import os, sqlite3, sys
from backend.agents.base_agent import BaseAgent


class RetrievalAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Retrieval Agent", "Knowledge retrieval quality and Brain optimization")
    
    def observe(self) -> dict:
        data = {
            "brain_db_exists": False,
            "memories_count": 0,
            "skills_count": 0,
            "sessions_count": 0,
            "embedding_model": "qwen3-embedding-8b",
            "hybrid_search_available": False,
            "recent_memories": [],
        }
        
        brain_db = "/opt/data/brain/brain.db"
        if os.path.exists(brain_db):
            data["brain_db_exists"] = True
            try:
                conn = sqlite3.connect(brain_db)
                data["memories_count"] = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                data["skills_count"] = conn.execute("SELECT COUNT(*) FROM skills_cache").fetchone()[0]
                data["sessions_count"] = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
                
                # Fetch 3 most recent memories as sample
                rows = conn.execute(
                    "SELECT content, category, source, created_at FROM memories ORDER BY created_at DESC LIMIT 3"
                ).fetchall()
                for row in rows:
                    data["recent_memories"].append({
                        "category": row[1] or "unknown",
                        "source": row[2] or "unknown",
                        "created": row[3] or "",
                        "preview": (row[0] or "")[:120],
                    })
                conn.close()
            except Exception as e:
                data["error"] = str(e)
        
        # Check if hybrid_search is importable
        try:
            sys.path.insert(0, "/opt/nexifyai-platform")
            from backend.brain.hybrid_search import hybrid_search
            data["hybrid_search_available"] = True
        except ImportError:
            pass
        
        return data
    
    def analyze(self, data: dict) -> list:
        findings = []
        
        if data["brain_db_exists"]:
            findings.append(f"✅ Brain DB: {data['memories_count']} memories, {data['skills_count']} skills, {data['sessions_count']} sessions")
        else:
            findings.append("❌ Brain DB not found — critical")
        
        if data["memories_count"] < 100:
            findings.append(f"⚠️  Only {data['memories_count']} memories (target: 1000+)")
        else:
            findings.append(f"✅ Memory count healthy ({data['memories_count']})")
        
        if data["hybrid_search_available"]:
            findings.append("✅ Hybrid search operational")
        else:
            findings.append("⚠️  Hybrid search module not importable")
        
        if data.get("recent_memories"):
            latest = data["recent_memories"][0]
            findings.append(f"ℹ️  Latest memory: [{latest['category']}] {latest['preview'][:80]}...")
        
        return findings
    
    def recommend(self, findings: list) -> list:
        return [
            "Run brain-sync.py to populate embeddings",
            "Set up Qdrant collection if not exists",
            "Configure Memory TTL (30 days default)",
            "Run brainforge-miner.py to enrich knowledge base",
        ]
