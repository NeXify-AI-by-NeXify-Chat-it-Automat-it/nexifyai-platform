"""Skill selector - matches task to relevant skills with evidence."""
import json
import logging
from app.skill_registry import load_registry, validate_registry, get_relevant_skills
from app.evidence import save_evidence

logger = logging.getLogger("pm.skill_selector")

async def select_and_validate(task_id: str, goal: str, mode: str) -> tuple[bool, str, list[dict]]:
    reg = load_registry()
    valid, reason = validate_registry(reg)
    if not valid:
        logger.warning("Skill registry invalid for task %s: %s", task_id, reason)
        return False, reason, []
    relevant = get_relevant_skills(goal, mode, reg)
    evidence = {
        "task_id": task_id,
        "registry_valid": valid,
        "registry_source": reg.get("skills", {}).get("meta", {}).get("source_repo", ""),
        "registry_commit": reg.get("skills", {}).get("meta", {}).get("source_commit", ""),
        "total_skills": reg.get("skills", {}).get("meta", {}).get("total_skills", 0),
        "relevant_categories": relevant,
        "fake_skills_blocked": True,
    }
    save_evidence(task_id, json.dumps(evidence, indent=2), "")
    return True, "", relevant
