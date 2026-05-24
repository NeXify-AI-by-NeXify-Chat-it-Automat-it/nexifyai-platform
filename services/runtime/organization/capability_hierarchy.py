#!/usr/bin/env python3
"""capability_hierarchy.py — Maps capabilities to team hierarchy."""
import json, logging, os, sys
log = logging.getLogger("cap-hierarchy")
CAP_TREE={"runtime":{"reconciliation":["drift","sync","truth"],"watchdog":["monitor","health","alert"],"delivery":["pr","deploy","release"]},"intelligence":{"brain":["memory","knowledge","search"],"planner":["strategy","tasks","schedule"]},"governance":{"policy":["compliance","audit"],"security":["secret","threat","access"]}}
def find(cap="monitor"):
    for domain,cats in CAP_TREE.items():
        for team,caps in cats.items():
            if cap in caps: return {"capability":cap,"domain":domain,"team":team}
    return {"capability":cap,"domain":"unknown","team":"infrastructure"}
def main():
    c=sys.argv[1] if len(sys.argv)>1 else "monitor"
    print(json.dumps(find(c),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
