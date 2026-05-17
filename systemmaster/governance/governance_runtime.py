#!/venv/bin/python3
"""governance_runtime.py — Policy enforcement + decision ledger."""
import json, logging, os, sys, time
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [governance] %(levelname)s: %(message)s")
log = logging.getLogger("governance")

DECISIONS = "/systemmaster/state/decision_ledger.jsonl"

def log_decision(action, status, detail=""):
    entry = {"ts": time.time(), "action": action, "status": status, "detail": detail}
    with open(DECISIONS, "a") as f:
        f.write(json.dumps(entry) + "\n")

class Governance:
    def __init__(self):
        self.bus = get_bus()
        self.bus.subscribe("planner.cycle", self._audit, "governance")
        self.bus.subscribe("incident.detected", self._assess, "governance")
        log.info("Governance runtime initialized")

    def _audit(self, event):
        log.info("Audit: planning cycle %s", event.get("payload",{}).get("plan_id","?"))
        log_decision("plan_cycle_audited", "ok", json.dumps(event))

    def _assess(self, event):
        sev = event.get("payload",{}).get("severity","info")
        if sev == "critical":
            log.warning("CRITICAL incident — governance notified")
            self.bus.publish("governance.alert", event, "governance")

    def run(self):
        while True:
            time.sleep(10)

if __name__ == "__main__":
    g = Governance()
    log.info("Governance ready. Blocking forever...")
    g.run()
