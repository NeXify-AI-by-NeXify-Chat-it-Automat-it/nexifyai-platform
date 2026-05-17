#!/usr/bin/env python3
"""control_plane.py — Central Runtime Controller."""
import json, logging, os, sys, yaml
from datetime import datetime, timezone
log = logging.getLogger("control-plane")
class ControlPlane:
    def __init__(self, config_path="/runtime/control_plane/autonomy_objectives.yaml"):
        self.config_path = config_path
        self.objectives = self._load_objectives()
        self.ledger = []
    def _load_objectives(self):
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    def evaluate(self, task: dict) -> dict:
        verdict = {"task": task.get("id", "unknown"), "status": "pending", "gates": []}
        policy = self._check_policy(task)
        verdict["gates"].append({"gate": "policy", "status": "pass" if policy else "block"})
        if not policy:
            verdict["status"] = "blocked"; verdict["reason"] = "policy_violation"
            return verdict
        const = self._check_constitutional(task)
        verdict["gates"].append({"gate": "constitution", "status": "pass" if const else "block"})
        if not const:
            verdict["status"] = "blocked"; verdict["reason"] = "constitutional_violation"
            return verdict
        auth = self._check_autonomy(task)
        verdict["gates"].append({"gate": "autonomy", "status": auth["status"]})
        if auth["status"] == "escalate":
            verdict["status"] = "escalated"; verdict["reason"] = auth["reason"]
            return verdict
        aligned = self._check_alignment(task)
        verdict["gates"].append({"gate": "alignment", "status": "pass" if aligned else "warn"})
        verdict["status"] = "approved"
        verdict["authority_token"] = f"AT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{hash(str(task)) % 10000:04d}"
        self._record(verdict)
        return verdict
    def _check_policy(self, task):
        never = self.objectives.get("constraints", {}).get("never", [])
        task_text = json.dumps(task).lower()
        for forbidden in never:
            if forbidden.replace("_", " ") in task_text:
                return False
        return True
    def _check_constitutional(self, task):
        action = task.get("action", "")
        el = self.objectives.get("constraints", {}).get("require_escalation", [])
        return action not in el
    def _check_autonomy(self, task):
        action = task.get("action", "")
        vl = self.objectives.get("constraints", {}).get("require_verification", [])
        if action in vl:
            return {"status": "escalate", "reason": f"requires_verification: {action}"}
        return {"status": "autonomous"}
    def _check_alignment(self, task):
        oids = [o["id"] for o in self.objectives.get("objectives", [])]
        to = task.get("objective", "")
        return to in oids or not to
    def _record(self, verdict):
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "verdict": verdict}
        self.ledger.append(entry)
        lp = "/runtime/control_plane/state/decision_ledger.jsonl"
        with open(lp, "a") as f:
            f.write(json.dumps(entry) + "\n")
if __name__ == "__main__":
    cp = ControlPlane()
    if len(sys.argv) > 1:
        task = json.loads(sys.argv[1])
        print(json.dumps(cp.evaluate(task), indent=2))
    else:
        print("Usage: control_plane.py '<json_task>'")
