#!/usr/bin/env python3
"""capability_boundary_engine.py — Defines and enforces capability boundaries for each team."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("cap-boundary")
BOUNDARIES={"reconciliation":{"max_concurrent":5,"scope":"brain_data"},"watchdog":{"max_concurrent":3,"scope":"runtime_health"},"delivery":{"max_concurrent":4,"scope":"deployment"},"governance":{"max_concurrent":2,"scope":"policy_valid"},"recovery":{"max_concurrent":2,"scope":"incidents"}}
def check(team="reconciliation",requested=1):
    bounds=BOUNDARIES.get(team,{"max_concurrent":1})
    allowed=requested<=bounds["max_concurrent"]
    return {"team":team,"requested":requested,"max":bounds["max_concurrent"],"allowed":allowed,"scope":bounds.get("scope")}
def main():
    t=sys.argv[1] if len(sys.argv)>1 else "reconciliation"
    r=int(sys.argv[2]) if len(sys.argv)>2 else 1
    print(json.dumps(check(t,r),indent=2)); exit(0 if check(t,r)["allowed"] else 1)
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
