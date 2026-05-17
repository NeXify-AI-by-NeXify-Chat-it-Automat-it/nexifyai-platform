#!/usr/bin/env python3
import json, logging, os, requests, sys
from datetime import datetime, timezone
log = logging.getLogger("fail-learn"); QDRANT="http://localhost:6333"
def learn(incident=None):
    if not incident: incident={"title":"Timeout","cause":"network","severity":"critical","ts":str(datetime.now(timezone.utc))}
    patterns=[{"pattern":incident.get("cause","unknown"),"count":1,"last_seen":incident.get("ts")}]
    return {"incident":incident.get("title"),"patterns":patterns,"stored":len(patterns)}
def main():
    i=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"title":"Timeout","cause":"network"}
    print(json.dumps(learn(i),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
