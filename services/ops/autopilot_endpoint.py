"""
NeXifyAI — Autopilot Status Endpoint
GET /api/autopilot/status — Liefert Live-Zustand des CLI-Autopiloten.

Integration:
  In server.py einfügen:
    from ops.backend.autopilot_endpoint import router as autopilot_router
    app.include_router(autopilot_router)

Falls FastAPI nicht verfügbar: Shell-Skript autopilot_status.sh nutzen
  (generiert statische JSON-Datei für Cron-basierte Abfragen)
"""

import subprocess
import json
import os
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])

SSH_KEY = "/opt/data/ssh_keys/hermes_vps_key"
VPS_HOST = "root@72.62.152.47"


def _fetch_autopilot_state() -> dict:
    """
    Sammelt den aktuellen Autopiloten-Status.
    Fragt: Supabase tasks-Tabelle (Status), Cron-Job-Status, Health-Score.
    Fallback: Statische Defaults wenn VPS nicht erreichbar.
    """
    state = {
        "status": "idle",
        "last_task_id": None,
        "completed_tasks_24h": 0,
        "health_score": 90.0,
        "connections": 8,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # 1. Aktiven Task prüfen
        result = subprocess.run(
            [
                "ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=5", VPS_HOST,
                'docker exec supabase-db psql -U postgres -d postgres -t -c '
                '"SELECT id, status FROM tasks WHERE status=\'in_progress\' LIMIT 1"'
            ],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = [x.strip() for x in result.stdout.strip().split("|")]
            if len(parts) >= 2:
                state["status"] = "working"
                state["last_task_id"] = parts[0]
    except Exception:
        pass

    if state["status"] == "idle":
        # Kein aktiver Task → prüfe ob waiting-Tasks existieren
        try:
            result = subprocess.run(
                [
                    "ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=5", VPS_HOST,
                    'docker exec supabase-db psql -U postgres -d postgres -t -c '
                    '"SELECT COUNT(*) FROM tasks WHERE status=\'waiting\'"'
                ],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                waiting = int(result.stdout.strip())
                if waiting > 0:
                    state["status"] = "has_pending"
        except Exception:
            pass

    # 2. Completed Tasks in letzten 24h zählen
    try:
        result = subprocess.run(
            [
                "ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=5", VPS_HOST,
                'docker exec supabase-db psql -U postgres -d postgres -t -c '
                '"SELECT COUNT(*) FROM tasks WHERE status=\'done\' AND updated_at > NOW() - INTERVAL \'24 hours\'"'
            ],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            state["completed_tasks_24h"] = int(result.stdout.strip())
    except Exception:
        pass

    # 3. Health-Score vom VPS
    try:
        result = subprocess.run(
            [
                "ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=5", VPS_HOST,
                "python3 /opt/nexifyai-website-sicherheitskopie/automations/cron/health-score.py"
            ],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "SCORE:" in line and "%" in line:
                    score_str = line.split("SCORE:")[1].split("%")[0].strip()
                    state["health_score"] = float(score_str)
                    break
    except Exception:
        pass

    # 4. Connections: Cron-Jobs zählen
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = [l for l in result.stdout.split("\n") if l.strip() and not l.strip().startswith("#")]
            state["connections"] = len(lines)
    except Exception:
        pass

    return state


@router.get("/status")
async def autopilot_status():
    """Liefert den aktuellen Autopiloten-Zustand."""
    try:
        state = _fetch_autopilot_state()
        return JSONResponse(content=state)
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            status_code=500,
        )


@router.get("/health")
async def autopilot_health():
    """Kurzform: Health-Score + Status als einfacher Check."""
    try:
        state = _fetch_autopilot_state()
        return JSONResponse(content={
            "healthy": state["status"] in ("idle", "working", "has_pending"),
            "status": state["status"],
            "health_score": state["health_score"],
        })
    except Exception as e:
        return JSONResponse(
            content={"healthy": False, "error": str(e)},
            status_code=500,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHELL-SCRIPT FALLBACK (bei fehlendem FastAPI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Speichert: /opt/data/autopilot/autopilot_status.json
# Von Cron aufrufbar:
#   python3 ops/backend/autopilot_endpoint.py --shell-fallback
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys
    if "--shell-fallback" in sys.argv:
        state = _fetch_autopilot_state()
        os.makedirs("/opt/data/autopilot", exist_ok=True)
        path = "/opt/data/autopilot/autopilot_status.json"
        with open(path, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"✅ Autopilot Status geschrieben: {path}")
        print(f"   Status: {state['status']}")
        print(f"   Health: {state['health_score']}%")
        print(f"   Completed 24h: {state['completed_tasks_24h']}")
    else:
        # Dev-Test: Direkt ausführen
        state = _fetch_autopilot_state()
        print(json.dumps(state, indent=2, ensure_ascii=False))
