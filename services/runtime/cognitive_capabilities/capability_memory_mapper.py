#!/usr/bin/env python3
"""capability_memory_mapper.py — Maps capability invocations to Brain memory for recall."""
import json, logging, requests, uuid
from datetime import datetime, timezone
from event_bus import get_bus
log = logging.getLogger("cap-memory")
QDRANT = "http://localhost:6333"

class CapabilityMemoryMapper:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke", self._store, "memory:invoke")
        log.info("Capability memory mapper active")
    def _store(self, event):
        try:
            point = {"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":"capability_invocation","source":"cap_memory_mapper","event":event["payload"],"ts":datetime.now(timezone.utc).isoformat()}}
            requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[point]}, timeout=10)
        except: pass

MAPPER = CapabilityMemoryMapper()
def start(): MAPPER.start(); return MAPPER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print("Active")
