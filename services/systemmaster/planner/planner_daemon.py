#!/venv/bin/python3
"""planner_daemon.py — Produktiver Planner. Löst MCP-Arbeiten über Eventbus aus."""
import json, logging, os, sys, threading, time, subprocess
from datetime import datetime, timezone
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [planner] %(levelname)s: %(message)s")
log = logging.getLogger("planner")

CHECKPOINT = "/systemmaster/state/planner_checkpoint.json"

class PlannerDaemon:
    def __init__(self):
        self.bus = get_bus()
        self._running = False
        self._lock = threading.Lock()
        self._stopper = threading.Event()
        self._cycle_count = 0
        self._load_checkpoint()
        # Subscribe to work-request events
        self.bus.subscribe("work.request", self._on_work_request, "planner")
        self.bus.subscribe("watchdog.alert", self._on_alert, "planner")
        self.bus.subscribe("mcp.result", self._on_mcp_result, "planner")

    def _load_checkpoint(self):
        if os.path.exists(CHECKPOINT):
            try:
                with open(CHECKPOINT) as f:
                    cp = json.load(f)
                    self._cycle_count = cp.get("cycle_count", 0)
                    log.info("Loaded checkpoint: cycle %d", self._cycle_count)
            except: pass

    def _save_checkpoint(self):
        with open(CHECKPOINT, "w") as f:
            json.dump({"cycle_count": self._cycle_count, "ts": time.time()}, f)

    def start(self):
        self._running = True
        log.info("Planner daemon started (cycle %d)", self._cycle_count)
        t = threading.Thread(target=self._bg_loop, daemon=True); t.start()

    def _on_alert(self, event):
        self._schedule_work("recovery_check", {"source": event.get("payload",{}).get("source","?")})

    def _on_work_request(self, event):
        payload = event.get("payload", {})
        self._schedule_work(payload.get("type", "generic"), payload.get("data", {}))

    def _on_mcp_result(self, event):
        payload = event.get("payload", {})
        cap = payload.get("capability", "?")
        result = payload.get("result", {})
        log.info("MCP result: %s -> %s", cap, json.dumps(result)[:200])

    def _schedule_work(self, work_type, data):
        with self._lock:
            self._cycle_count += 1
            cycle_id = f"cycle-{self._cycle_count}"
        log.info("Scheduling %s as %s", work_type, cycle_id)
        self._save_checkpoint()
        # Publish work to worker queue
        self.bus.publish("work.assigned", {
            "cycle_id": cycle_id,
            "type": work_type,
            "data": data,
            "ts": time.time()
        }, "planner")

    def _bg_loop(self):
        while self._running:
            # Jede Minute: System-Check via MCP
            log.info("Heartbeat cycle %d", self._cycle_count)
            self._schedule_work("system_health", {"interval": "60s"})
            self._stopper.wait(60)

    def get_state(self):
        return {"cycle_count": self._cycle_count, "running": self._running}

_DAEMON = None
def get_planner():
    global _DAEMON
    if _DAEMON is None:
        _DAEMON = PlannerDaemon(); _DAEMON.start()
    return _DAEMON

if __name__ == "__main__":
    p = get_planner()
    log.info("Planner ready — blocking forever")
    threading.Event().wait()
