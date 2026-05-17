#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("proj-runtime")
ROUTES = {"drift":"Bug Governance","deploy_ok":"Delivery Control","deploy_fail":"Bug Governance","incident":"Bug Governance","security":"Security Governance","plan":"Strategic Planning"}
def route(etype: str) -> dict:
    proj = ROUTES.get(etype, "Enterprise Operations")
    return {"event":etype,"project":proj}
def main():
    events = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [{"type":"incident"}]
    print(json.dumps([route(e.get("type","")) for e in events], indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
