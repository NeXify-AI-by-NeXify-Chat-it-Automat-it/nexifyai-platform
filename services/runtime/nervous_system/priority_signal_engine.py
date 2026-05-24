#!/usr/bin/env python3
"""priority_signal_engine.py -- Assigns priority to events."""
import json,logging
log=logging.getLogger("prio-signal")

PRIORITY_RULES={
    "critical_incident": {"priority":1,"action":"immediate","notify":"all"},
    "governance_violation": {"priority":2,"action":"block_and_report","notify":"governance"},
    "drift_detected": {"priority":3,"action":"reconcile","notify":"reconciliation"},
    "routine": {"priority":4,"action":"log","notify":"none"},
}

class PrioritySignalEngine:
    def classify(self,signal):
        for rule,meta in PRIORITY_RULES.items():
            if any(kw in str(signal).lower() for kw in rule.split("_")):
                return {"priority":meta["priority"],"action":meta["action"],"notify":meta["notify"],"label":rule}
        return {"priority":99,"action":"log","notify":"none","label":"unknown"}

PRIO_SIG=PrioritySignalEngine()
if __name__=="__main__":print(json.dumps(PRIO_SIG.classify("critical incident detected")))
