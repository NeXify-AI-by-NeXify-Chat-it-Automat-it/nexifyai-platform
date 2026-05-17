#!/usr/bin/env python3
import json, logging, os, requests, subprocess, sys, uuid
from datetime import datetime, timezone
log = logging.getLogger("incident-mgr")
QDRANT="http://localhost:6333"; IDIR="/runtime/incidents"

class IncidentManager:
    def run(self, title="Auto issue", detail="Detected by watchdog"):
        phases = []
        # Classify
        r = subprocess.run(["python3",f"{IDIR}/severity_classifier.py"], input=json.dumps({"title":title,"detail":detail}), capture_output=True, text=True, timeout=15)
        sev = json.loads(r.stdout) if r.returncode==0 else {"severity":"warning"}
        phases.append({"phase":"classification","severity":sev.get("severity")})
        log.info(f"Severity: {sev.get('severity')}")

        # RCA
        r = subprocess.run(["python3",f"{IDIR}/root_cause_engine.py"], input=json.dumps({"title":title,"detail":detail}), capture_output=True, text=True, timeout=15)
        rca = json.loads(r.stdout) if r.returncode==0 else {"causes":["unknown"]}
        phases.append({"phase":"rca","causes":rca.get("causes")})

        # Recovery route
        r = subprocess.run(["python3",f"{IDIR}/auto_recovery_router.py"], input=json.dumps({"title":title,"causes":rca.get("causes",[])}), capture_output=True, text=True, timeout=15)
        rec = json.loads(r.stdout) if r.returncode==0 else {"actions":["manual"]}
        phases.append({"phase":"recovery","actions":rec.get("actions")})

        # Escalate
        r = subprocess.run(["python3",f"{IDIR}/escalation_engine.py"], input=json.dumps({"title":title,"severity":sev.get("severity")}), capture_output=True, text=True, timeout=15)
        esc = json.loads(r.stdout) if r.returncode==0 else {"path":[]}
        phases.append({"phase":"escalation","path":esc.get("path")})

        # Prevention
        r = subprocess.run(["python3",f"{IDIR}/prevention_task_generator.py"], input=json.dumps({"causes":rca.get("causes",[]),"services":["system"]}), capture_output=True, text=True, timeout=15)
        prev = json.loads(r.stdout) if r.returncode==0 else []
        phases.append({"phase":"prevention","tasks":prev})

        report = {"id":str(uuid.uuid4()),"title":title,"severity":sev.get("severity"),"phases":phases,"ts":datetime.now(timezone.utc).isoformat()}
        try:
            requests.put(f"{QDRANT}/collections/nexifyai_brain/points", json={"points":[{"id":report["id"],"vector":[0.0]*4,"payload":{"category":"incident_lifecycle","source":"incident_manager_v2",**report}}]})
        except: pass
        return report

def main():
    mgr = IncidentManager()
    t = sys.argv[1] if len(sys.argv)>1 else "Auto-detected system issue"
    d = sys.argv[2] if len(sys.argv)>2 else "Detected by watchdog"
    r = mgr.run(t, d)
    print(json.dumps({k:v for k,v in r.items() if k!="phases"}, indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [incident-mgr] %(levelname)s: %(message)s")
    main()
