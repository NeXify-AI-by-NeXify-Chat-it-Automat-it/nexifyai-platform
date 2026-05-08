#!/usr/bin/env python3
"""NeXifyAI Task Generator — Konsolidiert Luecken-Scan, Brain-Sync, Health-Score, Connection-Health zu Tasks."""
import subprocess, json, sys, os
from datetime import datetime, timezone

PSQL = ["docker","exec","supabase-db","psql","-U","postgres","-d","postgres","-t","-c"]

def create_task(title, description, priority, source, rice_score=50):
    subprocess.run(PSQL + [
        f"INSERT INTO public.tasks (title,description,status,priority,source,autopilot,rice_score,max_retries) "
        f"VALUES ($${title}$$,$${description}$$,'waiting','{priority}','{source}',true,{rice_score},3)"
    ], capture_output=True, timeout=10)

def from_health_score():
    try:
        r = subprocess.run(["python3","/opt/nexifyai-website-sicherheitskopie/automations/cron/health-score.py"],
                           capture_output=True,text=True,timeout=30)
        for line in r.stdout.split("\n"):
            if "score" in line and "%" in line:
                score = float(line.split(":")[0].strip().split()[-1].replace("%","").strip())
                if score < 75:
                    create_task(f"Health-Score kritisch: {score}%",
                                f"Score unter 75%. Automatische Diagnose erforderlich. Letzter Wert: {score}%.",
                                "critical", "health-score-monitor", 95)
    except: pass

def from_connection_health():
    try:
        r = subprocess.run(["python3","/opt/nexifyai-website-sicherheitskopie/automations/cron/connection-health-check.py"],
                           capture_output=True,text=True,timeout=30)
        for line in r.stdout.split("\n"):
            if "❌" in line and line.strip().startswith("❌"):
                name = line.strip().split(maxsplit=1)[1] if len(line.strip().split())>1 else "unknown"
                create_task(f"Verbindung ausgefallen: {name[:60]}",
                            f"Connection-Health-Check hat einen Fehler bei {name} erkannt.",
                            "high", "connection-health-check", 80)
    except: pass

def from_luecken_scan():
    r = subprocess.run(["python3","/opt/nexifyai-website-sicherheitskopie/automations/cron/dos-compliance-check.py","--lueckenscan"],
                       capture_output=True,text=True,timeout=30)
    for line in r.stdout.split("\n"):
        if "❌" in line:
            create_task(f"Luecke: {line.strip()[:80]}", line.strip()[:200], "medium", "luecken-scan", 60)

def from_brain_sync():
    brain_db = "/opt/data/brain/brain.db"
    if not os.path.isfile(brain_db):
        create_task("Brain-DB fehlt", "/opt/data/brain/brain.db nicht gefunden.", "high", "brain-sync", 85)

def main():
    print(f"[task-gen] {datetime.now(timezone.utc).isoformat()}")
    from_health_score()
    from_connection_health()
    from_luecken_scan()
    from_brain_sync()
    print("[task-gen] done")

if __name__ == "__main__":
    main()
