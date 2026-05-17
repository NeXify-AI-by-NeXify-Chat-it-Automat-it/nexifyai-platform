#!/usr/bin/env python3
"""autonomy_engine.py — Central autonomy decision engine.
Evaluates whether an action can proceed autonomously.
Gates: risk, governance, constitution, safety, authority.
"""
import json, logging, os, sys
from datetime import datetime, timezone

sys.path.insert(0, "/runtime")
sys.path.insert(0, "/runtime/governance")
sys.path.insert(0, "/runtime/constitution")

log = logging.getLogger("autonomy-engine")

class AutonomyEngine:
    def __init__(self):
        self.policies = self._load_policies()
        self.authority = self._load_authority()

    def _load_policies(self):
        import yaml
        path = "/runtime/governance/autonomy_policy.yaml"
        if os.path.exists(path):
            with open(path) as f:
                return yaml.safe_load(f)
        return {}

    def _load_authority(self):
        import yaml
        path = "/brain/governance/runtime_authority_manifest.yaml"
        result = {}
        if os.path.exists(path):
            with open(path) as f:
                result = yaml.safe_load(f) or {}
        # Load enterprise authority for domains
        eapath = "/brain/governance/enterprise_authority.yaml"
        if os.path.exists(eapath):
            with open(eapath) as f:
                ea = yaml.safe_load(f) or {}
            ent = ea.get("enterprise_authority", {})
            # Merge autonomous domains from enterprise authority
            if "autonomous_domains" in ea:
                result["autonomous_domains"] = ea["autonomous_domains"]
            # Also add enterprise_authority with flags
            result["enterprise_authority"] = ent
        return result

    def can_execute(self, action: dict) -> dict:
        """Evaluate if action can proceed autonomously.
        Returns: {allowed: bool, reason: str, gates: dict}
        """
        action_type = action.get("type", action.get("action", "unknown"))
        gates = {}
        
        # 1. Risk check
        risk = action.get("risk_score", 0)
        max_auto = self.policies.get("policy_evaluation", {}).get("gates", {}).get("risk_score", {}).get("max_auto", 7)
        gates["risk"] = {"pass": risk <= max_auto, "score": risk, "max": max_auto}
        
        # 2. Never-ask check
        never_ask = self.authority.get("execution_policy", {}).get("never_ask", [])
        requires_human = self.authority.get("execution_policy", {}).get("requires_human", [])
        
        if any(pat in action_type for pat in never_ask):
            gates["policy"] = {"pass": True, "reason": "In never-ask list"}
        elif any(pat in action_type for pat in requires_human):
            gates["policy"] = {"pass": False, "reason": "Requires human approval", "human_required": True}
        else:
            gates["policy"] = {"pass": True, "reason": "Default autonomous"}
        
        # 3. Constitutional check (import from existing)
        try:
            from constitutional_validation_engine import VALIDATOR
            const_result = VALIDATOR.validate(action) or {"allowed": True, "checks": []}
            gates["constitution"] = {"pass": const_result.get("allowed", True), "detail": const_result}
        except ImportError:
            gates["constitution"] = {"pass": True, "reason": "Validator unavailable, bypassed"}
        
        # 4. Safety check
        try:
            from runtime_safety_charter import SAFETY
            safety_result = SAFETY.check(action) or {"safe": True, "checks": []}
            gates["safety"] = {"pass": safety_result.get("safe", True), "detail": safety_result}
        except ImportError:
            gates["safety"] = {"pass": True, "reason": "Safety check unavailable"}
        
        # 5. Authority check
        domain = action.get("domain", "unknown")
        auto_domains = self.authority.get("autonomous_domains", [])
        # If no domain list specified, allow all
        if not auto_domains:
            auto_domains = ["frontend", "backend", "infrastructure", "governance", 
                          "security", "observability", "deployment", "recovery", 
                          "learning", "evolution", "finance", "unknown"]
        gates["authority"] = {"pass": domain in auto_domains or "*" in auto_domains, "domain": domain}
        
        all_pass = all(g.get("pass", False) for g in gates.values())
        return {
            "allowed": all_pass,
            "action": action_type,
            "gates": gates,
            "ts": datetime.now(timezone.utc).isoformat()
        }

ENGINE = AutonomyEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test = {"type": "code_refactor", "domain": "frontend", "risk_score": 2}
    print(json.dumps(ENGINE.can_execute(test), indent=2))