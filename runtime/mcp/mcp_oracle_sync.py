#!/usr/bin/env python3
"""mcp_oracle_sync.py -- Syncs MCP capability registry to Brain/ Oracle for semantic discovery."""
import json, logging, requests, uuid
from datetime import datetime, timezone
from event_bus import get_bus, publish
log = logging.getLogger("mcp-oracle")
QDRANT = "http://localhost:6333"

class MCPOracleSync:
    def __init__(self):
        self.bus = get_bus()
    def start(self):
        self.bus.subscribe("mcp.invoke", self._on_invoke, "oracle:invoke")
        log.info("MCP oracle sync active")
    def _on_invoke(self, event):
        try:
            point = {"id": str(uuid.uuid4()), "vector": [0.0]*4, "payload": {"category":"mcp_invocation","source":"mcp_oracle_sync","event": event, "ts": datetime.now(timezone.utc).isoformat()}}
            requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[point]}, timeout=10)
        except: pass

OSYNC = MCPOracleSync()
def start_oracle(): OSYNC.start(); return OSYNC

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_oracle()
