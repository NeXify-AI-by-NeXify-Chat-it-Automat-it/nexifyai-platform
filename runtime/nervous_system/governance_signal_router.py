#!/usr/bin/env python3
"""gov_signal_router.py -- Routes signals through governance layer."""
import json,logging
from event_bus import get_bus,publish
log=logging.getLogger("gov-sig")

class GovernanceSignalRouter:
    def __init__(self):self.bus=get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke",self._route,"govsig:invoke")
        log.info("Governance signal router active")
    def _route(self,e):
        cap=e.get("payload",{}).get("cap","")
        if cap.startswith("deployment.") or cap.startswith("infra.") or cap.startswith("security."):
            publish("governance.check",{"cap":cap,"source":"signal_router"},"govsig-router")

GOV_SIG=GovernanceSignalRouter()
def start():GOV_SIG.start();return GOV_SIG
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print("Active")
