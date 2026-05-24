#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("harden")
def harden(failures=None):
    if not failures: failures=[{"type":"timeout","count":10}]
    actions=[{"trigger":f.get("type"),"action":"add_circuit_breaker","priority":"P0" if f.get("count",0)>5 else "P1"} for f in failures]
    return {"actions":actions}
def main():
    f=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(harden(f),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
