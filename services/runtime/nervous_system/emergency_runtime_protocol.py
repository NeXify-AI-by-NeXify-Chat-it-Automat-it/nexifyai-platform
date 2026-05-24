#!/usr/bin/env python3
"""emergency_runtime_protocol.py -- Emergency protocols for critical situations."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus,publish
log=logging.getLogger("emergency")

EMERGENCY_LEVELS={
    "critical": {"action":"halt_autonomy","notify":"all_teams","recovery":"forced","ts":""},
    "high": {"action":"pause_current_workflow","notify":"governance","recovery":"automated","ts":""},
    "medium": {"action":"quarantine_affected_capability","notify":"security","recovery":"scheduled","ts":""},
}

class EmergencyRuntimeProtocol:
    def __init__(self):
        self._active=False;self._history=[];self.bus=get_bus()
    def start(self):
        self.bus.subscribe("system.error",self._check_emergency,"emergency:error")
        self.bus.subscribe("incident.detected",self._check_emergency,"emergency:incident")
        log.info("Emergency runtime protocol active")
    def trigger(self,level,reason):
        proto=EMERGENCY_LEVELS.get(level,EMERGENCY_LEVELS["medium"])
        proto["ts"]=datetime.now(timezone.utc).isoformat()
        entry={"id":str(uuid.uuid4())[:8],"level":level,"reason":reason,"protocol":proto}
        self._history.append(entry)
        if level=="critical":
            self._active=True
            publish("emergency.active",{"reason":reason,"protocol":proto},"emergency")
            log.critical(f"EMERGENCY: {reason}")
        publish("planner.cycle",{"type":"emergency","level":level},"emergency")
        return entry
    def _check_emergency(self,e):
        payload=e.get("payload",{});cap=payload.get("cap","");err=payload.get("error","")
        if "critical" in str(err).lower() or "gateway" in cap:
            self.trigger("high",f"Error in {cap}: {err}")
    def history(self):return list(self._history)
    def is_active(self):return self._active
    def resolve(self):
        self._active=False;publish("emergency.resolved",{"ts":datetime.now(timezone.utc).isoformat()},"emergency")

EMERGENCY=EmergencyRuntimeProtocol()
def start():EMERGENCY.start();return EMERGENCY
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print(json.dumps(EMERGENCY.trigger("critical","Test")))
