#!/usr/bin/env python3
"""cycle_controller.py -- Determines cycle based on system state and time."""
import json, logging, os, requests, sys
from datetime import datetime, timezone
log = logging.getLogger("cycle-ctrl")
def determine():
    now = datetime.now(timezone.utc); m = now.minute
    if m % 5 == 0: base = "5min_op"
    elif m % 15 == 0: base = "15min_tac"
    elif m % 30 == 0: base = "30min_strat"
    elif m == 0: base = "60min_ent"
    else: base = "cont"
    try:
        r = requests.post("http://localhost:6333/collections/nexifyai_brain/points/scroll", json={"limit":5,"filter":{"must":[{"key":"status","match":{"value":"open"}}]}}, timeout=10)
        if r.status_code == 200 and len(r.json().get("result",{}).get("points",[])) > 0: base = "incident"
    except: pass
    return {"cycle": base, "ts": now.isoformat()}
def main():
    print(json.dumps(determine(), indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
