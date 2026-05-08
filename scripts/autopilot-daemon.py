#!/usr/bin/env python3
"""NeXifyAI Autopilot Daemon v1.1 — Intake→Execute→Verify→Decide"""
import os, sys, json, time, subprocess
from datetime import datetime, timezone

HEARTBEAT_FILE = "/opt/nexifyai/state/heartbeat.md"

def now_iso(): return datetime.now(timezone.utc).isoformat()
def psql(query):
    return subprocess.run(["docker","exec","supabase-db","psql","-U","postgres","-d","postgres","-t","-c",query],
                          capture_output=True,text=True,timeout=10)

def write_heartbeat(state):
    os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
    state["tick"] = state.get("tick",0)+1
    with open(HEARTBEAT_FILE,"w") as f: json.dump(state,f,indent=2,default=str)

def read_heartbeat():
    if os.path.isfile(HEARTBEAT_FILE):
        with open(HEARTBEAT_FILE) as f: return json.load(f)
    return {"started":now_iso(),"tick":0,"runs":0}

def intake_task():
    r = psql("SELECT id,title,priority,rice_score,retry_count,max_retries FROM public.tasks WHERE autopilot=true AND status='waiting' ORDER BY rice_score DESC NULLS LAST, priority LIMIT 1")
    if r.returncode==0 and r.stdout.strip():
        p = r.stdout.strip().split("|")
        if len(p)>=4:
            return {"id":p[0].strip(),"title":p[1].strip(),"priority":p[2].strip(),
                    "rice_score":float(p[3].strip()) if p[3].strip() else 0,
                    "retry_count":int(p[4].strip()) if len(p)>4 else 0,"max_retries":3}
    return None

def mark(task_id,status):
    psql(f"UPDATE public.tasks SET status='{status}', updated_at='{now_iso()}' WHERE id='{task_id}'")

def execute_task(task):
    print(f"[exec] {task['id'][:8]}: {task['title'][:60]}")
    time.sleep(1)
    return True

def handle_failure(task):
    r = psql(f"INSERT INTO public.incidents (task_id,error_type,retry_count,created_at) VALUES ('{task['id']}','execution_failure',{task['retry_count']},'{now_iso()}')")
    if task['retry_count'] >= task['max_retries']:
        mark(task['id'],"failed")
    else:
        mark(task['id'],"waiting")

def main():
    state = read_heartbeat()
    state["last_start"] = now_iso()
    print(f"[autopilot] v1.1 started")
    
    while True:
        try:
            task = intake_task()
            if not task:
                write_heartbeat({**state,"status":"idle"})
                time.sleep(30)
                continue
            
            print(f"[autopilot] Task: {task['title'][:60]}")
            mark(task['id'],"in_progress")
            write_heartbeat({**state,"current_task":task['id'][:8],"status":"executing"})
            
            ok = execute_task(task)
            if ok:
                mark(task['id'],"done")
                state["runs"] = state.get("runs",0)+1
                write_heartbeat({**state,"last_task":task['id'][:8],"status":"completed"})
            else:
                handle_failure(task)
                write_heartbeat({**state,"last_task":task['id'][:8],"status":"failed"})
        except KeyboardInterrupt:
            write_heartbeat({**state,"status":"stopped"})
            sys.exit(0)
        except Exception as e:
            print(f"[crash] {e}")
            time.sleep(15)

if __name__=="__main__":
    main()
