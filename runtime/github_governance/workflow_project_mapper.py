#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("wf-map")
PMAP = {"reconciliation":"Brain","deployment":"Delivery","recovery":"Ops","security":"Security","planning":"Strategic"}
def mapwf(wtype: str) -> dict:
    return {"workflow":wtype,"project":PMAP.get(wtype,"Ops")}
def main():
    wfs = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [{"type":"reconciliation"}]
    print(json.dumps([mapwf(w.get("type","")) for w in wfs], indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
