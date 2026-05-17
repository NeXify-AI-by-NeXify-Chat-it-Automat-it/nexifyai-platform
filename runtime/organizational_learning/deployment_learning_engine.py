#!/usr/bin/env python3
"""deployment_learning_engine.py -- Learns from deployment outcomes."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus
log=logging.getLogger("deploy-learn")

class DeploymentLearningEngine:
    def __init__(self):
        self._outcomes=[];self.bus=get_bus()
    def start(self):
        self.bus.subscribe("deployment.result",self._learn,"deplearn:result")
        log.info("Deployment learning engine active")
    def _learn(self,e):
        self._outcomes.append({"id":str(uuid.uuid4())[:8],"event":e,"ts":datetime.now(timezone.utc).isoformat()})
    def stats(self):return {"deployments_learned":len(self._outcomes)}
    def get_recent(self,limit=20):return list(self._outcomes[-limit:])

DEPLOY_LEARN=DeploymentLearningEngine()
def start():DEPLOY_LEARN.start();return DEPLOY_LEARN
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print(json.dumps(DEPLOY_LEARN.stats()))
