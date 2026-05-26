"""Policy gate - validates tasks before execution.

Rules:
1. DENIED_GLOBAL patterns are always rejected (destructive shell commands).
2. For readonly mode: DENIED_IN_READONLY words are checked via TOKEN-BOUNDARY match.
   "No GitHub pushes" is safe (negated). "Push to main" is blocked.
   Uses word-boundary regex to avoid substring false positives.
3. Explicit denied_actions are also token-boundary matched.
4. Goal must be at least 10 characters.
"""
import logging
import re
from app.schemas import TaskRecord, TaskStatus, TaskMode
from app.task_registry import update_status

logger = logging.getLogger("pm.policy")

# Global always-rejected patterns (literal substring, these are destructive)
DENIED_GLOBAL = ["rm -rf /", "format", "mkfs", "dd if=", ":(){:|:&};:"]

# Words blocked in readonly mode — token-boundary match, NOT substring
DENIED_IN_READONLY = [
    "write",
    "delete",
    "deploy",
    "merge",
    "push",
    "commit",
    "patch",
    "destroy",
    "drop",
    "truncate",
    "alter",
    "insert",
    "change",
    "install",
    "uninstall",
    "restart",
    "stop",
    "kill",
    "reboot",
    "upgrade",
    "downgrade",
    "modify",
    "overwrite",
]

# Whitelist: negated/restriction phrases that contain deny words but are safe
# These prefix-phrases indicate the task is FORBIDDING the action, not requesting it.
NEGATION_PREFIXES = [
    "no ",
    "not ",
    "never ",
    "without ",
    "don't ",
    "do not ",
    "must not ",
    "shall not ",
    "should not ",
    "cannot ",
    "can't ",
    "won't ",
    "banned ",
    "forbidden ",
    "prohibited ",
    "avoid ",
    "prevent ",
    "abstain from ",
    "refrain from ",
]

# Negation phrases in German
NEGATION_PREFIXES_DE = [
    "kein ", "keine ", "keinen ", "keinem ",
    "nicht ", "niemals ",
    "darf nicht ", "dürfen nicht ",
    "soll nicht ", "sollen nicht ",
    "keine änderung", "keine Änderung",
    "nur lesen", "read-only", "readonly",
    "nur anzeigen",
]


def _is_negated(text_lower: str, word: str) -> bool:
    """Check if a deny-word appears inside a negated/restriction clause.

    Uses regex to find word preceded by a negation prefix.
    Returns True if the word is safely negated, False otherwise.
    """
    all_prefixes = NEGATION_PREFIXES + NEGATION_PREFIXES_DE
    for prefix in all_prefixes:
        # Build regex: prefix + optional words + our deny-word, with word boundaries
        pattern = re.escape(prefix.strip()) + r"(?:\s+\w+){0,8}\s+" + re.escape(word) + r"\b"
        if re.search(pattern, text_lower):
            return True
    return False


def _token_match(pattern: str, text: str) -> bool:
    """Word-boundary match: 'push' matches 'push' but NOT 'pushing' or 'pushs'.

    Returns True if pattern found as a standalone word in text.
    """
    return bool(re.search(r"\b" + re.escape(pattern) + r"\b", text))


def _is_allowed_by_mode(task: TaskRecord) -> bool:
    """Check if task goal is compatible with the task's own mode and allowed_actions.

    If `task.allowed_actions` is non-empty, we check if the goal aligns with those actions.
    If `task.mode` is readonly, we check for denied words (with negation awareness).
    """
    goal_lower = task.goal.lower()

    if task.allowed_actions:
        # If allowed_actions specified, goal must contain at least one
        for action in task.allowed_actions:
            if _token_match(action.lower(), goal_lower):
                return True
        # No allowed action found verbatim; check if entire goal is in a safe mode
        # Don't auto-reject — fall through to mode check
        pass

    if task.mode == TaskMode.readonly:
        for pattern in DENIED_IN_READONLY:
            if _token_match(pattern, goal_lower):
                if _is_negated(goal_lower, pattern):
                    continue  # Safely negated, e.g. "No file edits"
                return False

    return True


def evaluate(task: TaskRecord) -> tuple[bool, str]:
    """Evaluate task against policy rules. Returns (approved, reason)."""
    goal_lower = task.goal.lower()

    # 1. Check globally denied destructive patterns (literal substring here is fine)
    for pattern in DENIED_GLOBAL:
        if pattern in goal_lower:
            return False, f"Denied: destructive pattern '{pattern}' in goal"

    # 2. Check goal length
    if len(task.goal) < 10:
        return False, "Denied: goal too short (< 10 chars)"

    # 3. Check mode compatibility (word-boundary with negation awareness)
    if not _is_allowed_by_mode(task):
        for pattern in DENIED_IN_READONLY:
            if _token_match(pattern, goal_lower):
                return False, (
                    f"Denied: goal contains action '{pattern}' incompatible with mode '{task.mode.value}'. "
                    f"Use 'no {pattern}', 'without {pattern}', switch to mode='implement', "
                    f"or add '{pattern}' to allowed_actions."
                )
        return False, f"Denied: goal incompatible with mode '{task.mode.value}'"

    # 4. Check explicit denied_actions (word-boundary)
    for denied in task.denied_actions:
        if _token_match(denied.lower(), goal_lower):
            # If the denied action appears in a negation context, it's fine
            if _is_negated(goal_lower, denied.lower()):
                continue
            return False, f"Denied: explicit denied action '{denied}' found in goal"

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
