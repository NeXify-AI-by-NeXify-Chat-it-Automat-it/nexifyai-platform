#!/venv/bin/python3
"""watchdog.py — System watchdog. Monitors services, FD, memory."""
import json, logging, os, subprocess, sys, time, psutil
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [watchdog] %(levelname)s: %(message)s")
log = logging.getLogger("watchdog")

MONITORED = {
    "event_bus": "nexify-eventbus.service",
    "planner": "nexify-planner.service",
    "governance": "nexify-governance.service",
    "recovery": "nexify-recovery.service",
    "mcp": "nexify-mcp-runtime.service",
    "systemmaster": "nexify-systemmaster.service",
}

class Watchdog:
    def __init__(self):
        self.bus = get_bus()

    def check_services(self):
        alerts = []
        for name, svc in MONITORED.items():
            r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True, timeout=5)
            status = r.stdout.strip()
            if status != "active":
                alerts.append({"source": name, "service": svc, "status": status, "severity": "critical"})
                log.warning("%s (%s): %s", name, svc, status)
        return alerts

    def check_resources(self):
        alerts = []
        # Memory pressure
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            alerts.append({"source": "memory", "severity": "critical", "detail": f"{mem.percent}%"})
            log.warning("Memory critical: %s%%", mem.percent)
        # FD usage
        proc = psutil.Process()
        fd_count = proc.num_fds()
        if fd_count > 50000:
            alerts.append({"source": "fd_leak", "severity": "critical", "detail": f"{fd_count} fds"})
            log.warning("FD leak: %d open", fd_count)
        # CPU load
        load = psutil.getloadavg()[0]
        cpu_count = psutil.cpu_count()
        if load > cpu_count * 2:
            alerts.append({"source": "cpu_pressure", "severity": "warning", "detail": f"load={load:.1f}"})
        return alerts

    def run(self):
        log.info("Watchdog started (interval=30s)")
        while True:
            try:
                alerts = self.check_services() + self.check_resources()
                criticals = [a for a in alerts if a["severity"] == "critical"]
                if criticals:
                    self.bus.publish("incident.detected", {"severity": "critical", "alerts": criticals}, "watchdog")
                time.sleep(30)
            except Exception as e:
                log.error("Watchdog error: %s", e)
                time.sleep(10)

if __name__ == "__main__":
    w = Watchdog()
    w.run()
