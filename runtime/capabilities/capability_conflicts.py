#!/usr/bin/env python3
"""capability_conflicts.py -- Conflict detection for MCP capabilities (prevent competing invocations)."""
import json, logging
log = logging.getLogger("cap-conflicts")

EXCLUSIONS = [
    {"if_active": "deployment.run", "block": "deployment.rollback"},
    {"if_active": "github.pr.create", "block": "github.pr.merge"},
    {"if_active": "infra.restart", "block": "deployment.run"},
]

class CapabilityConflictDetector:
    def __init__(self):
        self._active = {}
    def activate(self, cap_id):
        for ex in EXCLUSIONS:
            if ex["if_active"] == cap_id:
                self._active[ex["block"]] = True
        self._active[cap_id] = True
    def can_activate(self, cap_id):
        return not self._active.get(cap_id, False)
    def deactivate(self, cap_id):
        self._active.pop(cap_id, None)
        for ex in EXCLUSIONS:
            self._active.pop(ex["block"], None)
    def clear(self):
        self._active = {}

DETECTOR = CapabilityConflictDetector()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    DETECTOR.activate("deployment.run")
    print(f"Can rollback: {DETECTOR.can_activate('deployment.rollback')}")
    print(f"Can pr.merge: {DETECTOR.can_activate('github.pr.merge')}")
