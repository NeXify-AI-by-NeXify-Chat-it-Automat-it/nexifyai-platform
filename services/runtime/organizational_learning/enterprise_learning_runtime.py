#!/usr/bin/env python3
"""enterprise_learning_runtime.py -- Central learning runtime."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus,publish
log=logging.getLogger("ent-learn")

class EnterpriseLearningRuntime:
    def __init__(self):
        self._lessons=[];self.bus=get_bus()
    def start(self):
        self.bus.subscribe("incident.resolved",self._from_incident,"learn:incident")
        self.bus.subscribe("deployment.result",self._from_deploy,"learn:deploy")
        log.info("Enterprise learning runtime active")
    def record(self,category,observation):
        l={"id":str(uuid.uuid4())[:8],"category":category,"observation":observation,"ts":datetime.now(timezone.utc).isoformat()}
        self._lessons.append(l)
        publish("learning.recorded",{"id":l["id"],"category":category},"ent-learn")
        return l
    def _from_incident(self,e):self.record("incident",e.get("payload",{}))
    def _from_deploy(self,e):self.record("deployment",e.get("payload",{}))
    def get_lessons(self,category=None):
        if category:return [l for l in self._lessons if l["category"]==category]
        return list(self._lessons)

LEARN_RT=EnterpriseLearningRuntime()
def start():LEARN_RT.start();return LEARN_RT
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start()
    print(json.dumps(LEARN_RT.record("incident",{"msg":"test lesson"})))
