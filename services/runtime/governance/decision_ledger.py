#!/usr/bin/env python3
"""decision_ledger.py — Persistent organizational decision ledger.
All autonomous decisions recorded here for audit and learning.
Stores to: /brain/decisions/ (files) + Qdrant (vectors)
"""
import json, logging, os, uuid as uid
from datetime import datetime, timezone

DECISIONS_ROOT = "/brain/decisions"
log = logging.getLogger("decision-ledger")

class DecisionLedger:
    def __init__(self):
        os.makedirs(f"{DECISIONS_ROOT}/architectural_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/governance_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/runtime_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/deployment_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/security_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/recovery_decisions", exist_ok=True)
        os.makedirs(f"{DECISIONS_ROOT}/operational_patterns", exist_ok=True)
    
    def record(self, category: str, entry: dict, subcategory: str = None) -> str:
        decision_id = str(uid.uuid4())[:12]
        entry["decision_id"] = decision_id
        entry["recorded_at"] = datetime.now(timezone.utc).isoformat()
        
        # File storage
        cat_map = {
            "architectural": "architectural_decisions",
            "governance": "governance_decisions",
            "runtime": "runtime_decisions",
            "deployment": "deployment_decisions",
            "security": "security_decisions",
            "recovery": "recovery_decisions",
            "pattern": "operational_patterns",
        }
        subdir = cat_map.get(category, "runtime_decisions")
        if subcategory:
            subdir = f"{subdir}/{subcategory}"
            os.makedirs(f"{DECISIONS_ROOT}/{subdir}", exist_ok=True)
        
        fpath = f"{DECISIONS_ROOT}/{subdir}/{decision_id}.json"
        with open(fpath, "w") as f:
            json.dump(entry, f, indent=2, default=str)
        
        # Qdrant storage
        try:
            import requests
            payload = {"category": f"decision_{category}", "type": "decision", **entry}
            requests.put(
                "http://localhost:6333/collections/nexifyai_brain/points",
                json={"points": [{"id": str(uid.uuid4()), "vector": [0.0]*384, "payload": payload}]},
                timeout=5
            )
        except Exception as e:
            log.warning(f"Qdrant write failed: {e}")
        
        return decision_id
    
    def get(self, decision_id: str) -> dict:
        for root, dirs, files in os.walk(DECISIONS_ROOT):
            for f in files:
                if f == f"{decision_id}.json":
                    with open(os.path.join(root, f)) as fh:
                        return json.load(fh)
        return {"error": "not found"}
    
    def list_recent(self, category: str = None, limit: int = 20) -> list:
        results = []
        cat_map = {
            "architectural": "architectural_decisions",
            "governance": "governance_decisions",
            "runtime": "runtime_decisions",
            "deployment": "deployment_decisions",
            "security": "security_decisions",
            "recovery": "recovery_decisions",
            "pattern": "operational_patterns",
        }
        base = cat_map.get(category) if category else ""
        search_root = f"{DECISIONS_ROOT}/{base}" if base else DECISIONS_ROOT
        
        for root, dirs, files in os.walk(search_root):
            for f in sorted(files, reverse=True)[:limit]:
                if f.endswith('.json'):
                    with open(os.path.join(root, f)) as fh:
                        results.append(json.load(fh))
        return sorted(results, key=lambda x: x.get("recorded_at", ""), reverse=True)[:limit]

LEDGER = DecisionLedger()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    did = LEDGER.record("architectural", {"title": "Autonomy Transition", "decision": "Move to FULL_AUTONOMOUS_ENTERPRISE"})
    print(f"Recorded: {did}")
    print(json.dumps(LEDGER.get(did), indent=2))