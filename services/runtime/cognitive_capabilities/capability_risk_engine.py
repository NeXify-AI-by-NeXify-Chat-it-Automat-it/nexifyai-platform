#!/usr/bin/env python3
"""capability_risk_engine.py — Assesses risk of invoking a capability based on context."""
import json, logging
log = logging.getLogger("cap-risk")

RISK_PROFILES = {
    "critical": {"impact": "system_wide", "recovery_time": "high", "blast_radius": "enterprise"},
    "high": {"impact": "system_wide", "recovery_time": "medium", "blast_radius": "domain"},
    "medium": {"impact": "local", "recovery_time": "low", "blast_radius": "system"},
    "low": {"impact": "none", "recovery_time": "none", "blast_radius": "none"},
}
CAP_RISK = {
    "infra.service.restart": "critical", "deployment.rollback": "critical", "runtime.shell": "critical",
    "github.pr.merge": "high", "github.pr.create": "high", "deployment.run": "high",
    "github.issue.create": "medium", "brain.store": "medium", "infra.process.list": "medium",
    "brain.query": "low", "monitor.health": "low", "infra.disk.usage": "low",
}

class CapabilityRiskEngine:
    def assess(self, cap_id):
        level = CAP_RISK.get(cap_id, "low")
        return {"cap": cap_id, "risk_level": level, **RISK_PROFILES.get(level, {})}

RISK = CapabilityRiskEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(RISK.assess("infra.service.restart"), indent=2))
