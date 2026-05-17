#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("escalation")
PATHS = {"critical":[{"level":1,"wait":5,"action":"auto"},{"level":2,"wait":15,"action":"notify"},{"level":3,"wait":60,"action":"exec"}],"warning":[{"level":1,"wait":30,"action":"auto"},{"level":2,"wait":120,"action":"notify"}],"info":[{"level":1,"wait":360,"action":"backlog"}]}
def escalate(inc=None):
    if not inc: inc = {"title":"Critical","severity":"critical"}
    return {"title":inc.get("title"),"path":PATHS.get(inc.get("severity","info"),[])}
def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Crit","severity":"critical"}
    print(json.dumps(escalate(inc), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
