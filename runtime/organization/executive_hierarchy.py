#!/usr/bin/env python3
"""executive_hierarchy.py — Defines executive chain: who decides what."""
import json, logging, os, sys
from datetime import datetime
log = logging.getLogger("exec-hierarchy")
HIERARCHY=[{"level":"C-suite","teams":["executive"]},{"level":"Directors","teams":["orchestration","governance"]},{"level":"Managers","teams":["reconciliation","watchdog","delivery","security"]},{"level":"Leads","teams":["frontend","backend","infrastructure","ai_runtime"]},{"level":"Staff","teams":["observability","recovery","knowledge","optimization"]}]
def resolve(team="delivery"):
    for level in HIERARCHY:
        if team in level["teams"]: return {"team":team,"level":level["level"],"chain_of_command":[l["level"] for l in HIERARCHY[:HIERARCHY.index(level)+1]]}
    return {"team":team,"level":"unknown","chain":[]}
def main():
    t=sys.argv[1] if len(sys.argv)>1 else "delivery"
    print(json.dumps(resolve(t),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
