"""Test warning classifier."""
import pytest
from app.warning_classifier import classify_output, has_blocker_warnings


class TestWarningClassifier:
    def test_parse_error_is_blocker(self):
        findings = classify_output("Failed to parse projects.json file")
        blocker = [f for f in findings if f["level"] == "blocker"]
        assert len(blocker) >= 1
        assert "Failed to parse" in blocker[0]["pattern"]

    def test_generic_warning_is_follow_up(self):
        findings = classify_output("Warning: something might be wrong")
        follow = [f for f in findings if f["level"] == "follow_up_required"]
        assert len(follow) >= 1

    def test_clean_output_no_findings(self):
        findings = classify_output("Everything is fine")
        assert len(findings) == 0

    def test_has_blocker_detects_blockers(self):
        assert has_blocker_warnings("Failed to parse projects.json") is True

    def test_has_blocker_returns_false_for_clean(self):
        assert has_blocker_warnings("All good") is False

    def test_multiple_warnings_collected(self):
        findings = classify_output("Warning: first\nFailed to parse projects.json")
        assert len(findings) >= 2

    def test_known_harmless_warning_is_follow_up_not_blocker(self):
        findings = classify_output("Warning: deprecated endpoint /old/api will be removed")
        blocker = [f for f in findings if f["level"] == "blocker"]
        follow = [f for f in findings if f["level"] == "follow_up_required"]
        assert len(blocker) == 0
        assert len(follow) >= 1

    def test_skipping_is_informational(self):
        findings = classify_output("skipping file test.py")
        info = [f for f in findings if f["level"] == "informational"]
        assert len(info) >= 1
