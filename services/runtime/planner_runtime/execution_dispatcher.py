#!/usr/bin/env python3
"""execution_dispatcher.py -- Dispatches planned tasks to target systems asynchronously."""
import logging, os, subprocess, threading
from event_bus import get_bus, publish
log = logging.getLogger("exec-dispatcher")

DISPATCH = {"reconcile":"/opt/nexifyai-platform/services/runtime/reconciliation/auto_reconciler.py","govern":"/services/runtime/github_governance/issue_autogenerator.py","recover":"/services/runtime/incidents/incident_manager.py","observe":"/opt/nexifyai-platform/services/runtime/watchdog/runtime_watchdog.py","learn":"/services/runtime/learning/organizational_learning_engine.py"}

class ExecutionDispatcher:
    def __init__(self): self.bus = get_bus()
    def start(self):
        self.bus.subscribe("org.team_assembled", self._on_routed, "exec:routed"); log.info("Execution dispatcher active")
    def _on_routed(self, event):
        task_type = event.get("payload",{}).get("task_type","")
        script = DISPATCH.get(task_type)
        if script and os.path.exists(script):
            def _run():
                try: r = subprocess.run(["python3",script], capture_output=True, text=True, timeout=30); publish("planner.cycle",{"task":task_type,"rc":r.returncode})
                except: pass
            threading.Thread(target=_run, daemon=True).start()

DISP = None
def start_dispatcher():
    global DISP
    if DISP is None: DISP = ExecutionDispatcher(); DISP.start()
    return DISP

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_dispatcher(); time.sleep(5)
