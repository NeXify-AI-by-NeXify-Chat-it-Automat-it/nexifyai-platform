#!/usr/bin/env python3
"""assistant_pattern_blocker.py — Blocks assistant conversational patterns."""
import re, yaml, os

class AssistantPatternBlocker:
    def __init__(self):
        self.blocked = []
        self._load()
    def _load(self):
        path = "/runtime/communication/communication_policy.yaml"
        if os.path.exists(path):
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            for entry in data.get("forbidden_response_patterns", []):
                self.blocked.append((re.compile(entry["pattern"]), entry["severity"]))
    def check(self, text: str) -> dict:
        for pattern, severity in self.blocked:
            if pattern.search(text):
                return {"blocked": True, "pattern": pattern.pattern, "severity": severity}
        questions = [r"\bcontinue\?\b", r"\bproceed\?\b", r"\bshall I\b", r"\bshould I\b", r"\bcan I\b"]
        for q in questions:
            if re.search(q, text, re.IGNORECASE):
                return {"blocked": True, "pattern": q, "severity": "block"}
        return {"blocked": False}

BLOCKER = AssistantPatternBlocker()

if __name__ == "__main__":
    tests = ["Soll ich weitermachen?", "Build complete.", "should I continue?"]
    for t in tests:
        r = BLOCKER.check(t)
        status = "BLOCKED" if r["blocked"] else "ALLOWED"
        print(f"  {t:40s} -> {status}")