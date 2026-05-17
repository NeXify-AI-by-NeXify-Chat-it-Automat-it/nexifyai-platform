#!/usr/bin/env python3
"""capability_security_matrix.py -- Security classification of all MCP capabilities."""
import json, logging
log = logging.getLogger("cap-security")

MATRIX = {
    "critical": {"level":4,"requires":["approval","audit","recovery"]},
    "high": {"level":3,"requires":["audit","recovery"]},
    "medium": {"level":2,"requires":["audit"]},
    "low": {"level":1,"requires":[]},
}

CLASSIFICATION = {
    "deployment.rollback": "critical",
    "deployment.run": "high",
    "github.pr.create": "high",
    "github.pr.merge": "critical",
    "github.issue.create": "medium",
    "brain.store": "medium",
    "brain.query": "low",
    "monitor.health": "low",
    "runtime.shell": "critical",
    "infra.restart": "critical",
}

class CapabilitySecurityMatrix:
    def classify(self, cap_id):
        cl = CLASSIFICATION.get(cap_id, "low")
        return {"cap": cap_id, "classification": cl, **MATRIX.get(cl, {})}
    def requires(self, cap_id, requirement):
        cl = CLASSIFICATION.get(cap_id, "low")
        return requirement in MATRIX.get(cl, {}).get("requires", [])
    def get_all_classified(self):
        return {k: self.classify(k) for k in CLASSIFICATION}

MATRIX_ENGINE = CapabilitySecurityMatrix()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(MATRIX_ENGINE.classify("deployment.rollback"), indent=2))
