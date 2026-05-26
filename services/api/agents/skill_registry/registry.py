"""
NeXifyAI Skill Registry — manages all agent SKILL.md definitions.
Loads skills from filesystem and syncs to Brain.
"""
import os, json, httpx, hashlib, time, re, logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("nexifyai.skill_registry")

SKILLS_DIR = Path(__file__).parent / "skills"

# Sicherheit: Erlaubtes Pattern für Agent-Slugs (alphanumerisch, Bindestrich, Unterstrich)
_SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


def _is_safe_slug(agent_slug: str) -> bool:
    """Prüft, ob ein Agent-Slug sicher ist (kein Path-Traversal)."""
    return bool(_SLUG_PATTERN.match(agent_slug)) and ".." not in agent_slug and "/" not in agent_slug


def list_skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    return sorted([
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists() and _is_safe_slug(d.name)
    ])

def get_skill(agent_slug: str) -> Optional[str]:
    if not _is_safe_slug(agent_slug):
        return None
    path = SKILLS_DIR / agent_slug / "SKILL.md"
    # resolve + verify within allowed dir (double-check against path traversal)
    try:
        resolved = path.resolve()
        if not str(resolved).startswith(str(SKILLS_DIR.resolve())):
            logger.warning("Path-Traversal abgewehrt in get_skill: %s", agent_slug)
            return None
        if resolved.exists():
            return resolved.read_text()
    except (ValueError, OSError, RuntimeError) as e:
        logger.error("Fehler bei get_skill(%s): %s", agent_slug, e)
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
