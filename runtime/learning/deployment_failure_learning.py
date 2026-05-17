#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("deploy-learn")
def learn(deploys=None):
    if not deploys: deploys=[{"version":"1.0","success":False,"cause":"health_check_failed"}]
    failed=[d for d in deploys if not d.get("success")]
    return {"total":len(deploys),"failures":len(failed),"failure_rate":len(failed)/max(len(deploys),1),"common_cause":max([d.get("cause","") for d in failed],key=lambda c:sum(1 for d in failed if d.get("cause")==c)) if failed else "none"}
def main():
    d=json.loads(sys.stdin.read()) if not sys.stdin.isatty() else None
    print(json.dumps(learn(d),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
