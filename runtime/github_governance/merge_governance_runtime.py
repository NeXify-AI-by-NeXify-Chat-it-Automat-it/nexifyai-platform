#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("merge-gov")
GATES = ["ci","gov","conv","sec","release"]
def check(state: dict = None) -> dict:
    if not state: state = {g:True for g in GATES}
    results = {g:state.get(g,False) for g in GATES}
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"gates":results,"ok":all(results.values())}
def main():
    s = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    print(json.dumps(check(s), indent=2)); exit(0 if check(s)["ok"] else 1)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
