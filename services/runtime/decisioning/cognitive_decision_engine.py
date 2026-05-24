#!/usr/bin/env python3
"""cognitive_decision_engine.py -- Central decision engine."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus,publish
log=logging.getLogger("decision-engine")
class CognitiveDecisionEngine:
    def __init__(self):
        self._decisions=[];self._lock=__import__("threading").Lock();self.bus=get_bus()
    def start(self):
        self.bus.subscribe("planner.cycle",self._on_cycle,"decision:cycle");log.info("Decision engine active")
    def decide(self,options,context=None):
        if not options: return {"decision":None,"reason":"no_options"}
        scored=[]
        for o in options:
            score=o.get("priority",3)*1.0+o.get("confidence",0.5)*2-o.get("risk",0)*3
            scored.append({"option":o,"score":round(score,2)})
        scored.sort(key=lambda x:-x["score"])
        decision={"id":str(uuid.uuid4())[:8],"selected":scored[0]["option"],"ts":datetime.now(timezone.utc).isoformat()}
        with self._lock:self._decisions.append(decision)
        publish("decision.made",{"id":decision["id"]},"decision-engine")
        return decision
    def _on_cycle(self,e):pass
    def history(self):return list(self._decisions[-20:])
DECISION=CognitiveDecisionEngine()
def start():DECISION.start();return DECISION
