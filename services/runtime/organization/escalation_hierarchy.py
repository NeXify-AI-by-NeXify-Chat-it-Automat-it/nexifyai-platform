#!/usr/bin/env python3
"""escalation_hierarchy.py — Defines escalation paths for decisions and incidents."""
import json, logging, os, sys
log = logging.getLogger("esc-hierarchy")
PATHS={"reconciliation":["orchestration","governance","executive"],"watchdog":["orchestration","governance","executive"],"delivery":["governance","executive"],"security":["governance","executive"],"infrastructure":["orchestration","executive"]}
def escalate(team="watchdog",level=1):
    path=PATHS.get(team,["orchestration","executive"])
    if level>=len(path): return {"team":team,"escalate_to":"executive","final":True}
    return {"team":team,"escalate_to":path[level],"level":level,"final":False}
def main():
    t=sys.argv[1] if len(sys.argv)>1 else "watchdog"
    l=int(sys.argv[2]) if len(sys.argv)>2 else 1
    print(json.dumps(escalate(t,l),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
