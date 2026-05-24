#!/usr/bin/env python3
"""policy_evaluator.py — Evaluates actions against runtime policies."""
import json, logging, os, sys
sys.path.insert(0, "/services/runtime/governance")
from decision_ledger import LEDGER
log = logging.getLogger("policy-eval")

class PolicyEvaluator:
    def __init__(self):
        self.policies = self._load()
    def _load(self):
        import yaml
        p = "/services/runtime/governance/autonomy_policy.yaml"
        if os.path.exists(p):
            with open(p) as f: return yaml.safe_load(f) or {}
        return {}
    def evaluate(self, action: dict) -> dict:
        atype = action.get("type", "unknown")
        never_ask = ["code_refactor","dependency_update","lint_fix","type_fix",
                     "test_fix","ci_repair","workflow_repair","runtime_hardening",
                     "secret_rotation","recovery_execution","governance_update",
                     "frontend_alignment","deployment_validation"]
        human = ["destructive","legal","payment","data_loss","security_compromise"]
        if any(p in atype for p in never_ask):
            return {"pass":True,"mode":"autonomous","reason":f"{atype} auto-approved"}
        if any(p in atype for p in human):
            return {"pass":False,"mode":"human_required","reason":f"{atype} requires human"}
        risk = action.get("risk_score", 0)
        return {"pass":True,"mode":"autonomous" if risk <= 7 else "notify","reason":f"risk={risk}"}
    def record_evaluation(self, action: dict, result: dict):
        LEDGER.record("governance", {"title":f"Policy: {action.get('type','unknown')}","action":action,"result":result})

EVALUATOR = PolicyEvaluator()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = EVALUATOR.evaluate({"type":"code_refactor","domain":"frontend"})
    print(json.dumps(r, indent=2))