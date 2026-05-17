#!/usr/bin/env python3
"""escalation_engine.py — Routes blocked/risky actions to escalation paths."""
import json, logging, os, sys
from datetime import datetime, timezone
sys.path.insert(0, "/runtime/governance")
from decision_ledger import LEDGER
log = logging.getLogger("escalation")

ESCALATION_PATHS = {
    "security_compromise": {"target":"security_engine","priority":"critical","block":True},
    "legal_risk": {"target":"governance_engine","priority":"critical","block":True},
    "data_loss": {"target":"recovery_engine","priority":"critical","block":True},
    "payment": {"target":"executive","priority":"high","block":True},
    "destructive": {"target":"recovery_engine","priority":"high","block":True},
}

class EscalationEngine:
    def escalate(self, action: dict, reason: str) -> dict:
        atype = action.get("type","unknown")
        path = ESCALATION_PATHS.get(atype, {"target":"runtime","priority":"low","block":False})
        entry = {"action":action,"reason":reason,"path":path,
                 "ts":datetime.now(timezone.utc).isoformat(),"status":"escalated"}
        LEDGER.record("governance", {"title":f"Escalation: {atype}",**entry})
        try:
            sys.path.insert(0, "/runtime/events")
            from event_bus import get_bus
            get_bus().publish("governance.escalation", entry, "escalation-engine")
        except: log.warning("Event bus unavailable")
        return {"escalated":True,"path":path,"block":path["block"],"entry":entry}
    def notify_human(self, action: dict, reason: str):
        LEDGER.record("governance", {"title":f"Human notify: {action.get('type','unknown')}",
                     "action":action,"reason":reason,
                     "notified_at":datetime.now(timezone.utc).isoformat()})

ESCALATOR = EscalationEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = ESCALATOR.escalate({"type":"security_compromise"},"Credential leak detected")
    print(json.dumps(r, indent=2, default=str))