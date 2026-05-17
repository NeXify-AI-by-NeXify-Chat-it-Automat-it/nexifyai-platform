#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("rca-engine")
PATTERNS = {"timeout":"network_issue","crash":"memory_pressure","503":"overloaded","500":"app_error","refused":"service_down","dns":"dns_resolution","cert":"tls_expiry","disk":"disk_full","permission":"permission_denied"}
def analyze(inc=None):
    if not inc: inc = {"title":"Timeout","detail":"Connection timed out"}
    text = (inc.get("title","")+" "+inc.get("detail","")).lower()
    causes = [p for pat,p in PATTERNS.items() if pat in text]
    return {"title":inc.get("title"),"causes":causes or ["unknown"],"confidence":"high" if causes else "low","ts":datetime.now(timezone.utc).isoformat()}
def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Timeout error","detail":"Connection timeout after 30s"}
    print(json.dumps(analyze(inc), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
