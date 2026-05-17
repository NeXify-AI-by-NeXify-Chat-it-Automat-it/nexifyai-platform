#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("inc-router")
SMAP = {"critical":"Bug Gov","warning":"Enterprise Ops","info":"Brain"}
def route(inc: dict = None) -> dict:
    if not inc: inc = {"title":"Test","severity":"critical"}
    return {"title":inc.get("title"),"project":SMAP.get(inc.get("severity","info"),"Ops"),"create_issue":inc.get("severity") in ("critical","warning")}
def main():
    incs = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [{"title":"T1","severity":"critical"}]
    print(json.dumps([route(i) for i in incs], indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
