#!/usr/bin/env python3
"""enterprise_chain_of_command.py — Full chain of command for every organizational action."""
import json, logging, os, sys
log = logging.getLogger("chain-cmd")
CHAIN={"reconciliation":"orchestration","orchestration":"governance","governance":"executive","watchdog":"orchestration","delivery":"governance","recovery":"orchestration","security":"governance","infrastructure":"orchestration","observability":"infrastructure","knowledge":"brain","optimization":"executive"}
def resolve(team="watchdog"):
    cmd=[team]; current=team
    while current in CHAIN:
        cmd.append(CHAIN[current]); current=CHAIN[current]
    return {"team":team,"chain":cmd}
def main():
    t=sys.argv[1] if len(sys.argv)>1 else "watchdog"
    print(json.dumps(resolve(t),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
