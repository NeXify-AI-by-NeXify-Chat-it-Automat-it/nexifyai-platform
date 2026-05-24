#!/usr/bin/env python3
"""constitutional_validation_engine.py -- Validates all autonomous actions against constitution."""
import json, logging
from organizational_constitution import CON
from governance_law_engine import GOV_LAW
from strategic_boundary_engine import BOUNDARY
from autonomous_action_constraints import CONSTRAINTS_ENG
from runtime_safety_charter import SAFETY
log = logging.getLogger("const-validation")

class ConstitutionalValidationEngine:
    def validate(self, action):
        results = []
        c = CON.validate(action)
        results.append({"layer": "constitution", "pass": c["conforms"], "detail": c["violations"] if not c["conforms"] else "ok"})
        law = GOV_LAW.get_law(action.get("type",""))
        if law["enforcement"] == "blocking" and not action.get("governance_approved"):
            results.append({"layer": "governance_law", "pass": False, "detail": f"Blocked by {law['rule']}"})
        else:
            results.append({"layer": "governance_law", "pass": True})
        for key in BOUNDARY.boundaries():
            if key in action:
                b = BOUNDARY.check(key, action[key])
                if not b.get("within", True):
                    results.append({"layer": "boundary", "pass": False, "detail": f"{key}: {b.get('current')} exceeds {b.get('boundary')}"})
        con = CONSTRAINTS_ENG.check(action)
        if con.get("blocked"):
            results.append({"layer": "constraints", "pass": False, "detail": con["reason"]})
        SAFETY.check(action)
        results.append({"layer": "safety", "pass": True})
        overall = all(r.get("pass", False) for r in results)
        return {"allowed": overall, "checks": results}

VALIDATOR = ConstitutionalValidationEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(VALIDATOR.validate({"type":"self_modify"}), indent=2))
