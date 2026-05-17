#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("exec-report")
FIELDS = {"health":"Runtime","reconciliation":"Brain rate","deployments":"Deploy rate","incidents":"Open","governance":"Policy compliance"}
def gen(metrics: dict = None) -> dict:
    if not metrics: metrics = {k:"unknown" for k in FIELDS}
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"type":"exec_summary","fields":{FIELDS[k]:v for k,v in metrics.items()}}
def main():
    m = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    print(json.dumps(gen(m), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
