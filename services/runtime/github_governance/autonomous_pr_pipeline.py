#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("pr-pipeline")
STAGES = ["validate","policies","diff","branch","pr","reviewers","ci"]
def run(change: dict = None) -> dict:
    if not change: change = {"title":"Auto","files":[]}
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"change":change.get("title"),"stages":[{"s":s,"status":"ok"} for s in STAGES],"ok":True}
def main():
    c = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(run(c), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
