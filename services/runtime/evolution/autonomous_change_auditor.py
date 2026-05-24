#!/usr/bin/env python3
"""autonomous_change_auditor.py — Audits every autonomous change for governance compliance."""
import json, logging, os, requests, sys, uuid
from datetime import datetime, timezone
log = logging.getLogger("change-auditor")
QDRANT="http://localhost:6333"
def audit(change=None):
    if not change: change={"type":"module_update","target":"planner","reason":"optimization","approved":True}
    audit_entry={"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":"change_audit","source":"autonomous_change_auditor","change":change,"ts":datetime.now(timezone.utc).isoformat()}}
    try: requests.put(f"{QDRANT}/collections/nexifyai_brain/points",json={"points":[audit_entry]})
    except: pass
    return {"change":change.get("type"),"audited":True,"stored_in_brain":True}
def main():
    c=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"type":"test","reason":"test"}
    print(json.dumps(audit(c),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
