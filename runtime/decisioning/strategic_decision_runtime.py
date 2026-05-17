#!/usr/bin/env python3
"""strategic_decision_runtime.py"""
import json,logging
log=logging.getLogger("strategic-decision")
STRATEGIC={"business_critical":{"weight":5,"timeout":30},"operational":{"weight":3,"timeout":60},"optimization":{"weight":1,"timeout":300}}
class StrategicDecisionRuntime:
    def classify(self,decision):
        for cls,meta in STRATEGIC.items():
            if any(kw in str(decision).lower() for kw in cls.split("_")):
                return {"classification":cls,"weight":meta["weight"],"timeout":meta["timeout"]}
        return {"classification":"default","weight":2,"timeout":120}
STRAT_DEC=StrategicDecisionRuntime()
