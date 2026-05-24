#!/usr/bin/env python3
"""org_signal_router.py -- Routes signals to the right organizational subsystem."""
import json,logging
from event_bus import get_bus,publish
log=logging.getLogger("signal-router")

SIGNAL_ROUTES={
    "incident": ["recovery","planner","governance"],
    "governance_fail": ["security","audit","planner"],
    "deployment": ["delivery","planner","recovery"],
    "drift": ["reconciliation","brain","planner"],
}

class OrganizationalSignalRouter:
    def __init__(self):
        self.bus=get_bus()
    def start(self):
        self.bus.subscribe("incident.detected",lambda e:self.route("incident",e),"sig:incident")
        self.bus.subscribe("governance.fail",lambda e:self.route("governance_fail",e),"sig:govfail")
        self.bus.subscribe("watchdog.drift",lambda e:self.route("drift",e),"sig:drift")
        log.info("Signal router active")
    def route(self,signal_type,event):
        targets=SIGNAL_ROUTES.get(signal_type,[])
        for t in targets:
            publish(f"{t}.signal",{"signal":signal_type,"event":event.get("payload",{})},"signal-router")

SIG_ROUTER=OrganizationalSignalRouter()
def start():SIG_ROUTER.start();return SIG_ROUTER
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print("Active")
