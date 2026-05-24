#!/usr/bin/env python3
"""checkpoint_summarizer.py — Structured completion summaries, not conversation."""
import json
from datetime import datetime, timezone

class CheckpointSummarizer:
    def summarize(self, task: str, status: str, details: dict = None) -> dict:
        return {"type":"completion_summary","timestamp":datetime.now(timezone.utc).isoformat(),
                "task":task,"status":status,"details":details or {},"next":"autonomous_continuation"}
    def format(self, s: dict) -> str:
        t = s.get("task","?"); st = s.get("status","?")
        det = json.dumps(s.get("details",{}), default=str)[:200]
        if st == "complete": return f"Complete: {t}. {det}. Continuing."
        if st == "failed": return f"FAILED: {t}. Recovery."
        if st == "escalated": return f"ESCALATION: {t}. Human needed."
        return f"Status: {t} -> {st}."

SUMMARIZER = CheckpointSummarizer()

if __name__ == "__main__":
    s = SUMMARIZER.summarize("Frontend transition", "complete", {"files":3,"build":"ok"})
    print(SUMMARIZER.format(s))