#!/venv/bin/python3
"""worker_main.py — Produktiver Worker. Holt work.assigned, führt via MCP aus."""
import json, logging, os, sys, subprocess, threading, time
from datetime import datetime, timezone
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus
sys.path.insert(0, "/systemmaster/mcp")
from mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker-main] %(levelname)s: %(message)s")
log = logging.getLogger("worker-main")

RESULTS_LOG = "/systemmaster/state/work_results.jsonl"

class Worker:
    def __init__(self):
        self.bus = get_bus()
        self.mcp = MCPClient()
        self.bus.subscribe("work.assigned", self._on_work, "worker:main")
        self._running = True
        log.info("Main worker initialized — listening for work")

    def _log_result(self, result):
        try:
            with open(RESULTS_LOG, "a") as f:
                f.write(json.dumps(result) + "\n")
        except: pass

    def _on_work(self, event):
        payload = event.get("payload", {})
        work_type = payload.get("type", "generic")
        cycle_id = payload.get("cycle_id", "?")
        data = payload.get("data", {})
        log.info("Work received: %s (%s)", work_type, cycle_id)

        result = {"cycle_id": cycle_id, "type": work_type, "ts": time.time(), "actions": []}

        try:
            if work_type == "system_health":
                # Prüfe alle Services via MCP
                svc = self.mcp.query("systemd.list")
                result["actions"].append({"cap": "systemd.list", "result": svc})
                # Prüfe kritische Services einzeln
                for name in ["nexify-eventbus", "nexify-planner", "nexify-mcp-runtime", "nexify-watchdog"]:
                    st = self.mcp.query("systemd.service.status", {"service": f"{name}.service"})
                    result["actions"].append({"cap": "systemd.service.status", "service": name, "status": st})
                log.info("Health check: %d services checked", len(svc) if svc else 0)

            elif work_type == "recovery_check":
                source = data.get("source", "?")
                log.info("Recovery check for %s", source)
                svc = f"nexify-{source}.service" if not source.startswith("nexify-") else source
                st = self.mcp.query("systemd.service.status", {"service": svc})
                result["actions"].append({"cap": "systemd.service.status", "service": svc, "status": st})
                if st and st.get("status") != "active":
                    log.warning("%s not active — restarting", svc)
                    self.mcp.execute("systemd.service.restart", {"service": svc})
                    result["actions"].append({"cap": "systemd.service.restart", "service": svc})

            elif work_type == "log_check":
                path = data.get("path", "/systemmaster/logs/systemmaster.log")
                lines = self.mcp.query("log.tail", {"path": path, "lines": 50})
                result["actions"].append({"cap": "log.tail", "path": path, "lines": lines})

            elif work_type == "state_snapshot":
                # Sammle Zustand aller Systeme
                state = {"services": self.mcp.query("systemd.list"), "timestamp": time.time()}
                self.mcp.execute("state.set", {"key": "system_snapshot", "value": state})
                result["actions"].append({"cap": "state.set", "key": "system_snapshot"})

            else:
                log.info("Unknown work type: %s", work_type)
                result["actions"].append({"error": f"unknown work type: {work_type}"})

        except Exception as e:
            log.error("Work %s failed: %s", work_type, e)
            result["error"] = str(e)

        self._log_result(result)
        self.bus.publish("work.completed", result, "worker-main")
        log.info("Work %s completed: %d actions", cycle_id, len(result["actions"]))

    def run(self):
        threading.Event().wait()

if __name__ == "__main__":
    w = Worker()
    w.run()
