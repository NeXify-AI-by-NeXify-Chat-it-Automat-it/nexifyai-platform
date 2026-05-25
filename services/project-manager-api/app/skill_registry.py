"""Skill registry loader and validator."""
import json
import logging
from pathlib import Path
from app.config import REGISTRY_DIR

logger = logging.getLogger("pm.skill_registry")

REQUIRED_FILES = ["skills.json", "index.md", "scan-metadata.json"]

def load_registry() -> dict:
    reg = {}
    for fname in ["skills.json", "agents.json", "hooks.json", "commands.json", "mcp.json", "settings.json"]:
        fpath = REGISTRY_DIR / fname
        if fpath.exists():
            try:
                data = json.loads(fpath.read_text())
                # Normalize: if top-level has source_repo, wrap into meta
                if isinstance(data, dict) and "source_repo" in data and "meta" not in data:
                    data["meta"] = {
                        "source_repo": data.get("source_repo", ""),
                        "source_commit": data.get("source_commit", ""),
                        "scanned_at": data.get("scanned_at", ""),
                        "total_skills": data.get("total_skills", 0),
                    }
                reg[fname.replace(".json", "")] = data
            except json.JSONDecodeError as e:
                logger.error("Registry %s invalid: %s", fname, e)
                return {}
        else:
            logger.warning("Registry %s missing", fname)
    return reg

def validate_registry(reg: dict) -> tuple[bool, str]:
    if not reg:
        return False, "Registry is empty"
    if "skills" not in reg:
        return False, "Registry missing skills.json"
    meta = reg["skills"].get("meta", {})
    if not meta.get("source_repo"):
        return False, "Registry missing source_repo"
    if meta.get("total_skills", 0) == 0:
        return False, "Registry reports 0 skills"
    return True, "Registry valid"

def get_relevant_skills(task_goal: str, task_mode: str, reg: dict) -> list[dict]:
    skills_data = reg.get("skills", {})
    total = skills_data.get("meta", {}).get("total_skills", 0)
    categories = skills_data.get("categories", [])
    goal_lower = task_goal.lower()
    relevant = []

    # Normalize: categories can be list[str] or list[dict]
    normalized = []
    for cat in categories:
        if isinstance(cat, str):
            normalized.append({"name": cat, "skill_count": 0})
        elif isinstance(cat, dict):
            normalized.append(cat)
    categories = normalized

    for cat in categories:
        score = 0
        name = cat.get("name", "").lower()
        if name in goal_lower:
            score += 3
        if task_mode in name:
            score += 2
        if score > 0:
            relevant.append({"category": cat["name"], "skills": cat.get("skill_count", 0), "relevance": score})
    if not relevant:
        relevant.append({"category": "all", "skills": total, "relevance": 1, "note": "no direct keyword match, all skills available"})
    relevant.sort(key=lambda x: x["relevance"], reverse=True)
    return relevant
