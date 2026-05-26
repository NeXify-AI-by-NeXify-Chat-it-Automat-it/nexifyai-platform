"""Tests for TaskGenerator — GitHub webhook event → PM task mapping.

Covers ALL code paths in task_generator.py:
- generate_task: all event types, all actions, edge cases
- _prioritize: None, empty, all priority labels, string labels
- _determine_mode: all event-mode mappings, readonly labels
- _build_goal: all event types, edge cases
- _redact_goal: all secret patterns, clean text
- _redact_payload_summary: all payload types, empty payload
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "services/project-manager-api")

os.environ.setdefault("DATA_DIR", "/tmp/nexify-test-tg")
os.makedirs(os.environ["DATA_DIR"], exist_ok=True)

from app.task_generator import (
    generate_task,
    _prioritize,
    _determine_mode,
    _build_goal,
    _redact_goal,
    _redact_payload_summary,
    SILENT_EVENTS,
)
from app.schemas import TaskMode, TaskPriority
from app.config import DATA_DIR

# ── Helpers ──────────────────────────────────────────────────────────────────

_DB = DATA_DIR / "tasks.db"
if _DB.exists():
    _DB.unlink()

_SESSION = str(time.time_ns())[-6:]


def _did(n: int) -> str:
    """Unique delivery ID per test call."""
    return f"test-{_SESSION}-{n:04d}"


def _ip(action: str, title: str = "Test issue", number: int = 42,
        labels: list | None = None) -> dict:
    """Build a minimal issues payload."""
    return {
        "action": action,
        "issue": {
            "number": number,
            "title": title,
            "state": "open",
            "labels": labels or [],
        },
        "repository": {"full_name": "test-org/test-repo"},
    }


def _pr(action: str, title: str = "Test PR", number: int = 7,
        labels: list | None = None) -> dict:
    """Build a minimal pull_request payload."""
    return {
        "action": action,
        "pull_request": {
            "number": number,
            "title": title,
            "labels": labels or [],
        },
        "repository": {"full_name": "test-org/test-repo"},
    }


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Event-level coverage
# ═════════════════════════════════════════════════════════════════════════════

def test_ping_no_task():
    """ping events are health-only, never create a task (caught by silent_events)."""
    r = generate_task("ping", {"hook_id": 123, "zen": "test"}, delivery_id=_did(1))
    assert r["ok"] and not r["task_created"]
    assert "silent_event" in r.get("reason", "")


def test_issues_opened_creates_task():
    """issues.opened is the primary task trigger."""
    r = generate_task("issues", _ip("opened"), delivery_id=_did(2))
    assert r["ok"] and r["task_created"]


def test_issues_reopened_creates_task():
    """issues.reopened is actionable."""
    r = generate_task("issues", _ip("reopened"), delivery_id=_did(3))
    assert r["ok"] and r["task_created"]


def test_issues_labeled_creates_task():
    """issues.labeled triggers a task for label-driven routing."""
    r = generate_task("issues", _ip("labeled", labels=[{"name": "bug"}]),
                      delivery_id=_did(4))
    assert r["ok"] and r["task_created"]


def test_issues_unlabeled_creates_task():
    """issues.unlabeled triggers a task."""
    r = generate_task("issues", _ip("unlabeled"), delivery_id=_did(5))
    assert r["ok"] and r["task_created"]


def test_issues_assigned_creates_task():
    """issues.assigned triggers a task."""
    r = generate_task("issues", _ip("assigned"), delivery_id=_did(6))
    assert r["ok"] and r["task_created"]


def test_issues_closed_no_task():
    """issues.closed is not in the actionable set."""
    r = generate_task("issues", _ip("closed"), delivery_id=_did(7))
    assert r["ok"] and not r["task_created"]


def test_issues_other_actions_no_task():
    """issues actions like 'edited', 'transferred', 'deleted' are not actionable."""
    for action in ("edited", "transferred", "deleted", "locked", "unlocked",
                   "milestoned", "demilestoned", "pinned", "unpinned"):
        r = generate_task("issues", _ip(action), delivery_id=_did(8))
        assert r["ok"] and not r["task_created"], f"{action} should not create task"


def test_issues_no_action_payload():
    """issues without action field should still create a task (actionless event)."""
    r = generate_task("issues", {
        "issue": {"number": 1, "title": "No action", "labels": []},
        "repository": {"full_name": "t/t"},
    }, delivery_id=_did(9))
    assert r["ok"] and r["task_created"]


def test_issues_empty_action_no_task():
    """issues with empty action string should still create task (actionless)."""
    r = generate_task("issues", {
        "action": "",
        "issue": {"number": 1, "title": "Empty action", "labels": []},
        "repository": {"full_name": "t/t"},
    }, delivery_id=_did(10))
    assert r["ok"] and r["task_created"]


def test_issue_comment_created():
    """issue_comment.created triggers a task."""
    p = _ip("created")
    p["comment"] = {"body": "fix this issue please"}
    r = generate_task("issue_comment", p, delivery_id=_did(11))
    assert r["ok"] and r["task_created"]
    assert r["mode"] == "plan"


def test_issue_comment_empty_body():
    """issue_comment with empty body still triggers a task."""
    p = _ip("created")
    p["comment"] = {"body": ""}
    r = generate_task("issue_comment", p, delivery_id=_did(12))
    assert r["ok"] and r["task_created"]


def test_pull_request_opened():
    """pull_request.opened triggers a review task."""
    r = generate_task("pull_request", _pr("opened"), delivery_id=_did(13))
    assert r["ok"] and r["task_created"]
    assert r["mode"] == "review"


def test_pull_request_synchronize():
    """pull_request.synchronize triggers a review task."""
    r = generate_task("pull_request", _pr("synchronize"), delivery_id=_did(14))
    assert r["ok"] and r["task_created"]


def test_pull_request_reopened():
    """pull_request.reopened triggers a review task."""
    r = generate_task("pull_request", _pr("reopened"), delivery_id=_did(15))
    assert r["ok"] and r["task_created"]


def test_pull_request_ready_for_review():
    """pull_request.ready_for_review triggers a review task."""
    r = generate_task("pull_request", _pr("ready_for_review"),
                      delivery_id=_did(16))
    assert r["ok"] and r["task_created"]


def test_pull_request_labeled():
    """pull_request.labeled triggers a review task."""
    r = generate_task("pull_request", _pr("labeled", labels=[{"name": "bug"}]),
                      delivery_id=_did(17))
    assert r["ok"] and r["task_created"]


def test_pull_request_unlabeled():
    """pull_request.unlabeled triggers a review task."""
    r = generate_task("pull_request", _pr("unlabeled"), delivery_id=_did(18))
    assert r["ok"] and r["task_created"]


def test_pull_request_closed_no_task():
    """pull_request.closed is not actionable."""
    r = generate_task("pull_request", _pr("closed"), delivery_id=_did(19))
    assert r["ok"] and not r["task_created"]


def test_workflow_run_failure_creates_task():
    """workflow_run.completed with failure creates a task."""
    p = {
        "action": "completed",
        "workflow_run": {"name": "CI", "conclusion": "failure"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("workflow_run", p, delivery_id=_did(20))
    assert r["ok"] and r["task_created"]


def test_workflow_run_cancelled_creates_task():
    """workflow_run.completed with cancellation creates a task."""
    p = {
        "action": "completed",
        "workflow_run": {"name": "Deploy", "conclusion": "cancelled"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("workflow_run", p, delivery_id=_did(21))
    assert r["ok"] and r["task_created"]


def test_workflow_run_success_no_task():
    """workflow_run.completed with success does NOT create a task."""
    p = {
        "action": "completed",
        "workflow_run": {"name": "CI", "conclusion": "success"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("workflow_run", p, delivery_id=_did(22))
    assert r["ok"] and not r["task_created"]


def test_check_suite_completed_failure():
    """check_suite.completed with failure creates a task."""
    p = {
        "action": "completed",
        "check_suite": {"head_branch": "main", "conclusion": "failure"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("check_suite", p, delivery_id=_did(23))
    assert r["ok"] and r["task_created"]


def test_check_suite_completed_success():
    """check_suite.completed with success creates a task (success still creates)."""
    p = {
        "action": "completed",
        "check_suite": {"head_branch": "main", "conclusion": "success"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("check_suite", p, delivery_id=_did(24))
    assert r["ok"] and r["task_created"]


def test_check_run_completed():
    """check_run.completed creates a task."""
    p = {
        "action": "completed",
        "check_run": {"name": "Lint", "conclusion": "failure"},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("check_run", p, delivery_id=_did(25))
    assert r["ok"] and r["task_created"]


def test_check_run_rerequested():
    """check_run.rerequested creates a task."""
    p = {
        "action": "rerequested",
        "check_run": {"name": "Test", "conclusion": ""},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("check_run", p, delivery_id=_did(26))
    assert r["ok"] and r["task_created"]


def test_check_run_requested_action():
    """check_run.requested_action creates a task."""
    p = {
        "action": "requested_action",
        "check_run": {"name": "Action Required", "conclusion": ""},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("check_run", p, delivery_id=_did(27))
    assert r["ok"] and r["task_created"]


def test_code_scanning_alert_created():
    """code_scanning_alert.created creates a task."""
    p = {
        "action": "created",
        "alert": {
            "number": 101,
            "rule": {"description": "SSRF", "severity": "error"},
        },
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("code_scanning_alert", p, delivery_id=_did(28))
    assert r["ok"] and r["task_created"]
    assert r["mode"] == "review"


def test_code_scanning_alert_reopened():
    """code_scanning_alert.reopened creates a task."""
    p = {
        "action": "reopened",
        "alert": {
            "number": 202,
            "rule": {"description": "XSS", "severity": "warning"},
        },
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("code_scanning_alert", p, delivery_id=_did(29))
    assert r["ok"] and r["task_created"]


def test_code_scanning_alert_fixed_no_task():
    """code_scanning_alert.fixed does NOT create a task (already resolved)."""
    p = {
        "action": "fixed",
        "alert": {
            "number": 203,
            "rule": {"description": "XSS", "severity": "error"},
        },
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("code_scanning_alert", p, delivery_id=_did(30))
    assert r["ok"] and not r["task_created"]


def test_code_scanning_alert_dismissed_no_task():
    """code_scanning_alert.dismissed does NOT create a task (already resolved)."""
    p = {
        "action": "dismissed",
        "alert": {
            "number": 204,
            "rule": {"description": "XSS", "severity": "error"},
        },
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("code_scanning_alert", p, delivery_id=_did(31))
    assert r["ok"] and not r["task_created"]


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Non-task events
# ═════════════════════════════════════════════════════════════════════════════

def test_silent_events_no_task():
    """All SILENT_EVENTS should never create tasks."""
    for event in sorted(SILENT_EVENTS)[:5]:  # Sample 5
        if event == "ping":
            continue  # tested separately
        r = generate_task(event, {"action": "created"})
        assert r["ok"] and not r["task_created"], f"{event} should be silent"
        assert "silent_event" in r.get("reason", "")


def test_unmapped_event_no_task():
    """Events not in actionable_actions map should not create tasks."""
    # 'discussion' is neither silent nor actionable — triggers unmapped_event
    r = generate_task("discussion", {"action": "created"})
    assert r["ok"] and not r["task_created"]
    assert "unmapped_event" in r.get("reason", "")


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Priority mapping
# ═════════════════════════════════════════════════════════════════════════════

def test_priority_p0():
    """priority-p0 label maps to P0."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "priority-p0"}]),
                      delivery_id=_did(32))
    assert r["priority"] == "P0"


def test_priority_critical():
    """critical label maps to P0."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "critical"}]),
                      delivery_id=_did(33))
    assert r["priority"] == "P0"


def test_priority_blocker():
    """blocker label maps to P0."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "blocker"}]),
                      delivery_id=_did(34))
    assert r["priority"] == "P0"


def test_priority_p1():
    """p1 label maps to P1."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "p1"}]),
                      delivery_id=_did(35))
    assert r["priority"] == "P1"


def test_priority_security():
    """security label maps to P1."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "security"}]),
                      delivery_id=_did(36))
    assert r["priority"] == "P1"


def test_priority_bug():
    """bug label maps to P1."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "bug"}]),
                      delivery_id=_did(37))
    assert r["priority"] == "P1"


def test_priority_p2():
    """p2 label maps to P2."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "p2"}]),
                      delivery_id=_did(38))
    assert r["priority"] == "P2"


def test_priority_p3_fallback():
    """Labels not matching any priority tier fall back to P3."""
    r = generate_task("issues", _ip("opened", labels=[{"name": "enhancement"}]),
                      delivery_id=_did(39))
    assert r["priority"] == "P3"


def test_priority_default_p2():
    """No labels defaults to P2."""
    r = generate_task("issues", _ip("opened"), delivery_id=_did(40))
    assert r["priority"] == "P2"


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Mode mapping
# ═════════════════════════════════════════════════════════════════════════════

def test_mode_review_for_code_scanning():
    """code_scanning_alert events get review mode."""
    p = {
        "action": "created",
        "alert": {"number": 1, "rule": {"description": "SQLI", "severity": "critical"}},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("code_scanning_alert", p, delivery_id=_did(41))
    assert r["mode"] == "review"


def test_mode_review_for_pull_request():
    """pull_request events get review mode."""
    r = generate_task("pull_request", _pr("opened"), delivery_id=_did(42))
    assert r["mode"] == "review"


def test_mode_plan_for_issue_comment():
    """issue_comment events get plan mode."""
    p = _ip("created")
    p["comment"] = {"body": "hello"}
    r = generate_task("issue_comment", p, delivery_id=_did(43))
    assert r["mode"] == "plan"


def test_mode_readonly_for_readonly_label():
    """labels of readonly/research/docs/governance set readonly mode."""
    for i, label in enumerate(("readonly", "research", "docs", "governance")):
        r = generate_task("issues",
                          _ip("opened", labels=[{"name": label}]),
                          delivery_id=_did(44 + i))
        assert r.get("mode") == "readonly", f"label '{label}' should give readonly mode (got: {r})"


def test_mode_implement_default():
    """Default mode for issues is implement."""
    r = generate_task("issues", _ip("opened"), delivery_id=_did(200))
    assert r["mode"] == "implement"


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Deduplication
# ═════════════════════════════════════════════════════════════════════════════

def test_dedupe():
    """Same delivery_id twice should dedupe on second call."""
    did = _did(99)
    r1 = generate_task("issues", _ip("opened"), delivery_id=did)
    r2 = generate_task("issues", _ip("opened"), delivery_id=did)
    assert r1["task_created"]
    assert not r2["task_created"]
    assert r2.get("duplicate") is True
    assert r2.get("existing_task_id") == r1["task_id"]


# ═════════════════════════════════════════════════════════════════════════════
# generate_task — Edge cases
# ═════════════════════════════════════════════════════════════════════════════

def test_malformed_payload():
    """Empty payload should not crash (no issue key)."""
    r = generate_task("issues", {}, delivery_id=_did(50))
    assert r["ok"]


def test_no_repository_in_payload():
    """Missing repository should not crash."""
    p = {"action": "opened", "issue": {"number": 1, "title": "No repo", "labels": []}}
    r = generate_task("issues", p, delivery_id=_did(51))
    assert r["ok"] and r["task_created"]


def test_issue_without_number():
    """Issue without number should not crash."""
    p = {
        "action": "opened",
        "issue": {"title": "No number", "labels": []},
        "repository": {"full_name": "t/t"},
    }
    r = generate_task("issues", p, delivery_id=_did(52))
    assert r["ok"] and r["task_created"]


def test_long_title_truncated():
    """Goal longer than 500 chars should be truncated."""
    long_title = "Fix " + "very long " * 100
    r = generate_task("issues", _ip("opened", title=long_title),
                      delivery_id=_did(53))
    assert r["ok"] and r["task_created"]
    assert len(r["goal"]) <= 500


def test_context_enriched_with_delivery_id():
    """Task context should be a JSON dict when delivery_id is provided."""
    r = generate_task("issues", _ip("opened"), delivery_id=_did(54))
    assert r["ok"] and r["task_created"]
    # Verify task was stored with correct context by pulling from registry
    from app.task_registry import get
    task = get(r["task_id"])
    assert task is not None
    ctx = json.loads(task.context)
    assert ctx["delivery_id"] == _did(54)
    assert ctx["event"] == "issues"
    assert ctx["action"] == "opened"


def test_context_no_delivery_id():
    """Without delivery_id, context stays as payload summary string."""
    r = generate_task("issues", _ip("opened"), delivery_id=None)
    assert r["ok"] and r["task_created"]


# ═════════════════════════════════════════════════════════════════════════════
# _prioritize — Unit tests
# ═════════════════════════════════════════════════════════════════════════════

def test_prioritize_none():
    """None labels defaults to P2."""
    assert _prioritize(None) == TaskPriority.P2


def test_prioritize_empty():
    """Empty list defaults to P2."""
    assert _prioritize([]) == TaskPriority.P2


def test_prioritize_critical_p0():
    """critical label gives P0."""
    assert _prioritize([{"name": "critical"}]) == TaskPriority.P0


def test_prioritize_blocker_p0():
    """blocker label gives P0."""
    assert _prioritize([{"name": "blocker"}]) == TaskPriority.P0


def test_prioritize_p0():
    """p0 label gives P0."""
    assert _prioritize([{"name": "p0"}]) == TaskPriority.P0


def test_prioritize_bug_p1():
    """bug label gives P1."""
    assert _prioritize([{"name": "bug"}]) == TaskPriority.P1


def test_prioritize_p1():
    """p1 label gives P1."""
    assert _prioritize([{"name": "p1"}]) == TaskPriority.P1


def test_prioritize_priority_p1():
    """priority-p1 label gives P1."""
    assert _prioritize([{"name": "priority-p1"}]) == TaskPriority.P1


def test_prioritize_p2():
    """p2 label gives P2."""
    assert _prioritize([{"name": "p2"}]) == TaskPriority.P2


def test_prioritize_priority_p2():
    """priority-p2 label gives P2."""
    assert _prioritize([{"name": "priority-p2"}]) == TaskPriority.P2


def test_prioritize_unknown_p3():
    """Unrecognized label falls through to P3."""
    assert _prioritize([{"name": "enhancement"}]) == TaskPriority.P3


def test_prioritize_p0_defeats_p1():
    """When multiple labels, P0 wins over P1."""
    assert _prioritize([{"name": "p0"}, {"name": "p1"}]) == TaskPriority.P0


def test_prioritize_p1_defeats_p2():
    """When multiple labels, P1 wins over P2."""
    assert _prioritize([{"name": "p1"}, {"name": "p2"}]) == TaskPriority.P1


def test_prioritize_str_label_critical_p0():
    """String label 'critical' gives P0."""
    assert _prioritize(["critical"]) == TaskPriority.P0


def test_prioritize_str_label_bug_p1():
    """String label 'bug' gives P1."""
    assert _prioritize(["bug"]) == TaskPriority.P1


def test_prioritize_str_label_other_p3():
    """String label 'enhancement' falls through to P3."""
    assert _prioritize(["enhancement"]) == TaskPriority.P3


# ═════════════════════════════════════════════════════════════════════════════
# _determine_mode — Unit tests
# ═════════════════════════════════════════════════════════════════════════════

def test_determine_mode_code_scanning():
    """code_scanning_alert gets review mode."""
    assert _determine_mode("code_scanning_alert", "created", []) == TaskMode.review


def test_determine_mode_workflow_fail():
    """workflow_run.completed gets review mode."""
    assert _determine_mode("workflow_run", "completed", []) == TaskMode.review


def test_determine_mode_pull_request():
    """pull_request gets review mode."""
    assert _determine_mode("pull_request", "opened", []) == TaskMode.review


def test_determine_mode_issue_comment():
    """issue_comment gets plan mode."""
    assert _determine_mode("issue_comment", "created", []) == TaskMode.plan


def test_determine_mode_readonly_label():
    """readonly label sets readonly mode."""
    assert _determine_mode("issues", "opened", [{"name": "readonly"}]) == TaskMode.readonly


def test_determine_mode_research_label():
    """research label sets readonly mode."""
    assert _determine_mode("issues", "opened", [{"name": "research"}]) == TaskMode.readonly


def test_determine_mode_docs_label():
    """docs label sets readonly mode."""
    assert _determine_mode("issues", "opened", [{"name": "docs"}]) == TaskMode.readonly


def test_determine_mode_governance_label():
    """governance label sets readonly mode."""
    assert _determine_mode("issues", "opened", [{"name": "governance"}]) == TaskMode.readonly


def test_determine_mode_default_implement():
    """Default mode for unlabelled issues is implement."""
    assert _determine_mode("issues", "opened", []) == TaskMode.implement


def test_determine_mode_str_readonly():
    """String label 'readonly' sets readonly mode."""
    assert _determine_mode("issues", "opened", ["readonly"]) == TaskMode.readonly


# ═════════════════════════════════════════════════════════════════════════════
# _build_goal — Unit tests
# ═════════════════════════════════════════════════════════════════════════════

def test_build_goal_issues():
    """issues event builds correct goal format."""
    goal = _build_goal("issues", "opened",
                       {"issue": {"number": 42, "title": "Fix bug"},
                        "repository": {"full_name": "my-org/my-repo"}})
    assert "[my-org/my-repo]" in goal
    assert "#42" in goal
    assert "Fix bug" in goal
    assert "opened" in goal


def test_build_goal_issue_comment():
    """issue_comment event builds correct goal format."""
    goal = _build_goal("issue_comment", "created",
                       {"issue": {"number": 7},
                        "comment": {"body": "This is a review comment"},
                        "repository": {"full_name": "t/t"}})
    assert "comment" in goal
    assert "review comment" in goal


def test_build_goal_issue_comment_empty_body():
    """issue_comment with empty body still builds."""
    goal = _build_goal("issue_comment", "created",
                       {"issue": {"number": 1},
                        "comment": {"body": ""},
                        "repository": {"full_name": "t/t"}})
    assert "comment:" in goal


def test_build_goal_pull_request():
    """pull_request event builds correct goal format."""
    goal = _build_goal("pull_request", "opened",
                       {"pull_request": {"number": 12, "title": "Feature X"},
                        "repository": {"full_name": "t/t"}})
    assert "PR #12" in goal
    assert "Feature X" in goal


def test_build_goal_workflow_run():
    """workflow_run event builds correct goal format."""
    goal = _build_goal("workflow_run", "completed",
                       {"workflow_run": {"name": "Deploy", "conclusion": "failure"},
                        "repository": {"full_name": "t/t"}})
    assert "Workflow 'Deploy'" in goal
    assert "failure" in goal


def test_build_goal_check_suite():
    """check_suite event builds correct goal format."""
    goal = _build_goal("check_suite", "completed",
                       {"check_suite": {"head_branch": "feature-branch",
                                        "conclusion": "failure"},
                        "repository": {"full_name": "t/t"}})
    assert "Check suite on feature-branch" in goal


def test_build_goal_check_run():
    """check_run event builds correct goal format."""
    goal = _build_goal("check_run", "completed",
                       {"check_run": {"name": "Lint", "conclusion": "failure"},
                        "repository": {"full_name": "t/t"}})
    assert "Check 'Lint'" in goal


def test_build_goal_code_scanning():
    """code_scanning_alert event builds correct goal format."""
    goal = _build_goal("code_scanning_alert", "created",
                       {"alert": {"number": 50,
                                  "rule": {"description": "SSRF vulnerability"}},
                        "repository": {"full_name": "t/t"}})
    assert "Code scanning alert #50" in goal
    assert "SSRF" in goal


def test_build_goal_no_repo():
    """Missing repository defaults to 'unknown'."""
    goal = _build_goal("issues", "opened",
                       {"issue": {"number": 1, "title": "Test"}})
    assert goal.startswith("[unknown]")


def test_build_goal_fallback():
    """Unknown event type falls back to generic format."""
    goal = _build_goal("custom_event", "triggered",
                       {"repository": {"full_name": "t/t"}})
    assert "Event: custom_event/triggered" in goal


def test_build_goal_secrets_redacted():
    """Secrets in issue title should be redacted in goal."""
    goal = _build_goal("issues", "opened",
                       {"issue": {"number": 1, "title": "key=sk-abc123def456"},
                        "repository": {"full_name": "t/t"}})
    assert "[REDACTED]" in goal
    assert "sk-abc123def456" not in goal


# ═════════════════════════════════════════════════════════════════════════════
# _redact_goal — Unit tests
# ═════════════════════════════════════════════════════════════════════════════

def test_redact_goal_sk_key():
    """sk-... API key pattern is redacted."""
    assert _redact_goal("key=sk-abc123def456") == "key=[REDACTED]"


def test_redact_goal_token():
    """Generic token pattern is redacted."""
    assert _redact_goal("token=ghp_12345abcde") == "token=[REDACTED]"


def test_redact_goal_password():
    """Password pattern is redacted."""
    result = _redact_goal("password='secret-123'")
    assert "[REDACTED]" in result


def test_redact_goal_api_key():
    """api_key pattern is redacted."""
    assert _redact_goal("api_key=abc123secret") == "api_key=[REDACTED]"


def test_redact_goal_clean_text():
    """Clean text with no secrets is unchanged."""
    text = "Fix the login button alignment"
    assert _redact_goal(text) == text


def test_redact_goal_empty():
    """Empty string is unchanged."""
    assert _redact_goal("") == ""


# ═════════════════════════════════════════════════════════════════════════════
# _redact_payload_summary — Unit tests
# ═════════════════════════════════════════════════════════════════════════════

def test_redact_payload_summary_empty():
    """Empty payload returns empty JSON object."""
    assert _redact_payload_summary({}) == "{}"


def test_redact_payload_summary_issue():
    """Issue payload extracts number, title, state."""
    result = json.loads(_redact_payload_summary(
        {"issue": {"number": 42, "title": "Fix bug", "state": "open"}}))
    assert result["issue_number"] == 42
    assert result["issue_title"] == "Fix bug"
    assert result["issue_state"] == "open"


def test_redact_payload_summary_pr():
    """PR payload extracts number and title."""
    result = json.loads(_redact_payload_summary(
        {"pull_request": {"number": 7, "title": "Feature"}}))
    assert result["pr_number"] == 7
    assert result["pr_title"] == "Feature"


def test_redact_payload_summary_workflow():
    """Workflow payload extracts name and conclusion."""
    result = json.loads(_redact_payload_summary(
        {"workflow_run": {"name": "CI", "conclusion": "failure"}}))
    assert result["workflow"] == "CI"
    assert result["conclusion"] == "failure"


def test_redact_payload_summary_alert():
    """Alert payload extracts number, rule description, severity."""
    result = json.loads(_redact_payload_summary(
        {"alert": {"number": 101,
                    "rule": {"description": "SSRF", "severity": "error"}}}))
    assert result["alert_number"] == 101
    assert result["rule"] == "SSRF"
    assert result["severity"] == "error"
