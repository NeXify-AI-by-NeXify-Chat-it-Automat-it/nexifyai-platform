"""Policy gate - validates tasks before execution."""
import logging
from app.schemas import TaskRecord, TaskStatus, TaskMode
from app.task_registry import update_status

logger = logging.getLogger("pm.policy")

DENIED_GLOBAL = ["rm -rf /", "format", "mkfs", "dd if=", ":(){:|:&};:"]
DENIED_IN_READONLY = ["write", "delete", "push", "deploy", "merge"]

def evaluate(task: TaskRecord) -> tuple[bool, str]:
    goal_lower = task.goal.lower()
    for pattern in DENIED_GLOBAL:
        if pattern in goal_lower:
            return False, f"Denied: destructive pattern '{pattern}' in goal"
    if task.mode == TaskMode.readonly:
        for pattern in DENIED_IN_READONLY:
            if pattern in goal_lower:
                return False, f"Denied: write action '{pattern}' in readonly mode"
    for denied in task.denied_actions:
        if denied.lower() in goal_lower:
            return False, f"Denied: explicit denied action '{denied}' in goal"
    if len(task.goal) < 10:
        return False, "Denied: goal too short (< 10 chars)"
    return True, "Approved"

def gate(task: TaskRecord) -> TaskRecord:
    approved, reason = evaluate(task)
    if not approved:
        logger.warning("Task %s rejected: %s", task.task_id, reason)
        update_status(task.task_id, TaskStatus.rejected, error=reason)
        task.status = TaskStatus.rejected
        task.error = reason
        task.updated_at = task.created_at
    return task
