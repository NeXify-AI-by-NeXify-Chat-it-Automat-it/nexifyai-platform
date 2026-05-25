"""Skill policy - blocks fake/unknown skills."""
import logging

logger = logging.getLogger("pm.skill_policy")

BLOCKED_SKILL_SOURCES = [
    "/root/.config/goose/skills",
    "/root/.goose/skills",
    "/home/",
]

MASTER_REPO_PATH = "/opt/nexify/skills/claude-code-templates"

def check_skill_source(source_path: str) -> tuple[bool, str]:
    for blocked in BLOCKED_SKILL_SOURCES:
        if blocked in source_path:
            return False, f"Blocked: fake/unknown skill source '{source_path}'"
    return True, "Allowed"

def is_master_repo_path(path: str) -> bool:
    return path.startswith(MASTER_REPO_PATH)
