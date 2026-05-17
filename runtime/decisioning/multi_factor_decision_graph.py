#!/usr/bin/env python3
"""multi_factor_decision_graph.py"""
import json,logging
log=logging.getLogger("mfd-graph")
class MultiFactorDecisionGraph:
    def score(self,decision,criteria):
        total=0
        for c in criteria:
            weight=c.get("weight",1);val=c.get("value",decision.get(c.get("key",""),0));total+=weight*val
        return {"score":total,"factors":len(criteria)}
MFD=MultiFactorDecisionGraph()
