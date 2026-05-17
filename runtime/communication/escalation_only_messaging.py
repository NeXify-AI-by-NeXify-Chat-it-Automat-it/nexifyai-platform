#!/usr/bin/env python3
"""escalation_only_messaging.py — Only communicate for true escalations."""
import yaml, os, sys

class EscalationOnlyMessaging:
    def __init__(self):
        self.categories = self._load()
    def _load(self):
        path = "/runtime/communication/communication_policy.yaml"
        if os.path.exists(path):
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            return data.get("escalation_only_categories", [])
        return []
    def requires_human(self, action: dict) -> bool:
        atype = action.get("type", action.get("action", ""))
        for cat in self.categories:
            if cat in atype: return True
        kws = ["irreversible","legal","payment","credential","delete","constitutional","impossible"]
        for kw in kws:
            if kw in atype: return True
        return False
    def should_communicate(self, action: dict) -> dict:
        if self.requires_human(action):
            return {"communicate": True, "mode": "escalation", "reason": "Requires human"}
        return {"communicate": False, "mode": "autonomous", "reason": "No human needed"}

ESCALATION = EscalationOnlyMessaging()

if __name__ == "__main__":
    for t in [{"type":"code_refactor"},{"type":"credential_compromise"}]:
        r = ESCALATION.should_communicate(t)
        print(f"  {t['type']:35s} -> comm={r['communicate']}: {r['mode']}")