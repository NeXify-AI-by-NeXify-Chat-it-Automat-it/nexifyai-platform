#!/usr/bin/env python3
"""execution_authority.py — Grants or denies execution authority.
Consults: autonomy engine, authority manifest, decision ledger.
"""
import json, logging, os, sys, uuid
from datetime import datetime, timezone

sys.path.insert(0, "/runtime/governance")
log = logging.getLogger("exec-auth")

class DecisionLedger:
    """Persist decisions to Qdrant for audit trail."""
    def __init__(self):
        self._local = []
    
    def record(self, category: str, entry: dict):
        self._local.append(entry)
        # Try Qdrant
        try:
            import requests
            import uuid as uid
            payload = {"category": f"decision_{category}", **entry}
            requests.put(
                "http://localhost:6333/collections/nexifyai_brain/points",
                json={"points": [{"id": str(uid.uuid4()), "vector": [0.0]*384, "payload": payload}]},
                timeout=5
            )
        except Exception as e:
            log.warning(f"Qdrant write failed: {e}")
    
    def recent(self, category: str = None, limit: int = 10) -> list:
        if category:
            return [e for e in self._local if e.get("status") == category][-limit:]
        return self._local[-limit:]



class ExecutionAuthority:
    def __init__(self):
        self.ledger = DecisionLedger()

    def authorize(self, action: dict, context: dict = None) -> dict:
        from autonomy_engine import ENGINE
        result = ENGINE.can_execute(action)
        
        if result["allowed"]:
            # Issue execution token
            token = str(uuid.uuid4())[:12]
            entry = {
                "token": token,
                "action": action,
                "context": context or {},
                "decision": result,
                "ts": datetime.now(timezone.utc).isoformat(),
                "status": "authorized"
            }
            self.ledger.record("execution", entry)
            return {"authorized": True, "token": token, "gates": result["gates"]}
        else:
            entry = {
                "action": action,
                "decision": result,
                "ts": datetime.now(timezone.utc).isoformat(),
                "status": "denied"
            }
            self.ledger.record("denial", entry)
            return {"authorized": False, "reason": result.get("gates", {}), "human_required": any(
                g.get("human_required") for g in result.get("gates", {}).values()
            )}

AUTHORITY = ExecutionAuthority()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    auth = ExecutionAuthority()
    r = auth.authorize({"type": "code_refactor", "domain": "frontend", "risk_score": 2})
    print(json.dumps(r, indent=2, default=str))