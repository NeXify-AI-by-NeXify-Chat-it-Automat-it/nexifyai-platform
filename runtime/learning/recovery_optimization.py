#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("rec-opt")
def optimize(history=None):
    if not history: history=[{"action":"restart","time_sec":30,"success":True},{"action":"rollback","time_sec":120,"success":False}]
    avg_time=sum(h.get("time_sec",0) for h in history)/max(len(history),1)
    return {"avg_recovery_time_sec":avg_time,"total_incidents":len(history),"optimal_action":max(history,key=lambda x:x.get("success",False)).get("action","unknown") if history else "none"}
def main():
    h=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(optimize(h),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
