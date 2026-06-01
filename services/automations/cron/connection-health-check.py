#!/usr/bin/env python3
"""
NeXifyAI — Connection Health Check
Läuft täglich 05:00 UTC via VPS-Cron.
Testet jede Verbindung mit minimalem API-Call.
Ergebnis in connection-inventory.md loggen.
Bei Fehler: SEV3-Incident + Selbstheilungsversuch.
"""
import json, subprocess, sys, os
from datetime import datetime, timezone
from pathlib import Path

INVENTORY_FILE = "/opt/nexifyai-website-sicherheitskopie/docs/infrastructure/connection-inventory.md"

CHECKS = [
    {
        "name": "GitHub",
        "cmd": ["ssh", "-T", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10", "git@github.com"],
        "expect": "successfully authenticated",
        "sev": "SEV1",
        "fallback": "git push origin dry-run"
    },
    {
        "name": "VPS",
        "cmd": ["hostname"],
        "expect": "nexifyai",
        "sev": "SEV0",
        "fallback": "systemctl is-active nexifyai-backend"
    },
    {
        "name": "Supabase",
        "cmd": ["psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-c", "SELECT 1"],
        "expect": "1",
        "sev": "SEV1",
        "fallback": "docker exec supabase-db pg_isready"
    },
    {
        "name": "NeXify AI/OpenRouter",
        "cmd": ["curl", "-s", "--connect-timeout", "10", "-H", f"Authorization: Bearer {os.environ.get('OPENROUTER_API_KEY','')}", "https://openrouter.ai/api/v1/models"],
        "expect": "id",
        "sev": "SEV1",
        "fallback": None
    },
    {
        "name": "Vercel",
        "cmd": ["curl", "-s", "--connect-timeout", "10", "-H", f"Authorization: Bearer {os.environ.get('VERCEL_TOKEN','')}", "https://api.vercel.com/v5/user"],
        "expect": "user",
        "sev": "SEV2",
        "fallback": None
    },
    {
        "name": "Umami",
        "cmd": ["curl", "-s", "--connect-timeout", "10", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8088"],
        "expect": "200",
        "sev": "SEV3",
        "fallback": "docker restart umami"
    },
    {
        "name": "Resend",
        "cmd": ["curl", "-s", "--connect-timeout", "10", "-H", f"Authorization: Bearer {os.environ.get('RESEND_API_KEY','')}", "https://api.resend.com/emails"],
        "expect": "data",
        "sev": "SEV2",
        "fallback": None
    },
    {
        "name": "Traefik",
        "cmd": ["curl", "-s", "--connect-timeout", "10", "-o", "/dev/null", "-w", "%{http_code}", "-H", "Host: mail.nexifyai.cloud", "http://localhost"],
        "expect": "301",
        "sev": "SEV1",
        "fallback": "docker restart traefik-tcja-traefik-1"
    },
]

def run_check(check: dict) -> dict:
    start = datetime.now(timezone.utc)
    success = False
    output = ""
    try:
        env = {**os.environ, "PGPASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres")}
        result = subprocess.run(check["cmd"], capture_output=True, text=True, timeout=15, env=env)
        output = (result.stdout + result.stderr)[:500]
        success = check["expect"].lower() in output.lower() or result.returncode == 0
    except Exception as e:
        output = str(e)[:500]
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    return {**check, "success": success, "output": output[:200], "duration_s": round(duration, 1), "timestamp": start.isoformat()}

def try_self_heal(check: dict) -> bool:
    """Versucht automatische Heilung per Fallback-Kommando."""
    fb = check.get("fallback")
    if not fb:
        return False
    try:
        print(f"  🔧 Selbstheilung: {fb}")
        result = subprocess.run(fb.split(), capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception:
        return False

def update_inventory(results: list):
    """Loggt Ergebnisse in die Inventar-Datei."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    # Kurzer Status in MD
    status_line = f"| {now} | " + " | ".join("✅" if r["success"] else "❌" for r in results) + f" | {int(passed/total*100)}% |"
    
    if os.path.isfile(INVENTORY_FILE):
        with open(INVENTORY_FILE) as f:
            content = f.read()
        if now not in content:
            pos = content.find("## Health-Check-Ergebnisse") + len("## Health-Check-Ergebnisse\n\n")
            header_end = content.find("|", pos)
            table_end = content.find("\n\n", header_end)
            if table_end > 0:
                new_content = content[:pos] + status_line + "\n" + content[table_end:]
                with open(INVENTORY_FILE, "w") as f:
                    f.write(new_content)
    
    return passed, total

def main():
    print(f"═══ Connection Health Check — {datetime.now(timezone.utc).isoformat()} ═══")
    results = []
    failures = []
    
    for check in CHECKS:
        r = run_check(check)
        results.append(r)
        icon = "✅" if r["success"] else "❌"
        print(f"{icon} {r['name']} ({r['duration_s']}s)")
        if not r["success"]:
            print(f"   Output: {r['output'][:100]}")
            # Selbstheilung
            healed = try_self_heal(r)
            r["healed"] = healed
            if healed:
                # Re-test
                r2 = run_check(check)
                results[-1] = r2
                print(f"   🔧 Nach Selbstheilung: {'✅' if r2['success'] else '❌'}")
            if not r.get("healed") or not r2.get("success", False):
                failures.append(r)
    
    passed, total = update_inventory(results)
    score = int(passed / total * 100)
    
    print(f"\n═══ RESULT: {passed}/{total} ({score}%) ═══")
    
    if failures:
        print(f"❌ {len(failures)} fehlgeschlagen:")
        for f in failures:
            print(f"   {f['name']}: {f['output'][:100]}")
        return 1
    else:
        print("✅ Alle Verbindungen OK")
        return 0

if __name__ == "__main__":
    sys.exit(main())
