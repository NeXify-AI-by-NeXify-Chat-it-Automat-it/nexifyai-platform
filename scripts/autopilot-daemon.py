#!/usr/bin/env python3
'''
NeXifyAI — Autopilot Daemon v1.0
Haupt-Loop: intake_task() → plan() → execute() → verify() → decide()
Heartbeat: /opt/nexifyai/state/heartbeat.md
'''
import os, sys, json, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

HEARTBEAT_FILE = "/opt/nexifyai/state/heartbeat.md"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://localhost:5432")
REPO_ROOT = "/opt/nexifyai-website-sicherheitskopie"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def write_heartbeat(state: dict):
    os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
    state["tick"] = state.get("tick", 0) + 1
    with open(HEARTBEAT_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def read_heartbeat() -> dict:
    if os.path.isfile(HEARTBEAT_FILE):
        with open(HEARTBEAT_FILE) as f:
            return json.load(f)
    return {"started": now_iso(), "tick": 0, "runs": 0}

def intake_task() -> dict | None:
    '''Liest Tasks aus Supabase mit status=waiting, priorisiert nach rice_score.'''
    try:
        result = subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-t", "-c",
            "SELECT id,title,description,priority,rice_score,retry_count,max_retries "
            "FROM public.tasks WHERE autopilot=true AND status='waiting' "
            "ORDER BY rice_score DESC NULLS LAST, priority LIMIT 1"
        ], capture_output=True, text=True, timeout=10, 
        env={**os.environ, "PGPASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres")})
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|")
            if len(parts) >= 5:
                return {
                    "id": parts[0].strip(), "title": parts[1].strip(),
                    "description": parts[2].strip(), "priority": parts[3].strip(),
                    "rice_score": float(parts[4].strip()) if parts[4].strip() else 0,
                    "retry_count": int(parts[5].strip()) if len(parts) > 5 else 0,
                    "max_retries": int(parts[6].strip()) if len(parts) > 6 else 3,
                }
    except Exception as e:
        print(f"[intake] Error: {e}")
    return None

def mark_status(task_id: str, status: str):
    try:
        subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-c",
            f"UPDATE public.tasks SET status='{status}', updated_at='{now_iso()}' WHERE id='{task_id}'"
        ], capture_output=True, timeout=10,
        env={**os.environ, "PGPASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres")})
    except Exception as e:
        print(f"[mark_status] Error: {e}")

def execute_task(task: dict) -> bool:
    '''Einfacher Executor: Versucht Task via Subprozess auszuführen.'''
    print(f"[exec] Starting task {task['id']}: {task['title']}")
    # Platzhalter: In Produktion wird hier KI-basierte Task-Ausführung passieren
    time.sleep(1)
    return True  # Erfolg simuliert für Basisgerüst

def handle_failure(task: dict):
    print(f"[fail] Task {task['id']} failed (retry {task['retry_count']}/{task['max_retries']})")
    try:
        subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-c",
            f"INSERT INTO public.incidents (task_id, error_type, retry_count, created_at) "
            f"VALUES ('{task['id']}','execution_failure',{task['retry_count']},'{now_iso()}')"
        ], capture_output=True, timeout=10,
        env={**os.environ, "PGPASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres")})
    except Exception as e:
        print(f"[fail] Error logging incident: {e}")

    if task['retry_count'] >= task['max_retries']:
        mark_status(task['id'], "failed")
    else:
        mark_status(task['id'], "waiting")

def main():
    print(f"[autopilot] Daemon starting at {now_iso()}")
    state = read_heartbeat()
    state["last_start"] = now_iso()
    
    while True:
        try:
            task = intake_task()
            if not task:
                write_heartbeat({**state, "status": "idle", "tick": state.get("tick", 0) + 1})
                time.sleep(60)
                continue
            
            mark_status(task["id"], "in_progress")
            write_heartbeat({**state, "current_task": task["id"], "status": "executing"})
            
            success = execute_task(task)
            
            if success:
                mark_status(task["id"], "done")
                state["runs"] = state.get("runs", 0) + 1
                write_heartbeat({**state, "last_task": task["id"], "status": "completed"})
                print(f"[autopilot] Task {task['id']} completed successfully")
            else:
                handle_failure(task)
                write_heartbeat({**state, "last_task": task["id"], "status": "failed"})
        
        except KeyboardInterrupt:
            write_heartbeat({**state, "status": "stopped", "stopped_at": now_iso()})
            print("[autopilot] Daemon stopped")
            sys.exit(0)
        except Exception as e:
            print(f"[autopilot] Crash: {e}")
            write_heartbeat({**state, "status": "crashed", "error": str(e)})
            time.sleep(30)

if __name__ == "__main__":
    main()
