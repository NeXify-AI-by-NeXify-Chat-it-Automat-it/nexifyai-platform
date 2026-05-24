#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("pattern-rec")
PATTERNS={"503_cluster":"service_overload","timeout_cluster":"network_degradation","crash_cluster":"memory_pressure"}
def recognize(signals=None):
    if not signals: signals=[{"type":"http_503","count":5}]
    found=[{"signal":s.get("type"),"pattern":PATTERNS.get(s.get("type",""),"unknown"),"confidence":"high" if s.get("count",0)>3 else "low"} for s in signals]
    return {"signals_analyzed":len(signals),"patterns_found":found}
def main():
    s=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [{"type":"http_503","count":5}]
    print(json.dumps(recognize(s),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
