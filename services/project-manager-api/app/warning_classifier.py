"""Warning and error classification for goose output.

Levels:
  blocker: Task must stop, cannot proceed safely.
  follow_up_required: Needs action in follow-up, but task result is valid.
  informational: Deprecation, skipping notes, known compatibility.
"""
import re
import logging

logger = logging.getLogger("pm.warning")

WARNING_PATTERNS = {
    "blocker": [
        re.compile(r"Failed to parse projects\.json", re.I),
        re.compile(r"unknown skill source", re.I),
        re.compile(r"mergeable=false", re.I),
        re.compile(r"failed checks", re.I),
        re.compile(r"permission denied", re.I),
        re.compile(r"no evidence", re.I),
        re.compile(r"cannot proceed", re.I),
        re.compile(r"Secrets?\s+exposed", re.I),
    ],
    "follow_up_required": [
        re.compile(r"Warning:", re.I),
        re.compile(r"not found", re.I),
        re.compile(r"dirty git status", re.I),
        re.compile(r"local only", re.I),
        re.compile(r"no brain update", re.I),
        re.compile(r"fake_skills_blocked:\s*true", re.I),
    ],
    "informational": [
        re.compile(r"skipping", re.I),
        re.compile(r"deprecated", re.I),
        re.compile(r"fake skill", re.I),  # Runtime reports fake-skill findings, not usage
        re.compile(r"Bridge.*OK", re.I),
        re.compile(r"registry.*ok", re.I),
    ],
}

def classify_output(output: str) -> list[dict]:
    findings = []
    for level, patterns in WARNING_PATTERNS.items():
        for pat in patterns:
            matches = pat.findall(output)
            if matches:
                findings.append({"level": level, "pattern": pat.pattern, "count": len(matches)})
    return findings

def has_blocker_warnings(output: str) -> bool:
    return any(f["level"] == "blocker" for f in classify_output(output))
