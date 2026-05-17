#!/usr/bin/env python3
"""maturity_evaluator.py -- Evaluates organizational maturity level 1-5."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("maturity")
LVLS = {1:"ad-hoc",2:"automated",3:"governed",4:"autonomous",5:"self-evolving"}
def evaluate(mods=67, teams=14, sys_count=7):
    s = 0
    if mods >= 30: s += 25
    if teams >= 10: s += 25
    if sys_count >= 5: s += 25
    if os.path.exists("/runtime/planner"): s += 15
    if os.path.exists("/runtime/evolution"): s += 10
    lvl = 1
    if s >= 20: lvl = 2
    if s >= 40: lvl = 3
    if s >= 70: lvl = 4
    if s >= 90: lvl = 5
    return {"score": s, "level": lvl, "name": LVLS.get(lvl, "unknown"), "ts": datetime.now(timezone.utc).isoformat()}
def main():
    print(json.dumps(evaluate(), indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
