"""Test project tracker - robust parsing with error handling."""
import json
import pytest
from pathlib import Path
from app.project_tracker import load_tracker, validate_tracker


VALID_PROJECTS = json.dumps({
    "projects": {
        "/path/one": {"path": "/path/one", "last_accessed": "2026-05-25T00:00:00"},
    }
})


class TestLoadTracker:
    def test_loads_valid_json(self, tmp_path):
        f = tmp_path / "projects.json"
        f.write_text(VALID_PROJECTS)
        from app import project_tracker
        project_tracker.TRACKER_PATHS = [f]
        ok, data, msg = load_tracker()
        assert ok is True
        assert data is not None

    def test_empty_file_returns_error(self, tmp_path):
        f = tmp_path / "projects.json"
        f.write_text("")
        from app import project_tracker
        project_tracker.TRACKER_PATHS = [f]
        ok, data, msg = load_tracker()
        assert ok is False
        assert data is None
        assert "empty" in msg.lower()

    def test_invalid_json_returns_error(self, tmp_path):
        f = tmp_path / "projects.json"
        f.write_text("{invalid json}")
        from app import project_tracker
        project_tracker.TRACKER_PATHS = [f]
        ok, data, msg = load_tracker()
        assert ok is False
        assert data is None
        assert "Failed to parse" in msg

    def test_no_file_returns_fallback(self, tmp_path):
        from app import project_tracker
        project_tracker.TRACKER_PATHS = [tmp_path / "nonexistent.json"]
        ok, data, msg = load_tracker()
        assert ok is True
        assert data == []
        assert "No projects.json found" in msg


class TestValidateTracker:
    def test_valid_list(self):
        ok, msg = validate_tracker([])
        assert ok is True

    def test_valid_dict(self):
        ok, msg = validate_tracker({"projects": {}})
        assert ok is True

    def test_null_is_invalid(self):
        ok, msg = validate_tracker(None)
        assert ok is False
        assert "null" in msg.lower()
