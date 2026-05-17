#!/usr/bin/env python3
"""incident_learning_engine.py -- Extracts lessons from incidents."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus
log=logging.getLogger("incident-learn")

class IncidentLearningEngine:
    def __init__(self):
        self._patterns=[];self.bus=get_bus()
    def start(self):
        self.bus.subscribe("incident.detected",self._learn,"inclearn:detect")
        self.bus.subscribe("incident.resolved",self._learn,"inclearn:resolve")
        log.info("Incident learning engine active")
    def _learn(self,e):
        pattern={"id":str(uuid.uuid4())[:8],"source":"incident","event":e,"ts":datetime.now(timezone.utc).isoformat()}
        self._patterns.append(pattern)
    def get_patterns(self):return list(self._patterns[-50:])
    def stats(self):return {"learned":len(self._patterns)}

INCIDENT_LEARN=IncidentLearningEngine()
def start():INCIDENT_LEARN.start();return INCIDENT_LEARN
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print(json.dumps(INCIDENT_LEARN.stats()))
