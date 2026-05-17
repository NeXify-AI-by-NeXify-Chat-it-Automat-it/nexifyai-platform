#!/usr/bin/env python3
"""recursive_change_limiter.py — Prevents infinite recursion in self-modifying systems."""
import json, logging, os, sys
from datetime import datetime, timezone, timedelta
log = logging.getLogger("rec-limit")
MAX_DEPTH=5; COOLDOWN_MINUTES=10
def check(chain=None):
    if not chain: chain={"depth":1,"last_change":"2026-05-16T20:00:00"}
    allowed=chain.get("depth",0)<=MAX_DEPTH
    return {"depth":chain.get("depth"),"max":MAX_DEPTH,"allowed":allowed,"reason":"ok" if allowed else "max_depth_exceeded"}
def main():
    c=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"depth":1}
    print(json.dumps(check(c),indent=2)); exit(0 if check(c)["allowed"] else 1)
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
