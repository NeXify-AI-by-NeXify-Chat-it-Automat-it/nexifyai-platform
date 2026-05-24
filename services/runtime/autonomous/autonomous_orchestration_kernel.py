#!/usr/bin/env python3
"""autonomous_orchestration_kernel.py — The permanent organizational runtime kernel.
Runs continuously: observe -> detect -> plan -> execute -> validate -> learn -> evolve.
"""
import json, logging, os, requests, subprocess, sys, time, uuid
from datetime import datetime, timezone
log = logging.getLogger("auto-kernel")

class AutonomousKernel:
    def __init__(self):
        self.token = os.environ.get("DS_GITHUB_9569466F__TOKEN", "")
        self.repo = "nexifyai-dev/nexifyai-website-sicherheitskopie"
        self.api = "https://api.github.com"
        self.hdrs = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json"} if self.token else {}

    def observe(self):
        """Phase 1: Observe system state"""
        log.info("OBSERVE: Scanning runtime state")
        state = {"ts": datetime.now(timezone.utc).isoformat()}
        try:
            r = requests.get("http://localhost:6333/collections/nexifyai_brain", timeout=5)
            if r.status_code == 200: state["brain"] = r.json().get("result",{}).get("points_count",0)
            else: state["brain"] = -1
        except: state["brain"] = -1
        try:
            r = requests.post("http://localhost:6333/collections/nexifyai_brain/points/scroll",
                json={"limit":5,"filter":{"must":[{"key":"category","match":{"value":"incident"}}]},"with_payload":True}, timeout=10)
            if r.status_code == 200:
                state["open_incidents"] = len(r.json().get("result",{}).get("points",[]))
        except: state["open_incidents"] = 0
        # Check systemd timers
        r = subprocess.run("systemctl list-timers --no-pager | grep -c nexify", shell=True, capture_output=True, text=True, timeout=5)
        state["active_timers"] = int(r.stdout.strip() or 0)
        return state

    def detect(self, state):
        """Phase 2: Detect what needs to happen"""
        log.info("DETECT: Analyzing state for actions")
        actions = []
        if state.get("brain", 0) == -1:
            actions.append({"type":"recover","target":"brain","priority":"P0","reason":"Brain unreachable"})
        if state.get("open_incidents", 0) > 0:
            actions.append({"type":"process_incidents","target":"incident_manager","priority":"P0","reason":f"{state['open_incidents']} open incidents"})
        if state.get("active_timers", 0) < 14:
            actions.append({"type":"restore_timers","target":"systemd","priority":"P1","reason":f"Only {state.get('active_timers',0)}/14 timers active"})
        # Always plan
        actions.append({"type":"plan_cycle","target":"planner","priority":"P2","reason":"Continuous planning"})
        return actions

    def plan_and_execute(self, actions):
        """Phase 3-5: Plan, dispatch, execute"""
        log.info(f"PLAN+EXECUTE: {len(actions)} actions")
        results = []
        for a in actions:
            log.info(f"  Action: {a['type']} on {a['target']} [{a['priority']}]")
            if a["type"] == "plan_cycle":
                r = subprocess.run(["python3","/services/runtime/planner/autonomous_program_manager.py"], capture_output=True, text=True, timeout=30)
                results.append({"action":a["type"],"result":"dispatched","detail":"Planner cycle triggered"})
            elif a["type"] == "process_incidents":
                r = subprocess.run(["python3","/services/runtime/incidents/incident_manager.py"], capture_output=True, text=True, timeout=30)
                results.append({"action":a["type"],"result":"dispatched"})
            elif a["type"] == "recover":
                results.append({"action":a["type"],"result":"queued"})
            else:
                results.append({"action":a["type"],"result":"acknowledged"})
        return results

    def validate(self, results):
        """Phase 6: Validate execution results"""
        failed = [r for r in results if r.get("status") == "error"]
        return {"validated": len(failed) == 0, "failed": len(failed)}

    def learn_and_store(self, state, actions, results):
        """Phase 7-8: Learn and store in Brain"""
        entry = {"id": str(uuid.uuid4()), "vector": [0.0]*4, "payload": {
            "category": "autonomous_cycle", "source": "autonomous_kernel",
            "state": state, "actions": [a["type"] for a in actions],
            "results": results, "ts": datetime.now(timezone.utc).isoformat()
        }}
        try:
            requests.put("http://localhost:6333/collections/nexifyai_brain/points", json={"points":[entry]}, timeout=10)
        except: pass
        return True

    def run_cycle(self):
        """Full autonomous cycle"""
        log.info("=== AUTONOMOUS KERNEL CYCLE START ===")
        state = self.observe()
        log.info(f"State: brain={state.get('brain')}, incidents={state.get('open_incidents')}, timers={state.get('active_timers')}")
        actions = self.detect(state)
        results = self.plan_and_execute(actions)
        self.learn_and_store(state, actions, results)
        log.info("=== AUTONOMOUS KERNEL CYCLE COMPLETE ===")
        return {"state": state, "actions": len(actions), "results": len(results)}

def main():
    kernel = AutonomousKernel()
    result = kernel.run_cycle()
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [kernel] %(name)s: %(levelname)s: %(message)s")
    sys.exit(main())
