#!/usr/bin/env python3
"""self_modification_auditor.py -- Auditor for all self-modifications."""
import json,logging,threading,uuid
from datetime import datetime,timezone
from event_bus import get_bus
log=logging.getLogger("selfmod-audit")
class SelfModAuditor:
    def __init__(self): self._log=[];self._lock=threading.Lock();self.bus=get_bus()
    def start(self):
        self.bus.subscribe("evolution.approved",lambda e:self._log_event("approved",e),"selfmod:approved")
        self.bus.subscribe("evolution.blocked",lambda e:self._log_event("blocked",e),"selfmod:blocked")
        log.info("Self-mod audit active")
    def _log_event(self,status,e):
        with self._lock:self._log.append({"id":str(uuid.uuid4())[:8],"status":status,"event":e["payload"],"ts":datetime.now(timezone.utc).isoformat()})
    def get_log(self,limit=50):
        with self._lock:return list(self._log[-limit:])
AUDITOR=SelfModAuditor()
def start():AUDITOR.start();return AUDITOR
if __name__=="__main__":logging.basicConfig(level=logging.INFO);start();print("Active")
