#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("sev-classifier")
CRIT = ["down","crash","data_loss","security","breach","outage","production"]
WARN = ["degraded","slow","warning","high_memory","error_rate","latency"]
def classify(inc=None):
    if not inc: inc = {"title":"Production down","detail":"All 503s"}
    text = (inc.get("title","")+" "+inc.get("detail","")).lower()
    crit = any(k in text for k in CRIT); warn = any(k in text for k in WARN)
    sev = "critical" if crit else "warning" if warn else "info"
    return {"title":inc.get("title"),"severity":sev,"response":"15min" if sev=="critical" else "1h" if sev=="warning" else "24h"}
def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Down","detail":"All 503"}
    print(json.dumps(classify(inc), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
