#!/venv/bin/python3
"""recovery_daemon.py — Listens for incidents. Routes to auto-recovery actions."""
import json, logging, os, subprocess, sys, time
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [recovery] %(levelname)s: %(message)s")
log = logging.getLogger("recovery")

class RecoveryDaemon:
    def __init__(self):
        self.bus = get_bus()
        self.bus.subscribe("incident.detected", self._on_incident, "recovery")
        self._retries = {}
        log.info("Recovery daemon initialized")

    def _restart_svc(self, svc):
        r = subprocess.run(["systemctl", "restart", svc], capture_output=True, text=True, timeout=30)
        ok = r.returncode == 0
        log.info("Restart %s: %s", svc, "OK" if ok else "FAIL")
        return ok

    def _on_incident(self, event):
        payload = event.get("payload", {})
        source = payload.get("source", event.get("source", "unknown"))
        severity = payload.get("severity", "warning")

        self._retries[source] = self._retries.get(source, 0) + 1
        retry = self._retries[source]

        if retry > 3:
            log.critical("ESCALATION: %s failed %d times", source, retry)
            self.bus.publish("governance.alert", {"type": "incident.escalated", "source": source}, "recovery")
            return

        if severity != "critical":
            log.info("Non-critical incident from %s — no auto-recovery", source)
            return

        svc_map = {
            "planner": "nexify-planner.service",
            "event_bus": "nexify-eventbus.service",
            "watchdog": "nexify-watchdog.service",
            "anton": "nexify-systemmaster.service",
        }
        svc = svc_map.get(source, f"nexify-{source}.service")
        ok = self._restart_svc(svc)
        self.bus.publish("recovery.action", {"service": svc, "success": ok, "retry": retry}, "recovery")

    def run(self):
        while True:
            time.sleep(10)

if __name__ == "__main__":
    r = RecoveryDaemon()
    log.info("Recovery ready. Blocking forever...")
    r.run()
