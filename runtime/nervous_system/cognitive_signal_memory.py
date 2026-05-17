#!/usr/bin/env python3
"""cognitive_signal_memory.py -- Stores signals in brain for pattern learning."""
import json,logging,requests,uuid
from datetime import datetime,timezone
from event_bus import get_bus
log=logging.getLogger("sig-memory")
Q="http://localhost:6333"

class CognitiveSignalMemory:
    def __init__(self):self.bus=get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke",self._store,"sigmem:invoke")
        log.info("Cognitive signal memory active")
    def _store(self,e):
        try:
            pt={"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":"nervous_signal","source":"cognitive_signal_memory","event":e["payload"],"ts":datetime.now(timezone.utc).isoformat()}}
            requests.put(f"{Q}/collections/nexifyai_brain/points",json={"points":[pt]},timeout=5)
        except:pass

SIG_MEM=CognitiveSignalMemory()
def start():SIG_MEM.start();return SIG_MEM
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO);start();print("Active")
