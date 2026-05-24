#!/usr/bin/env python3
"""roadmap_generator.py — Generates organizational roadmap from goals and system state."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("roadmap")
def generate(goals=None):
    if not goals: goals=[{"id":"G1","title":"Stability","horizon":"6mo","active":True}]
    phases=[{"phase":"immediate","items":[g for g in goals if g.get("horizon")=="1mo"]},{"phase":"short_term","items":[g for g in goals if g.get("horizon")=="3mo"]},{"phase":"long_term","items":[g for g in goals if g.get("horizon") in ("6mo","12mo")]}]
    return {"generated":datetime.now(timezone.utc).isoformat(),"phases":phases}
def main():
    g=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(generate(g),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
