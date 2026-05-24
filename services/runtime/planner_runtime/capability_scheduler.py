#!/usr/bin/env python3
"""capability_scheduler.py -- Schedules planner tasks to teams by capability matching."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("cap-scheduler")

TEAMS = {"reconciliation":["reconcile","sync","dedup"],"watchdog":["observe","monitor","detect"],"governance":["govern","validate","audit"],"delivery":["deploy","pr","release"],"recovery":["recover","restore","heal"],"learning":["learn","analyze","pattern"],"infrastructure":["infra","network","deploy"],"security":["secure","audit","scan"]}

def schedule(task_type, priority="P2"):
    for team, caps in TEAMS.items():
        if task_type in caps:
            publish("org.team_assembled", {"team":team,"task_type":task_type,"priority":priority},"cap-scheduler")
            return {"team":team,"task_type":task_type,"priority":priority}
    return {"team":"general","task_type":task_type}

if __name__ == "__main__":
    import sys; print(json.dumps(schedule(sys.argv[1] if len(sys.argv)>1 else "reconcile"), indent=2))
