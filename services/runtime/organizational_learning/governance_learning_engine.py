#!/usr/bin/env python3
"""gov_learning_engine.py -- Learns from governance outcomes."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus
log=logging.getLogger("gov-learn")

class GovernanceLearningEngine:
    def __init__(self):
        self._violations=[];self._passes=[];self.bus=get_bus()
    def start(self):
        self.bus.subscribe("governance.pass",self._pass,"govlearn:pass")
        self.bus.subscribe("governance.fail",self._fail,"govlearn:fail")
        log.info("Governance learning engine active")
    def _pass(self,e):self._passes.append({"event":e,"ts":datetime.now(timezone.utc).isoformat()})
    def _fail(self,e):self._violations.append({"event":e,"ts":datetime.now(timezone.utc).isoformat()})
    def stats(self):return {"passes":len(self._passes),"violations":len(self._violations)}

GOV_LEARN=GovernanceLearningEngine()
def start():GOV_LEARN.start();return GOV_LEARN
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print(json.dumps(GOV_LEARN.stats()))
