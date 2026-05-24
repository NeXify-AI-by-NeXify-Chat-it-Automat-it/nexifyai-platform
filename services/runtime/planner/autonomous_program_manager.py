#!/usr/bin/env python3
"""autonomous_program_manager.py — Runs full strategic cycle autonomously."""
import json, logging, os, subprocess, sys, requests, uuid
from datetime import datetime, timezone
log = logging.getLogger("program-mgr")
QDRANT="http://localhost:6333"; PDIR="/services/runtime/planner"
STEPS = ["strategic_planner","task_graph_planner","organizational_scheduler","capability_router","dependency_resolver","resource_allocator","execution_coordinator"]

def run_cycle() -> dict:
    phases = []
    for step in STEPS:
        path = f"{PDIR}/{step}.py"
        if os.path.exists(path):
            r = subprocess.run(["python3",path], capture_output=True, text=True, timeout=30)
            try: data = json.loads(r.stdout)
            except: data = {"raw":r.stdout[:100]}
            phases.append({"step":step,"status":"ok" if r.returncode==0 else "error","output":data})
            log.info(f"  {step}: {'OK' if r.returncode==0 else 'FAIL'}")
    report = {"timestamp":datetime.now(timezone.utc).isoformat(),"phases":phases,"all_ok":all(p["status"]=="ok" for p in phases)}
    try:
        point = {"id":str(uuid.uuid4()),"vector":[0.0]*4,"payload":{"category":"program_cycle","source":"autonomous_program_manager",**report}}
        requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[point]})
    except: pass
    return report

def main():
    r = run_cycle()
    print(json.dumps({k:v for k,v in r.items() if k!="phases"}, indent=2))
    return 0 if r["all_ok"] else 1
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
