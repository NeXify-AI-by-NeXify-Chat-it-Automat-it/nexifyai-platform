#!/usr/bin/env python3
"""priority_engine.py — Dynamic priority assignment based on severity."""
import json, logging, os, sys
from datetime import datetime
log = logging.getLogger("priority-engine")
MAP = {"critical":0,"warning":1,"info":2}

def assign_priority(items: list = None) -> list:
    if not items: items = [{"title":"Test","severity":"critical"}]
    for i in items:
        base = MAP.get(i.get("severity","info"),2)
        i["priority_score"] = base; i["priority_label"] = "P0" if base==0 else "P1" if base==1 else "P2"
    return sorted(items, key=lambda x: x.get("priority_score",99))

def main():
    items = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [{"title":"Test","severity":"critical"}]
    print(json.dumps(assign_priority(items), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
