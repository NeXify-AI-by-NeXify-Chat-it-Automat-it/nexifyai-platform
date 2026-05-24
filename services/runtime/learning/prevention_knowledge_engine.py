#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("prev-knowledge")
def generate(incidents=None):
    if not incidents: incidents=[{"title":"Timeout","cause":"network","prevention":"add_timeout_handler"}]
    return [{"from":i.get("title"),"prevention":i.get("prevention")} for i in incidents]
def main():
    i=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(generate(i),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
