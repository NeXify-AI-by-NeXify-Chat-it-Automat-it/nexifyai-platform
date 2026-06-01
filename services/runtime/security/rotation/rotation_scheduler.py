#!/usr/bin/env python3
"""Rotation Scheduler -- prioritizes and schedules rotation tasks."""
import os, json
from datetime import datetime, timezone

SCHEDULE = {
    "github": {"days": 30, "prio": "P0", "auto": True},
    "vercel": {"days": 60, "prio": "P1", "auto": False},
    "nexify_provider": {"days": 90, "prio": "P2", "auto": False},
    "resend": {"days": 90, "prio": "P1", "auto": True},
    "supabase": {"days": 90, "prio": "P1", "auto": False},
    "cloudflare": {"days": 60, "prio": "P1", "auto": False},
    "default": {"days": 90, "prio": "P3", "auto": False},
}

class RotationScheduler:
    def __init__(self):
        self.plan_path = "/services/runtime/security/rotation/rotation_plan.json"
    def get_queue(self):
        reg_path = "/services/runtime/security/vault/registry.json"
        if not os.path.exists(reg_path): return []
        with open(reg_path) as f: reg = json.load(f)
        now = datetime.now(timezone.utc)
        queue = []
        for name, meta in reg.items():
            stype = meta.get("type", "default")
            s = SCHEDULE.get(stype, SCHEDULE["default"])
            last_str = meta.get("last_rotation", meta.get("created", now.isoformat()))
            try: last_dt = datetime.fromisoformat(last_str)
            except: last_dt = now
            due = (now - last_dt).days / s["days"]
            queue.append({"name": name, "type": stype, "due_ratio": round(due, 2), "priority": s["prio"], "auto": s["auto"]})
        queue.sort(key=lambda x: (-x["due_ratio"], x["priority"]))
        return queue
    def save_plan(self):
        queue = self.get_queue()
        plan = {"ts": datetime.now(timezone.utc).isoformat(), "count": len(queue), "queue": queue}
        with open(self.plan_path, "w") as f: json.dump(plan, f, indent=2)
        return plan
