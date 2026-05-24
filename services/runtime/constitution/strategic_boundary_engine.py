#!/usr/bin/env python3
"""strategic_boundary_engine.py -- Defines strategic operational boundaries autonomous actions cannot cross."""
import json, logging
log = logging.getLogger("strategy-boundary")

BOUNDARIES = {
    "max_autonomous_prs_per_hour": 5,
    "max_services_restarted_in_window": 3,
    "max_capabilities_added_per_day": 10,
    "blocked_domains_for_autonomous_action": ["production_secrets", "infrastructure_base"],
    "require_human_approval_after_failures": 3,
}

class StrategicBoundaryEngine:
    def check(self, action_type, value):
        bound = BOUNDARIES.get(action_type)
        if bound is None: return {"within": True, "boundary": None}
        if isinstance(bound, (int, float)):
            return {"within": value <= bound, "boundary": bound, "current": value, "excess": max(0, value - bound)}
        if isinstance(bound, list):
            return {"within": value not in bound, "boundary": bound, "current": value}
        return {"within": True}
    def boundaries(self): return BOUNDARIES

BOUNDARY = StrategicBoundaryEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(BOUNDARY.check("max_autonomous_prs_per_hour", 6)))
