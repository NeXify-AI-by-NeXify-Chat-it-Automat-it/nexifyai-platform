#!/usr/bin/env python3
"""org_tradeoff_engine.py"""
import json,logging
log=logging.getLogger("tradeoff")
class TradeoffEngine:
    def analyze(self,a,b):
        w={"stability":2,"speed":1,"safety":3,"cost":-1}
        a_s=sum(a.get(k,0)*v for k,v in w.items())
        b_s=sum(b.get(k,0)*v for k,v in w.items())
        return {"a_score":a_s,"b_score":b_s,"rec":"a" if a_s>b_s else "b","delta":round(abs(a_s-b_s),2)}
TRADEOFF=TradeoffEngine()
