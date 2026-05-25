"""Test skill policy - blocks fake/unknown sources."""
import pytest
from app.skill_policy import check_skill_source, is_master_repo_path, BLOCKED_SKILL_SOURCES


class TestCheckSkillSource:
    def test_local_goose_skills_blocked(self):
        allowed, msg = check_skill_source("/root/.config/goose/skills/brain.md")
        assert allowed is False
        assert "Blocked" in msg

    def test_home_dir_blocked(self):
        allowed, msg = check_skill_source("/home/user/.goose/skills/custom.md")
        assert allowed is False
        assert "Blocked" in msg

    def test_master_repo_allowed(self):
        allowed, msg = check_skill_source("/opt/nexify/skills/claude-code-templates/skills/agent.md")
        assert allowed is True
        assert "Allowed" in msg

    def test_goose_bridge_allowed(self):
        allowed, msg = check_skill_source("/opt/nexify/goose-skill-bridge/registry/skills.json")
        assert allowed is True
        assert "Allowed" in msg

    def test_empty_path_disallowed(self):
        allowed, msg = check_skill_source("/root/.goose/skills/")
        assert allowed is False
        assert "Blocked" in msg


class TestIsMasterRepoPath:
    def test_master_repo_recognized(self):
        assert is_master_repo_path("/opt/nexify/skills/claude-code-templates/skills") is True

    def test_other_path_not_master(self):
        assert is_master_repo_path("/opt/nexify/goose-skill-bridge/registry") is False

    def test_blocked_list_contains_key_paths(self):
        assert any("/root/.config/goose/skills" in p for p in BLOCKED_SKILL_SOURCES)
