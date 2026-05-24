#!/usr/bin/env python3
"""dependency_resolver.py — Computes topological execution order."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("dep-resolver")

def resolve(tasks: list = None) -> dict:
    if not tasks: tasks = [{"id":"A","depends_on":[]},{"id":"B","depends_on":["A"]},{"id":"C","depends_on":["B"]}]
    resolved, order = [], []
    remaining = list(tasks)
    while remaining:
        ready = [t for t in remaining if all(d in [r["id"] for r in resolved] for d in t.get("depends_on",[]))]
        if not ready: break
        for t in ready: resolved.append(t); order.append(t["id"]); remaining.remove(t)
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"execution_order":order,"resolved":len(resolved),"remaining":len(remaining)}

def main():
    r = resolve(); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
