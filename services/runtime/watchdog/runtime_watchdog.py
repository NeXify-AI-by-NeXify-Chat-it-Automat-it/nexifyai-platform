#!/usr/bin/env python3
"""runtime_watchdog.py — Persistent system watchdog daemon. Monitors process health, fd/memory pressure, publishes alerts."""
import json, logging, os, subprocess, sys, time, threading
from datetime import datetime, timezone

sys.path.insert(0, "/services/runtime/events")
from event_bus import get_bus, publish

log = logging.getLogger("watchdog-daemon")

class RuntimeWatchdog:
    def __init__(self):
        self.bus = get_bus()
        self._running = False
        self._interval = 15  # seconds between checks
        # Define monitored services and their check commands
        self._monitored = {
            "anton": {"svc": "anton.service", "critical": True},
            "planner": {"svc": "anton-planner-runtime.service", "critical": True},
            "event_bus": {"svc": "nexify-event-bus.service", "critical": True},
            "mcp": {"svc": "nexify-mcp-daemon.service", "critical": True},
            "cognitive": {"svc": "nexify-cognitive-runtime.service", "critical": True},
        }
        # Additional health checks that don't rely on systemd
        self._health_checks = {
            "anton_proc": self._check_anton_proc,
            "fd_usage": self._check_fd_usage,
            "memory_pressure": self._check_memory,
        }

    def _check_anton_proc(self):
        r = subprocess.run(["pgrep", "-f", "anton$"], capture_output=True, text=True, timeout=5)
        return {"alive": r.returncode == 0, "count": len(r.stdout.strip().split()) if r.stdout else 0}

    def _check_fd_usage(self):
        try:
            procs = subprocess.run(["find", "/proc", "-maxdepth", "1", "-name", "[0-9]*"], capture_output=True, text=True, timeout=5)
            max_fd = 65536
            for pid in procs.stdout.strip().split()[-10:]:
                fd = subprocess.run(["ls", "-1", f"{pid}/fd"], capture_output=True, text=True, timeout=3)
                fd_count = len(fd.stdout.strip().split()) if fd.stdout else 0
                if fd_count > max_fd * 0.8:
                    return {"alive": False, "fd_count": fd_count, "pid": pid, "critical": True}
            return {"alive": True}
        except: return {"alive": True}

    def _check_memory(self):
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemAvailable" in line:
                        avail_kb = int(line.split()[1])
                        with open("/proc/meminfo") as f2:
                            for l2 in f2:
                                if "MemTotal" in l2:
                                    total_kb = int(l2.split()[1])
                                    pct = (total_kb - avail_kb) / total_kb * 100
                                    return {"alive": pct < 95, "mem_pct": round(pct, 1), "critical": pct > 90}
                        break
            return {"alive": True}
        except: return {"alive": True}

    def _check_service(self, svc_name):
        r = subprocess.run(["systemctl", "is-active", svc_name], capture_output=True, text=True, timeout=5)
        status = r.stdout.strip()
        return {"alive": status == "active", "status": status}

    def check_all(self):
        results = {"ts": datetime.now(timezone.utc).isoformat(), "services": {}, "health": {}, "alerts": []}

        # Service checks
        for name, cfg in self._monitored.items():
            s = self._check_service(cfg["svc"])
            results["services"][name] = s
            if not s["alive"] and cfg["critical"]:
                results["alerts"].append({
                    "type": "watchdog.alert",
                    "severity": "critical",
                    "source": name,
                    "detail": f"{cfg['svc']} ({s.get('status','unknown')})"
                })

        # Health checks
        for name, check_fn in self._health_checks.items():
            try:
                h = check_fn()
                results["health"][name] = h
                if not h.get("alive", True) and h.get("critical", False):
                    results["alerts"].append({
                        "type": "watchdog.alert",
                        "severity": "critical",
                        "source": name,
                        "detail": json.dumps({k:v for k,v in h.items() if k != "alive"})
                    })
            except Exception as e:
                results["health"][name] = {"alive": False, "error": str(e)}

        return results

    def run(self):
        self._running = True
        log.info("Watchdog daemon started (interval=%ss)", self._interval)
        while self._running:
            try:
                results = self.check_all()
                # Publish all alerts
                for alert in results.get("alerts", []):
                    publish(alert["type"], alert, "watchdog")
                # If there are critical failures publish to incident manager path too
                if any(a["severity"] == "critical" for a in results.get("alerts", [])):
                    publish("incident.detected", {
                        "source": "watchdog",
                        "severity": "critical",
                        "detail": json.dumps(results["alerts"]),
                        "ts": results["ts"]
                    }, "watchdog")
                time.sleep(self._interval)
            except Exception as e:
                log.error("Watchdog cycle error: %s", e)
                time.sleep(self._interval)

    def stop(self):
        self._running = False

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    wd = RuntimeWatchdog()
    wd.run()

if __name__ == "__main__":
    main()
