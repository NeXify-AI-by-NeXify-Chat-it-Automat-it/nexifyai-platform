#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("pm-gen")

def generate(inc=None):
    if not inc: inc = {"title":"Test","severity":"warning","summary":"Something"}
    lines = []
    lines.append("# Postmortem: " + inc.get("title","X"))
    lines.append("**Severity:** " + inc.get("severity","info"))
    lines.append("**Summary:** " + inc.get("summary",""))
    lines.append("**Generated:** " + datetime.now(timezone.utc).isoformat())
    pm = chr(10).join(lines)
    return {"markdown": pm, "title": inc.get("title"), "generated": datetime.now(timezone.utc).isoformat()}

def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Test","severity":"warning","summary":"test"}
    print(json.dumps(generate(inc), indent=2))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
