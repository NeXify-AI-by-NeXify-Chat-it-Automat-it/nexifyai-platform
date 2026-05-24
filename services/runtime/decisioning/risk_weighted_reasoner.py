#!/usr/bin/env python3
"""risk_weighted_reasoner.py"""
import json,logging
log=logging.getLogger("risk-weight")
class RiskWeightedReasoner:
    def assess(self,opts):
        for o in opts:
            o["risk_adj_score"]=round(o.get("benefit",0.5)*(1-o.get("risk",0.5))*5,2)
        return sorted(opts,key=lambda x:-x["risk_adj_score"])
REASONER=RiskWeightedReasoner()
