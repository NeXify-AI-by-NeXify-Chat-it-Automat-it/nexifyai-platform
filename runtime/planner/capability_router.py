#!/usr/bin/env python3
"""capability_router.py — Routes tasks to correct team via capability matching."""
import json, logging, os, sys
from datetime import datetime
log = logging.getLogger("cap-router")
CAPS = {"reconciliation":["drift","divergence","sync","reconcile","truth","memory"],"watchdog":["monitor","watch","heartbeat","alert","supervise"],"delivery":["pr","merge","deploy","release","rollout","canary"],"governance":["policy","compliance","audit","approve","validate"],"recovery":["incident","rollback","restore","recover","fail"],"security":["secret","vulnerability","threat","permission"],"infrastructure":["network","docker","port","dns","cert","config"]}

def route_task(task: dict) -> dict:
    title = task.get("title","").lower()
    for team,kws in CAPS.items():
        if any(k in title for k in kws): return {"task_id":task.get("id"),"assigned_team":team,"confidence":"high"}
    return {"task_id":task.get("id"),"assigned_team":"infrastructure","confidence":"low"}

def main():
    import select; stdin_data=select.select([sys.stdin],[],[],0.5)[0] if not sys.stdin.isatty() else False; tasks = json.loads(sys.stdin.read()) if not sys.stdin.isatty() and stdin_data else [{"id":"T1","title":"Check drift in memory"}]
    print(json.dumps([route_task(t) for t in tasks], indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
