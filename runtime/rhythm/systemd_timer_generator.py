#!/usr/bin/env python3
"""timer_generator.py -- Generates systemd timer definitions for enterprise cycles."""
import json, logging, os, sys
log = logging.getLogger("timer-gen")
TIMERS = {
    "nexify-pulse-5min": {"on": "*:0/5", "cmd": "/runtime/rhythm/enterprise_pulse.py 5min"},
    "nexify-heartbeat-5min": {"on": "*:1/5", "cmd": "/runtime/rhythm/organization_heartbeat.py"},
    "nexify-cycle-ctrl-5min": {"on": "*:2/5", "cmd": "/runtime/rhythm/organizational_cycle_controller.py"},
    "nexify-maturity-hourly": {"on": "0:0", "cmd": "/runtime/rhythm/runtime_maturity_evaluator.py"},
}
def gen(name=None):
    if name: t = TIMERS.get(name); return {"name": name, **t} if t else {"error": f"unknown: {name}"}
    return {"timers": len(TIMERS), "names": list(TIMERS.keys())}
def main():
    n = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(gen(n), indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
