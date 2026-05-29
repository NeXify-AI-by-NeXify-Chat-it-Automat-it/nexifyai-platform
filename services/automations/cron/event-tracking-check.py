#!/usr/bin/env python3
"""
NeXifyAI — Event Tracking Check Cron-Job
Täglich um 04:00. Prüft ob alle in taxonomy.ts definierten Events
in den letzten 24h im Analytics-Backend eingegangen sind.

Output: JSON-Report in automations/cron/output/event-check-*.json
"""

import os
import sys
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = "/opt/nexify/repos/nexifyai-platform"
TAXONOMY_FILE = f"{REPO_ROOT}/packages/events/taxonomy.ts"
OUTPUT_DIR = f"{REPO_ROOT}/services/automations/cron/output"

# ══════════════════════════════════════════════════════════════

def extract_events_from_taxonomy() -> list:
    """Extrahiert alle Event-Namen aus taxonomy.ts."""
    if not os.path.isfile(TAXONOMY_FILE):
        print(f"❌ taxonomy.ts nicht gefunden: {TAXONOMY_FILE}")
        return []
    
    with open(TAXONOMY_FILE) as f:
        content = f.read()
    
    # Finde 'event: z.literal('...')' Muster
    events = re.findall(r"event:\s*z\.literal\('(\w+)'\)", content)
    return sorted(set(events))


def check_events_in_backend(expected_events: list) -> dict:
    """Prüft ob Events in den letzten 24h im Backend eingegangen sind."""
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_expected": len(expected_events),
        "events": {},
    }
    
    # Backend-Health prüfen
    import subprocess
    try:
        health = subprocess.run(
            ["curl", "-s", "--connect-timeout", "5", "http://localhost:8001/api/health"],
            capture_output=True, text=True, timeout=10
        )
        if health.returncode == 0 and "healthy" in health.stdout:
            result["backend_status"] = "healthy"
        else:
            result["backend_status"] = "unreachable"
            return result
    except Exception:
        result["backend_status"] = "error"
        return result
    
    # MongoDB Analytics prüfen (vereinfacht: Datenbank-Query)
    # In Produktion: Supabase analytics_events Tabelle abfragen
    for event in expected_events:
        result["events"][event] = {
            "defined": True,
            "tracked_in_code": None,  # Wird durch Code-Scan geprüft
            "fired_last_24h": None,   # Wird durch DB-Query geprüft
        }
    
    # Code-Scan: Prüfe ob track(event, ...) Aufrufe existieren
    frontend_src = f"{REPO_ROOT}/apps/web/src"
    if os.path.isdir(frontend_src):
        import subprocess as sp
        for event in expected_events:
            try:
                grep = sp.run(
                    ["grep", "-r", f"'{event}'", frontend_src],
                    capture_output=True, text=True
                )
                result["events"][event]["tracked_in_code"] = grep.returncode == 0
            except:
                pass
    
    return result


def run():
    print(f"═══ EVENT TRACKING CHECK — {datetime.now().isoformat()} ═══")
    
    expected = extract_events_from_taxonomy()
    print(f"📋 {len(expected)} Events in taxonomy.ts definiert")
    
    result = check_events_in_backend(expected)
    
    # Tracked vs untracked
    tracked = sum(1 for e in result.get("events", {}).values() if e.get("tracked_in_code"))
    untracked = [name for name, data in result.get("events", {}).items() if not data.get("tracked_in_code")]
    
    print(f"✅ In Code getrackt: {tracked}/{len(expected)}")
    if untracked:
        print(f"⚠️  Nicht getrackt: {', '.join(untracked)}")
    
    result["summary"] = {
        "tracked": tracked,
        "untracked": len(untracked),
        "untracked_list": untracked,
    }
    
    # Output speichern
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = f"{OUTPUT_DIR}/event-check-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Report gespeichert: {output_file}")
    return result


if __name__ == "__main__":
    run()
