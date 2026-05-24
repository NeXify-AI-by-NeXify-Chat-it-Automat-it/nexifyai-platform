#!/usr/bin/env python3
"""
DEPRECATED: Wird durch services/planner_workflow.py ersetzt.
            LangGraph StateGraph übernimmt Task-Graph + Dependency Resolution.
            Entfernung geplant: 2026-06-21
"""

"""task_graph_planner.py — Breaks objectives into dependency-ordered task graphs."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("task-planner")

def generate_task_graph(objectives: list = None) -> dict:
    if not objectives: objectives = [{"id": "OBJ-1", "title": "System Health", "priority": "P0"}]
    tasks = []
    for obj in objectives:
        tasks.append({"id": f"T-{obj.get('id','OBJ')}-1", "objective": obj.get("title"), "depends_on": [], "assignee": "reconciliation", "status": "pending"})
        tasks.append({"id": f"T-{obj.get('id','OBJ')}-2", "objective": obj.get("title"), "depends_on": [f"T-{obj.get('id','OBJ')}-1"], "assignee": "watchdog", "status": "pending"})
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "tasks": tasks, "count": len(tasks)}

def main():
    r = generate_task_graph()
    print(json.dumps(r, indent=2))
    return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
