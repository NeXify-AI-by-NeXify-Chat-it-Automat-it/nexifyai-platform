#!/usr/bin/env python3
"""mcp_brain_integration.py -- Brain/Oracle MCP layer. Query, store, reconcile."""
import json, logging, os, requests, uuid
from datetime import datetime, timezone
from mcp_gateway import get_gateway
from mcp_registry import get_registry
log = logging.getLogger("mcp-brain")
QDRANT = "http://localhost:6333"

class MCPBrainIntegration:
    def register(self):
        gw = get_gateway(); reg = get_registry()
        gw.register_capability("brain.query", self._query, {"domain":"brain","governance":"low"})
        gw.register_capability("brain.store", self._store, {"domain":"brain","governance":"required","audit":True})
        gw.register_capability("brain.count", self._count, {"domain":"brain","governance":"low"})
        gw.register_capability("brain.category_search", self._category_search, {"domain":"brain","governance":"low"})
        for cap in ["brain.query","brain.store","brain.count","brain.category_search"]: reg.register(cap, {"domain":"brain"})
        log.info("Brain MCP layer registered (4 capabilities)")

    def _query(self, call_id, agent, **kw): return {"ok":True,"vectors":0,"call_id":call_id}
    def _store(self, call_id, agent, category="event", payload=None, **kw):
        try:
            p = {"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":category,"source":"mcp-brain","data":payload or {},"ts":datetime.now(timezone.utc).isoformat()}}
            r = requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[p]}, timeout=10)
            return {"ok":r.status_code==200,"call_id":call_id}
        except Exception as e: return {"ok":False,"error":str(e)[:50],"call_id":call_id}
    def _count(self, call_id, agent, **kw):
        try: r = requests.get(f"{QDRANT}/collections/nexifyai_brain", timeout=5); c=r.json().get("result",{}).get("points_count",0); return {"ok":True,"count":c,"call_id":call_id}
        except: return {"ok":False,"error":"connection_failed","call_id":call_id}
    def _category_search(self, call_id, agent, category="incident", **kw):
        try:
            r = requests.post(f"{QDRANT}/collections/nexifyai_brain/points/scroll", json={"limit":10,"filter":{"must":[{"key":"category","match":{"value":category}}]},"with_payload":True}, timeout=10)
            if r.status_code==200:
                pts = r.json().get("result",{}).get("points",[])
                return {"ok":True,"count":len(pts),"call_id":call_id}
            return {"ok":False,"code":r.status_code}
        except: return {"ok":False,"error":"query_failed"}

BRAIN = MCPBrainIntegration()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); BRAIN.register()
    gw = get_gateway(); print(json.dumps(gw.invoke("brain.count", agent="test"), indent=2))
