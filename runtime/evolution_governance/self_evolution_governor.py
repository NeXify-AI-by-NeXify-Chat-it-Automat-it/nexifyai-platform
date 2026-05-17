#!/usr/bin/env python3
"""self_evolution_governor.py -- Controls autonomous evolution within boundaries."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus,publish
log=logging.getLogger("evolution-gov")
class SelfEvolutionGovernor:
    def __init__(self):
        self._log=[];self._max=5;self._locked=False;self.bus=get_bus()
    def start(self):
        self.bus.subscribe("planner.cycle",self._on_cycle,"evolgov:cycle");log.info("Evolution governor active")
    def approve(self,req):
        if self._locked: return {"approved":False,"reason":"locked"}
        if len(self._log)>=self._max: return {"approved":False,"reason":f"max {self._max}/day"}
        e={"id":str(uuid.uuid4())[:8],"req":req,"ts":datetime.now(timezone.utc).isoformat()}
        self._log.append(e);publish("evolution.approved",e,"evolution-gov");return {"approved":True,"id":e["id"]}
    def _on_cycle(self,e):
        if e.get("payload",{}).get("type")=="evolution_proposal":self.approve(e["payload"])
    def lock(self): self._locked=True;publish("evolution.locked",{},"evolution-gov")
    def stats(self): return {"approved":len(self._log),"max":self._max,"locked":self._locked}
GOV=SelfEvolutionGovernor()
def start():GOV.start();return GOV
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);print(json.dumps(GOV.approve({"type":"add_capability"})))
