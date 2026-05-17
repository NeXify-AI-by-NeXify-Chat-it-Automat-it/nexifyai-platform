#!/usr/bin/env python3
import json, logging, os, requests, sys
log = logging.getLogger("inc-mem"); QDRANT="http://localhost:6333"
def graph():
    try:
        r=requests.post(f"{QDRANT}/collections/nexifyai_brain/points/scroll",json={"limit":100,"filter":{"must":[{"key":"category","match":{"value":"incident"}}]},"with_payload":True},timeout=15)
        if r.status_code==200: pts=r.json().get("result",{}).get("points",[]); return {"incidents":len(pts),"severities":{}}
    except: pass
    return {"incidents":0,"severities":{}}
def main():
    print(json.dumps(graph(),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
