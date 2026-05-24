#!/usr/bin/env python3
"""autonomous_response_filter.py — Filters outgoing responses."""
import yaml, os, re
from assistant_pattern_blocker import BLOCKER

ALLOWED = ["status_update","governance_alert","architecture_decision","incident_report",
           "completion_summary","strategic_escalation","error_report","verification_result","decision_record","memory_update"]

class AutonomousResponseFilter:
    def filter(self, text: str, response_type: str = None) -> dict:
        if response_type and response_type not in ALLOWED:
            return {"allowed": False, "reason": f"Type '{response_type}' not allowed"}
        br = BLOCKER.check(text)
        if br["blocked"]:
            return {"allowed": False, "reason": f"Blocked pattern: {br['pattern']}"}
        text_s = text.strip()
        if text_s.rstrip(".").endswith("?") and len(text_s) < 120:
            return {"allowed": False, "reason": "Question continuation not allowed"}
        return {"allowed": True}
    def classify(self, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["error","fail","blocked","crash"]): return "error_report"
        if any(w in lower for w in ["alert","warning","critical","escalat"]): return "governance_alert"
        if any(w in lower for w in ["build","deploy","deployment"]): return "status_update"
        if any(w in lower for w in ["decision","authority","approve"]): return "architecture_decision"
        if any(w in lower for w in ["incident","compromise","breach"]): return "incident_report"
        if any(w in lower for w in ["complete","done","finish","summary"]): return "completion_summary"
        return "status_update"

FILTER = AutonomousResponseFilter()

if __name__ == "__main__":
    tests = [("Build complete. 23/23 pass.", "completion_summary"), ("Soll ich weitermachen?", None)]
    for t, rtype in tests:
        r = FILTER.filter(t, rtype)
        print(f"  {t:45s} -> {'OK' if r['allowed'] else 'BLOCKED'}: {r.get('reason','')}")