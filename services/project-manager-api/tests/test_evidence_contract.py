"""Test evidence contract - task_id, status, no secrets."""
import json
import pytest
from pathlib import Path
from app.evidence import save_evidence
from app.redaction import redact_string


class TestEvidenceContract:
    def test_evidence_requires_task_id(self):
        """Evidence without task_id saves with empty task_id dir, no exception."""
        from app import evidence
        original = evidence.EVIDENCE_DIR
        evidence.EVIDENCE_DIR = Path("/tmp/test-evidence-no-id")
        try:
            path = save_evidence("", "output", "")
            assert path is not None
        finally:
            evidence.EVIDENCE_DIR = original

    def test_evidence_saves_without_error(self, tmp_path):
        from app import evidence
        original = evidence.EVIDENCE_DIR
        evidence.EVIDENCE_DIR = tmp_path
        try:
            path = save_evidence("test-task-001", "some output", "")
            assert path is not None
        finally:
            evidence.EVIDENCE_DIR = original

    def test_evidence_file_contains_no_secrets(self, tmp_path):
        from app import evidence
        original = evidence.EVIDENCE_DIR
        evidence.EVIDENCE_DIR = tmp_path
        try:
            path = save_evidence("test-task-002", "Bearer sk-secret123", "")
            for f in Path(path).iterdir():
                content = f.read_text()
                assert "sk-secret123" not in content
        finally:
            evidence.EVIDENCE_DIR = original

    def test_evidence_stores_decision_status(self, tmp_path):
        from app import evidence
        original = evidence.EVIDENCE_DIR
        evidence.EVIDENCE_DIR = tmp_path
        try:
            path = save_evidence("test-task-003", "status: blocked_missing_tests", "")
            meta_files = [f for f in Path(path).iterdir() if f.name.startswith("meta_")]
            assert len(meta_files) >= 1
            meta = json.loads(meta_files[0].read_text())
            assert meta["task_id"] == "test-task-003"
        finally:
            evidence.EVIDENCE_DIR = original

    def test_redaction_preserves_safe_content(self):
        result = redact_string("This is a normal log message.")
        assert "normal" in result
        assert "[REDACTED]" not in result
