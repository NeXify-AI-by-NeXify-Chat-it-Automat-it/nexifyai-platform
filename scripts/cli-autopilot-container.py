#!/usr/bin/env python3
"""CLI Autopilot — Container-native, zeigt System-Status"""
import subprocess, time, os
from datetime import datetime

SSH = ["ssh","-i","/opt/data/ssh_keys/hermes_vps_key","-o","StrictHostKeyChecking=no","root@72.62.152.47"]

def now(): return datetime.now().strftime("%H:%M:%S")

def check_health():
    try:
        r = subprocess.run(SSH + ["python3 /opt/nexifyai-website-sicherheitskopie/automations/cron/health-score.py"],
                          capture_output=True,text=True,timeout=10)
        for l in r.stdout.split("\n"):
            if "SCORE:" in l: return l.strip()
    except: pass
    return "?"

def check_tasks():
    try:
        r = subprocess.run(SSH + ["docker exec supabase-db psql -U postgres -d postgres -t -c",
                           "SELECT status,count(*) FROM tasks GROUP BY status"],
                          capture_output=True,text=True,timeout=10)
        lines = [l.strip() for l in r.stdout.split("\n") if "|" in l]
        return " ".join(lines[-6:])[:100]
    except: return "?"

def main():
    print(f"╔══════════════════════════════════╗")
    print(f"║  NeXifyAI Autopilot (Container)  ║")
    print(f"╚══════════════════════════════════╝")
    tick = 0
    while True:
        try:
            tick += 1
            health = check_health()
            tasks = check_tasks()
            status_line = f"[{now()}] Tick #{tick} | {health or '...'} | Tasks: {tasks or '...'}"
            sys.stdout.write(f"\r{status_line[:100]}")
            sys.stdout.flush()
            time.sleep(15)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped (ticks={tick})")
            sys.exit(0)
        except Exception as e:
            print(f"[{now()}] 💥 {e}")
            time.sleep(5)

import sys
if __name__=="__main__":
    main()
