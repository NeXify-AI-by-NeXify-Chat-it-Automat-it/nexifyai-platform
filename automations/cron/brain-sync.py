#!/usr/bin/env python3
"""
NeXifyAI — Brain Sync Cron-Job
Läuft alle 30 Minuten. Gleicht Open Notebook, Qdrant und Brain DB
mit aktuellen Repo-Daten und DOS-Dokument ab.

Installation:
  */30 * * * * python3 /opt/nexifyai-website-sicherheitskopie/automations/cron/brain-sync.py
"""

import os
import sys
import json
import subprocess
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BRAIN_DB = "/opt/data/brain/brain.db"
REPO_ROOT = "/opt/nexifyai-website-sicherheitskopie"
OUTPUT_DIR = f"{REPO_ROOT}/automations/cron/output"

def sync_dos_to_brain():
    """Synchronisiert DOS v2.0 Kapitel-Struktur ins Brain."""
    dos_file = f"{REPO_ROOT}/docs/DOS-v2.0.md"
    if not os.path.isfile(dos_file):
        print("❌ DOS v2.0 nicht gefunden")
        return False

    with open(dos_file) as f:
        content = f.read()

    # Extrahiere Kapitel
    chapters = []
    for line in content.split("\n"):
        if line.startswith("## "):
            chapters.append(line.strip("# ").strip())

    print(f"📋 {len(chapters)} DOS-Kapitel identifiziert")

    # Ins Brain schreiben
    if os.path.isfile(BRAIN_DB):
        try:
            conn = sqlite3.connect(BRAIN_DB)
            cursor = conn.cursor()
            # Tabelle anlegen falls nicht vorhanden
            cursor.execute("CREATE TABLE IF NOT EXISTS memories (id TEXT PRIMARY KEY, content TEXT, category TEXT, source TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)")
            cursor.execute("""
                INSERT OR REPLACE INTO memories (id, content, category, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "dos_v2_chapters",
                json.dumps({"chapters": chapters, "count": len(chapters), "timestamp": datetime.now(timezone.utc).isoformat()}),
                "governance",
                "brain-sync-cron",
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            conn.close()
            print("✅ DOS-Struktur ins Brain synchronisiert")
            return True
        except Exception as e:
            print(f"⚠️ Brain-Sync teilweise fehlgeschlagen: {e}")
            return False

    return False

def check_notebook():
    """Prüft ob Open Notebook erreichbar ist."""
    try:
        # MASTER-WIKI D5: Open Notebook Port 32770 (nicht 32774)
        # Open Notebook hat KEIN /api/health — prüfe /api/sources statt dessen
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "5", "http://localhost:32770/api/sources"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip().startswith("["):
            # Valide JSON-Array-Antwort — Notebook läuft
            try:
                sources = json.loads(result.stdout)
                embedded = sum(1 for s in sources if s.get("embedded"))
                total = len(sources)
                print(f"✅ Open Notebook erreichbar ({total} Quellen, {embedded} embedded)")
                if total > 0 and embedded == 0:
                    print("⚠️ Keine Quellen embedded — Embedding-Pipeline prüfen!")
                return True
            except json.JSONDecodeError:
                print(f"⚠️ Open Notebook antwortet, aber kein valides JSON: {result.stdout[:80]}")
                return False
        elif result.returncode == 0:
            print(f"⚠️ Open Notebook unerwartete Antwort: {result.stdout[:100]}")
            return False
        else:
            print("⚠️ Open Notebook nicht erreichbar")
            return False
    except Exception as e:
        print(f"⚠️ Open Notebook Fehler: {e}")
        return False

def check_repo_integrity():
    """Prüft ob alle DOS-Pflichtverzeichnisse im Repo existieren."""
    required = [
        "docs", "docs/adrs", "docs/governance", "docs/policies",
        "packages", "packages/events", "packages/config",
        "ops", "ops/policies",
        "automations", "automations/serverless", "automations/cron"
    ]

    missing = []
    for d in required:
        if not os.path.isdir(f"{REPO_ROOT}/{d}"):
            missing.append(d)

    if missing:
        print(f"❌ Fehlende Verzeichnisse: {', '.join(missing)}")
        return False
    else:
        print(f"✅ Alle {len(required)} Pflichtverzeichnisse vorhanden")
        return True

def run():
    print(f"═══ BRAIN SYNC — {datetime.now().isoformat()} ═══")

    success = True

    # 1. DOS → Brain
    if not sync_dos_to_brain():
        success = False

    # 2. Open Notebook Check
    check_notebook()

    # 3. Repo-Integrität
    if not check_repo_integrity():
        success = False

    # Output speichern
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = f"{OUTPUT_DIR}/brain-sync-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": success
        }, f)

    print(f"Sync abgeschlossen. {'✅ Erfolg' if success else '⚠️ Teilweise fehlgeschlagen'}")
    return success

if __name__ == "__main__":
    run()
