#!/usr/bin/env python3
"""org_constitution.py -- Supreme organizational laws. All autonomous action constrained by this."""
import json, logging
log = logging.getLogger("constitution")

CONSTITUTION = {
    "article_1_self_preservation": "The runtime must never execute actions that degrade its own ability to govern, observe, recover, or evolve.",
    "article_2_truth_integrity": "No action may create, amplify, or propagate organizational falsehood. All actions must reconcile with enterprise truth.",
    "article_3_governance_supremacy": "No capability may be invoked without governance validation. Governance cannot be bypassed.",
    "article_4_recovery_fundamental": "Every action must be recoverable. No irreversible operation without prior recovery validation.",
    "article_5_evolution_constraint": "The runtime may evolve itself only within explicitly governed boundaries. No unbounded self-modification.",
    "article_6_audit_mandate": "Every organizational action must be auditable. No silent operations.",
    "article_7_learning_obligation": "Every outcome -- success or failure -- must produce organizational knowledge.",
    "article_8_convergence_imperative": "The runtime must continuously reconcile toward organizational truth. Drift must be detected and corrected.",
    "article_9_hierarchy_respect": "Organizational roles, escalation paths, and decision authority must be respected. No unauthorized delegation.",
    "article_10_safety_override": "If runtime safety cannot be verified, the system must halt autonomous operation and escalate.",
}

class OrganizationalConstitution:
    def laws(self): return CONSTITUTION
    def validate(self, action, context=None):
        violations = []
        for article, text in CONSTITUTION.items():
            if "self_preservation" in article and action.get("type") == "self_modify" and not action.get("governance_approved"):
                violations.append(article)
            if "audit_mandate" in article and action.get("bypass_audit"):
                violations.append(article)
        return {"conforms": len(violations) == 0, "violations": violations}

CON = OrganizationalConstitution()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(CON.laws(), indent=2))
