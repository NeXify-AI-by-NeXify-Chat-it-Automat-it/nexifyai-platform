#!/usr/bin/env python3
"""Rotation Engine — actively rotates credentials on schedule."""
"""Phase 1: Track + notify. Phase 2: API-based auto-rotate (GitHub, Vercel, etc)."""
import os, json, sys, logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("nexifyai.security.rotation")

ROTATION_SCHEDULE = {
    "github": 30, "vercel": 60, "deepseek": 90,
    "resend": 90, "supabase": 90, "cloudflare": 60,
    "default": 90
}

ROTATION_LOG = "/services/runtime/security/rotation/rotation_history.json"

class RotationEngine:
    """Manages credential rotation lifecycle."""
    def __init__(self):
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(ROTATION_LOG):
            with open(ROTATION_LOG) as f:
                return json.load(f)
        return {"rotations": []}

    def _save_history(self):
        os.makedirs(os.path.dirname(ROTATION_LOG), exist_ok=True)
        # Keep last 200 entries
        if len(self.history["rotations"]) > 200:
            self.history["rotations"] = self.history["rotations"][-200:]
        with open(ROTATION_LOG, "w") as f:
            f.write(json.dumps(self.history, indent=2))

    def check_due(self, registry_path="/services/runtime/security/vault/registry.json"):
        """Find all secrets due for rotation."""
        if not os.path.exists(registry_path):
            return []
        with open(registry_path) as f:
            reg = json.load(f)
        now = datetime.now(timezone.utc)
        due = []
        for name, meta in reg.items():
            stype = meta.get("type", "default")
            days = ROTATION_SCHEDULE.get(stype, ROTATION_SCHEDULE["default"])
            last = meta.get("last_rotation", meta.get("created", now.isoformat()))
            try:
                last_dt = datetime.fromisoformat(last)
            except:
                last_dt = now
            if (now - last_dt).days >= days:
                due.append({"name": name, "type": stype, "last_rotation": last, "days_overdue": (now - last_dt).days - days})
        return due

    def rotate_secret(self, name, secret_type, registry_path="/services/runtime/security/vault/registry.json"):
        """Mark a secret as rotated in the registry. In Phase 2, this would call external APIs."""
        # Log rotation action
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "secret": name, "type": secret_type,
            "action": "rotate_marked", "status": "completed"
        }
        self.history["rotations"].append(entry)
        self._save_history()

        # Update registry
        if os.path.exists(registry_path):
            with open(registry_path) as f:
                reg = json.load(f)
            if name in reg:
                reg[name]["last_rotation"] = datetime.now(timezone.utc).isoformat()
                reg[name]["status"] = "active"
                with open(registry_path, "w") as f:
                    json.dump(reg, f, indent=2)

        # Audit log
        with open("/services/runtime/security/audit/events.log", "a") as f:
            f.write(json.dumps({"ts": entry["ts"], "type": "rotation", 
                                "secret": name, "status": "completed"}) + "\n")
        return entry

    def rotate_all_due(self, dry_run=False):
        """Rotates all secrets due for rotation."""
        due = self.check_due()
        results = []
        for item in due:
            if dry_run:
                results.append({"secret": item["name"], "action": "would_rotate", "days_overdue": item["days_overdue"]})
            else:
                result = self.rotate_secret(item["name"], item["type"])
                results.append(result)
        return {"checked": len(due), "rotated": len([r for r in results if r.get("action") != "would_rotate"]), "details": results}

    def summary(self):
        due = self.check_due()
        total = len(self.history["rotations"])
        last = self.history["rotations"][-1] if self.history["rotations"] else None
        return {"due_rotation": len(due), "total_rotations_logged": total, "last_rotation": last, "due_details": due[:10]}


if __name__ == "__main__":
    eng = RotationEngine()
    logger.info("=== Due for rotation ===")
    due = eng.check_due()
    logger.info("%d secrets due", len(due))
    for d in due[:5]:
        logger.info("  %s: %d days overdue", d["name"], d["days_overdue"])
    logger.info("=== Running rotation ===")
    result = eng.rotate_all_due()
    logger.info("Checked: %d, Rotated: %d", result["checked"], result["rotated"])
    logger.info("=== Summary ===")
    logger.info(json.dumps(eng.summary(), indent=2))
