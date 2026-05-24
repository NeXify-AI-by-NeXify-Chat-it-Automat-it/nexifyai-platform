#!/usr/bin/env python3
"""organizational_scheduler.py — Schedules work across teams by priority+capacity."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("scheduler")
TEAM_CAPACITY = {"reconciliation":5,"watchdog":3,"delivery":4,"governance":2,"recovery":2,"infrastructure":3,"security":2}

def schedule_tasks(tasks: list = None) -> dict:
    if not tasks: tasks = [{"id":"T-1","assignee":"reconciliation","priority":"P0"}]
    assignments = {}
    for t in tasks:
        team = t.get("assignee","infrastructure")
        if team not in assignments: assignments[team] = []
        if len(assignments[team]) < TEAM_CAPACITY.get(team,2): assignments[team].append(t)
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"assignments":assignments,"total":len(tasks)}

def main():
    r = schedule_tasks()
    print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
