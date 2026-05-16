"""
NeXifyAI Skill Registry — manages all agent SKILL.md definitions.
Loads skills from filesystem and syncs to Brain.
"""
import os, json, httpx, hashlib, time
from pathlib import Path
from typing import Optional

SKILLS_DIR = Path(__file__).parent / "skills"

def list_skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    return sorted([d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])

def get_skill(agent_slug: str) -> Optional[str]:
    path = SKILLS_DIR / agent_slug / "SKILL.md"
    if path.exists():
        return path.read_text()
    return None

async def sync_skills_to_brain():
    skills = {}
    for agent_slug in list_skills():
        content = get_skill(agent_slug)
        if content:
            skills[agent_slug] = content

    async with httpx.AsyncClient() as client:
        for slug, content in skills.items():
            point_id = hashlib.sha256(f"skill:{slug}".encode()).hexdigest()[:16]
            payload = {
                "category": "skill_definition",
                "title": f"SKILL.md for {slug}",
                "content": content[:5000],
                "agent_name": slug,
                "source": "skill-registry",
                "timestamp": time.time(),
            }
            try:
                await client.put(
                    "http://localhost:6333/collections/nexifyai_brain/points",
                    json={"points": [{"id": point_id, "vector": [0.0]*1536, "payload": payload}]},
                    timeout=10
                )
            except Exception as e:
                print(f"Sync failed for {slug}: {e}")
    return {"synced": len(skills), "agents": list(skills.keys())}
