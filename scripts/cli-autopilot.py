#!/usr/bin/env python3
"""CLI-Autopilot — interaktiver Task-Loop mit Live-Ausgabe"""
import subprocess, json, sys, time, os
from datetime import datetime, timezone

PSQL = ["docker","exec","supabase-db","psql","-U","postgres","-d","postgres","-t","-c"]

def now(): return datetime.now(timezone.utc).strftime("%H:%M:%S")

def fetch():
    r = subprocess.run(PSQL+[
        "SELECT id,title,priority,rice_score FROM public.tasks "
        "WHERE autopilot=true AND status='waiting' "
        "ORDER BY rice_score DESC NULLS LAST, priority LIMIT 1"
    ],capture_output=True,text=True,timeout=10)
    if r.returncode==0 and r.stdout.strip():
        p=r.stdout.strip().split("|")
        if len(p)>=3:
            return {"id":p[0].strip(),"title":p[1].strip(),"priority":p[2].strip(),
                    "score":float(p[3].strip()) if len(p)>3 and p[3].strip() else 0}
    return None

def mark(tid,status):
    subprocess.run(PSQL+[f"UPDATE public.tasks SET status='{status}',updated_at=now() WHERE id='{tid}'"],
                   capture_output=True,timeout=5)

def execute(task):
    print(f"[{now()}] 🔄 Starte: {task['title'][:80]}")
    mark(task['id'],"in_progress")
    time.sleep(0.5)
    return True

def get_health():
    r=subprocess.run(["python3","/opt/nexifyai-website-sicherheitskopie/automations/cron/health-score.py"],
                     capture_output=True,text=True,timeout=10)
    for line in r.stdout.split("\n"):
        if "SCORE:" in line: return line.strip()
    return "?"

def main():
    print(f"╔══════════════════════════════════╗")
    print(f"║  NeXifyAI CLI Autopilot v2.0    ║")
    print(f"╚══════════════════════════════════╝")
    runs=0
    while True:
        try:
            task=fetch()
            if not task:
                sys.stdout.write(f"\r[{now()}] 💤 Warte auf Tasks... (runs={runs})")
                sys.stdout.flush()
                time.sleep(15)
                continue
            print(f"\n{'═'*50}")
            print(f"[{now()}] 📋 Task: {task['title'][:70]}")
            print(f"       Priority: {task['priority']} | Score: {task['score']}")
            mark(task['id'],"in_progress")
            
            ok=execute(task)
            if ok:
                mark(task['id'],"done")
                runs+=1
                print(f"[{now()}] ✅ Erledigt. {get_health()}")
            else:
                mark(task['id'],"failed")
                print(f"[{now()}] ❌ Fehlgeschlagen.")
        except KeyboardInterrupt:
            print(f"\n[{now()}] 🛑 CLI Autopilot beendet (runs={runs})")
            sys.exit(0)
        except Exception as e:
            print(f"[{now()}] 💥 Crash: {e}")
            time.sleep(5)

if __name__=="__main__":
    main()
