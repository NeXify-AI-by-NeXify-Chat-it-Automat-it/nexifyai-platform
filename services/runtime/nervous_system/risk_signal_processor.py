#!/usr/bin/env python3
"""risk_signal_processor.py -- Assesses risk of incoming signals."""
import json,logging
log=logging.getLogger("risk-sig")

class RiskSignalProcessor:
    def assess(self,signal):
        risk=0
        if signal.get("type")=="system_error":risk+=3
        if signal.get("severity")=="critical":risk+=2
        if signal.get("domain")=="infrastructure":risk+=1.5
        if signal.get("repeated",0)>3:risk+=1
        return {"risk_score":min(10,risk),"level":"high" if risk>5 else "medium" if risk>2 else "low","signal":signal.get("type","unknown")}

RISK_PROC=RiskSignalProcessor()
if __name__=="__main__":print(json.dumps(RISK_PROC.assess({"type":"system_error","severity":"critical","domain":"infrastructure"})))
