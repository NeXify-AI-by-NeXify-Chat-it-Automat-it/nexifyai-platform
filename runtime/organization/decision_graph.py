#!/usr/bin/env python3
"""decision_graph.py — Decision flow: who decides what based on context."""
import json, logging, os, sys
log = logging.getLogger("dec-graph")
DECISIONS={"emergency_rollback":{"decides":"recovery","notify":["executive","delivery"],"timeframe":"immediate"},"strategic_plan":{"decides":"executive","notify":["all"],"timeframe":"1d"},"pr_approval":{"decides":"delivery","notify":["governance"],"timeframe":"1h"},"policy_update":{"decides":"governance","notify":["executive","all"],"timeframe":"1d"},"incident_classify":{"decides":"watchdog","notify":["recovery"],"timeframe":"5min"}}
def route(decision="incident_classify"):
    return DECISIONS.get(decision,{"decides":"unknown","notify":[],"timeframe":"unknown"})
def main():
    d=sys.argv[1] if len(sys.argv)>1 else "incident_classify"
    print(json.dumps({"decision":d,"flow":route(d)},indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
