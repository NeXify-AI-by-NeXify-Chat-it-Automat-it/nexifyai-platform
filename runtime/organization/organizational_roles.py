#!/usr/bin/env python3
"""organizational_roles.py — Defines roles and responsibilities for each organizational unit."""
import json, logging, os, sys
log = logging.getLogger("org-roles")
ROLES={"executive":{"oversight":["all"],"decides":["strategy","architecture","evolution"]},"orchestration":{"oversight":["planner","scheduler"],"decides":["schedule","dispatch"]},"governance":{"oversight":["policy","audit"],"decides":["validation","compliance"]},"reconciliation":{"oversight":["brain","memory"],"decides":["truth","consistency"]}}
def get_role(team="reconciliation"):
    return ROLES.get(team,{"oversight":[],"decides":[]})
def main():
    t=sys.argv[1] if len(sys.argv)>1 else "reconciliation"
    print(json.dumps({"team":t,"role":get_role(t)},indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
