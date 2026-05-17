#!/usr/bin/env python3
"""enterprise_awareness_runtime.py -- Global enterprise situational awareness."""
import json,logging,uuid
from datetime import datetime,timezone
from event_bus import get_bus,publish
log=logging.getLogger("awareness")

class EnterpriseAwarenessRuntime:
    def __init__(self):
        self._state={"mode":"autonomous","health":"normal","last_scan":None};self.bus=get_bus()
    def start(self):
        log.info("Enterprise awareness runtime active")
    def scan(self):
        svcs=__import__("subprocess").run("systemctl list-units --type=service --state=running | grep -c nexify",shell=True,capture_output=True,text=True,timeout=5)
        timers=__import__("subprocess").run("systemctl list-timers --no-pager | grep -c nexify",shell=True,capture_output=True,text=True,timeout=5)
        brain=0
        try:brain=requests.get("http://localhost:6333/collections/nexifyai_brain",timeout=5).json().get("result",{}).get("points_count",0)
        except:pass
        self._state["services"]=int(svcs.stdout.strip());self._state["timers"]=int(timers.stdout.strip());self._state["brain_vectors"]=brain
        self._state["last_scan"]=datetime.now(timezone.utc).isoformat()
        health="normal"
        if self._state.get("services",0)<10:health="degraded"
        if self._state.get("timers",0)<10:health="warning"
        self._state["health"]=health
        publish("awareness.update",dict(self._state),"awareness")
        return dict(self._state)
    def status(self):return dict(self._state)
    def mode(self,m=None):
        if m:self._state["mode"]=m
        return self._state["mode"]

AWARENESS=EnterpriseAwarenessRuntime()
def start():AWARENESS.start();return AWARENESS
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print(json.dumps(AWARENESS.status()))
