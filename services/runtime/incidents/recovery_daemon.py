#!/usr/bin/env python3
"""recovery_daemon.py — Listens for incident.detected events, runs auto_recovery_router, executes recovery."""
import json, logging, os, subprocess, sys, time
sys.path.insert(0, "/services/runtime/events")
from event_bus import get_bus, publish
log = logging.getLogger("recovery-daemon")

class RecoveryDaemon:
    def __init__(self):
        self.bus = get_bus()
        self._running = False
    
    def _on_incident(self, event):
        detail = event.get("detail", event.get("payload", {}))
        if isinstance(detail, str):
            try: detail = json.loads(detail)
            except: pass
        
        inc = {
            "title": event.get("source", "watchdog"),
            "causes": ["service_down"],
            "source": detail.get("source", "unknown") if isinstance(detail, dict) else "unknown",
            "severity": detail.get("severity", "info") if isinstance(detail, dict) else "info"
        }
        
        # Only auto-recover critical
        if inc.get("severity") != "critical":
            log.info("Non-critical incident, skipping auto-recovery")
            return
        
        log.info("Running auto-recovery for: %s", json.dumps(inc))
        r = subprocess.run(
            ["python3", "/services/runtime/incidents/auto_recovery_router.py"],
            input=json.dumps(inc), capture_output=True, text=True, timeout=20
        )
        log.info("Recovery result: %s", r.stdout[:500])
        
        # If escalation needed, notify
        if "escalate" in r.stdout:
            publish("governance.alert", {
                "type": "incident.escalated",
                "detail": r.stdout[:1000],
                "ts": time.time()
            }, "recovery-daemon")
    
    def start(self):
        self._running = True
        self.bus.subscribe("incident.detected", self._on_incident, "recovery:incidents")
        log.info("Recovery daemon started — listening for incidents")
        while self._running:
            time.sleep(1)
    
    def stop(self):
        self._running = False

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    rd = RecoveryDaemon()
    rd.start()

if __name__ == "__main__":
    main()
