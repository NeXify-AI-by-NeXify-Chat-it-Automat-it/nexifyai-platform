#!/usr/bin/env python3
"""resource_allocator.py — Allocates system resources to tasks."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("resource-alloc")
AVAIL = {"timer_slots":10,"queue_capacity":100,"concurrent_tasks":5}

def allocate(task_count: int = 1) -> dict:
    alloc = {"timer_slots":min(task_count, AVAIL["timer_slots"]),"queue_capacity_needed":task_count*10}
    alloc["feasible"] = alloc["queue_capacity_needed"] <= AVAIL["queue_capacity"]
    if task_count > AVAIL["timer_slots"]: alloc["warning"]="Insufficient timer slots"
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"allocation":alloc,"available":AVAIL}

def main():
    count = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print(json.dumps(allocate(count), indent=2)); return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
