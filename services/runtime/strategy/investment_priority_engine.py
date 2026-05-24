#!/usr/bin/env python3
"""investment_priority_engine.py — Where to invest organizational effort."""
import json, logging, os, sys
log = logging.getLogger("invest-prio")
AREAS={"stability":{"score":95,"roi":"high","recommendation":"invest"},"features":{"score":40,"roi":"medium","recommendation":"maintain"},"debt_reduction":{"score":70,"roi":"high","recommendation":"increase"},"documentation":{"score":30,"roi":"medium","recommendation":"maintain"}}
def prioritize():
    ranked=sorted(AREAS.items(),key=lambda x:x[1]["score"],reverse=True)
    return [{"area":a,"score":s["score"],"roi":s["roi"],"action":s["recommendation"]} for a,s in ranked]
def main():
    print(json.dumps(prioritize(),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
