"""TaskGenerator — maps GitHub webhook events to PM API TaskRecords.

Policies:
- ping events → no task (health/evidence only)
- issues.opened/reopened → task
- issue_comment.created → task (if actionable)
- pull_request.opened/synchronize/ready_for_review → task
- workflow_run.completed (failure/cancelled) → task
- check_run/check_suite failure → task
- code_scanning_alert created/reopened → task
- All other events → no task (silent ack)
- Dedupe via delivery_id as external_event_id in TaskRecord
- No secrets in task payloads
"""

import json
import logging
from typing import Any

from app.schemas import TaskRecord, TaskStatus, TaskMode, TaskPriority
from app.task_registry import insert, generate_task_id, now_iso, get_by_external_event

logger = logging.getLogger("pm.task_generator")

# Events that we don't create tasks for
SILENT_EVENTS = {
    "ping", "marketplace_purchase", "member", "membership",
    "organization", "org_block", "public", "repository_vulnerability_alert",
    "star", "status", "team", "team_add", "watch",
    "deployment", "deployment_status", "page_build", "create", "delete",
    "fork", "gollum", "label", "milestone", "project", "project_card",
    "project_column", "release",
}


def _prioritize(labels: list[dict] | None) -> TaskPriority:
    """Map GitHub labels to task priority."""
    if not labels:
        return TaskPriority.P2
    label_names = [l.get("name", "").lower() if isinstance(l, dict) else str(l).lower() for l in labels]
    if any("p0" in n or "priority-p0" in n or "critical" in n or "blocker" in n for n in label_names):
        return TaskPriority.P0
    if any("p1" in n or "priority-p1" in n or "security" in n or "bug" in n for n in label_names):
        return TaskPriority.P1
    if any("p2" in n or "priority-p2" in n for n in label_names):
        return TaskPriority.P2
    return TaskPriority.P3


def _determine_mode(event: str, action: str | None, labels: list[dict] | None) -> TaskMode:
    """Determine task mode based on event context."""
    if event == "code_scanning_alert" or (event == "workflow_run" and action == "completed"):
        return TaskMode.review
    if event == "pull_request":
        return TaskMode.review
    if event == "issue_comment":
        return TaskMode.plan
    if labels and any(
        l.get("name", "").lower() in ("readonly", "research", "docs", "governance")
        if isinstance(l, dict) else str(l).lower() in ("readonly", "research", "docs", "governance")
        for l in labels
    ):
        return TaskMode.readonly
    return TaskMode.implement


SENSITIVE_PATTERNS_GOAL = [
    r"(?i)(key|secret|token|password|api_key|apikey|sk-[a-z0-9]+)[\s:=]+['\"]?[a-z0-9_\-\.]{8,}",
]


def _redact_goal(text: str) -> str:
    """Remove secrets from goal text before storing."""
    import re
    for pat in SENSITIVE_PATTERNS_GOAL:
        text = re.sub(pat, r"\1=[REDACTED]", text)
    return text


def _build_goal(event: str, action: str | None, payload: dict) -> str:
    """Build a concise goal from the GitHub event payload."""
    repo_full = (payload.get("repository") or {}).get("full_name", "unknown")
    
    if event == "issues":
        issue = payload.get("issue", {})
        number = issue.get("number", "?")
        title = _redact_goal((issue.get("title") or "")[:200])
        return f"[{repo_full}] Issue #{number}: {title} (action: {action})"

    if event == "issue_comment":
        issue = payload.get("issue", {})
        number = issue.get("number", "?")
        comment_preview = (payload.get("comment", {}).get("body", "") or "")[:80]
        return f"[{repo_full}] Issue #{number} comment: {comment_preview}..."

    if event == "pull_request":
        pr = payload.get("pull_request", {})
        number = pr.get("number", "?")
        title = (pr.get("title") or "")[:100]
        return f"[{repo_full}] PR #{number}: {title} (action: {action})"

    if event == "workflow_run":
        run = payload.get("workflow_run", {})
        name = run.get("name", "?")
        conclusion = run.get("conclusion", "?")
        return f"[{repo_full}] Workflow '{name}' concluded: {conclusion}"

    if event == "check_suite":
        suite = payload.get("check_suite", {})
        branch = (suite.get("head_branch") or "?")
        conclusion = suite.get("conclusion", "?")
        return f"[{repo_full}] Check suite on {branch}: {conclusion}"

    if event == "check_run":
        run = payload.get("check_run", {})
        name = run.get("name", "?")
        conclusion = run.get("conclusion", "?")
        return f"[{repo_full}] Check '{name}': {conclusion}"

    if event == "code_scanning_alert":
        alert = payload.get("alert", {})
        number = alert.get("number", "?")
        rule_desc = (alert.get("rule", {}).get("description", "") or "?")[:80]
        return f"[{repo_full}] Code scanning alert #{number}: {rule_desc} (action: {action})"

    return f"[{repo_full}] Event: {event}/{action}"


def _redact_payload_summary(payload: dict) -> str:
    """Safe summary of payload — no secrets, no full bodies."""
    summary = {}
    if payload.get("issue"):
        summary["issue_number"] = payload["issue"].get("number")
        summary["issue_title"] = (payload["issue"].get("title") or "")[:80]
        summary["issue_state"] = payload["issue"].get("state")
    if payload.get("pull_request"):
        summary["pr_number"] = payload["pull_request"].get("number")
        summary["pr_title"] = (payload["pull_request"].get("title") or "")[:80]
    if payload.get("workflow_run"):
        summary["workflow"] = payload["workflow_run"].get("name")
        summary["conclusion"] = payload["workflow_run"].get("conclusion")
    if payload.get("alert"):
        summary["alert_number"] = payload["alert"].get("number")
        summary["rule"] = (payload["alert"].get("rule", {}).get("description", "") or "?")[:80]
        summary["severity"] = payload["alert"].get("rule", {}).get("severity")
    return json.dumps(summary, default=str, ensure_ascii=False)


def generate_task(event_type: str, payload: dict, delivery_id: str | None = None) -> dict[str, Any]:
    """Main entry: analyze event and create a PM task if actionable.

    Returns:
        {"ok": true, "task_created": true/false, "task_id": "..." or None, "reason": "...", ...}
    """
    action = None
    if isinstance(payload.get("action"), str) and payload["action"]:
        action = payload["action"].lower()

    # Silent events — no task needed
    if event_type in SILENT_EVENTS:
        logger.debug("Silent event %s — no task", event_type)
        return {"ok": True, "task_created": False, "reason": f"silent_event:{event_type}"}

    # ping — always health evidence
    if event_type == "ping":
        hook_id = payload.get("hook_id", "?")
        logger.info("Ping received (hook_id=%s) — no task", hook_id)
        return {"ok": True, "task_created": False, "reason": "ping"}

    # Determine if actionable
    actionable_actions = {
        "issues": {"opened", "reopened", "labeled", "unlabeled", "assigned"},
        "issue_comment": {"created"},
        "pull_request": {"opened", "synchronize", "reopened", "ready_for_review", "labeled", "unlabeled"},
        "workflow_run": {"completed"},
        "check_suite": {"completed"},
        "check_run": {"completed", "rerequested", "requested_action"},
        "code_scanning_alert": {"created", "reopened", "fixed", "dismissed"},
    }

    event_actions = actionable_actions.get(event_type, set())
    if not event_actions:
        logger.debug("Unmapped event %s — no task", event_type)
        return {"ok": True, "task_created": False, "reason": f"unmapped_event:{event_type}"}

    # If no action or action not in actionable set → no task unless actionless event
    if action and action not in event_actions:
        logger.debug("Event %s/%s not actionable — no task", event_type, action)
        return {"ok": True, "task_created": False, "reason": f"action_not_actionable:{event_type}/{action}"}

    # workflow_run.completed with success → no coding task (evidence only)
    if event_type == "workflow_run" and action == "completed":
        conclusion = (payload.get("workflow_run", {}).get("conclusion") or "").lower()
        if conclusion == "success":
            return {"ok": True, "task_created": False, "reason": "workflow_success_no_task_needed"}

    # code_scanning_alert fixed/dismissed → no task (already resolved)
    if event_type == "code_scanning_alert" and action in ("fixed", "dismissed"):
        return {"ok": True, "task_created": False, "reason": f"alert_already_{action}"}

    # Dedupe: check delivery_id
    if delivery_id:
        existing = get_by_external_event(delivery_id)
        if existing:
            logger.info("Duplicate delivery %s — existing task %s", delivery_id, existing.task_id)
            return {"ok": True, "duplicate": True, "task_created": False, "existing_task_id": existing.task_id}

    # Build task
    repo = (payload.get("repository") or {}).get("full_name", "")
    labels = None
    issue_number = None
    pr_number = None

    if payload.get("issue"):
        issue_number = payload["issue"].get("number")
        labels = payload["issue"].get("labels")
    elif payload.get("pull_request"):
        pr_number = payload["pull_request"].get("number")
        labels = payload["pull_request"].get("labels")
    elif payload.get("alert"):
        labels = [{"name": "security"}]  # default for alerts

    priority = _prioritize(labels)
    mode = _determine_mode(event_type, action, labels)
    goal = _build_goal(event_type, action, payload)
    summary = _redact_payload_summary(payload)

    # Truncate goal to schema limit
    if len(goal) > 500:
        goal = goal[:497] + "..."

    task_id = generate_task_id()
    task = TaskRecord(
        task_id=task_id,
        status=TaskStatus.queued,
        created_at=now_iso(),
        updated_at=now_iso(),
        created_by=f"github_webhook:{event_type}/{action or '?'}",
        goal=goal,
        mode=mode,
        priority=priority,
        project="github-webhook",
        repo=repo,
        external_event_id=delivery_id or "",
        context=summary,
        evidence_required=["webhook_delivery_ok", "worker_output", "brain_update"],
        brain_context_required=True,
    )

    # Enrich context
    if delivery_id:
        task.context = json.dumps({
            "delivery_id": delivery_id,
            "payload_summary": summary,
            "event": event_type,
            "action": action,
            "issue_number": issue_number,
            "pr_number": pr_number,
        })

    insert(task)
    logger.info("Task %s created from webhook %s/%s (priority=%s, mode=%s)",
                task_id, event_type, action or "?", priority.value, mode.value)

    return {
        "ok": True,
        "task_created": True,
        "task_id": task_id,
        "event": event_type,
        "action": action,
        "priority": priority.value,
        "mode": mode.value,
        "goal": goal,
    }
