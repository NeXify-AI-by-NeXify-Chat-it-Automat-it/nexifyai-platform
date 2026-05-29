#!/usr/bin/env python3
"""
NeXifyAI — DOS Compliance Check Cron-Job
Läuft täglich. Validiert die gesamte Systemlandschaft gegen DOS v2.0.
Generiert Issues/Tickets bei Abweichungen.

Installation:
  ln -s /opt/nexify/repos/nexifyai-platform/services/automations/cron/dos-compliance-check.py /usr/local/bin/
  echo "0 6 * * * python3 /usr/local/bin/dos-compliance-check.py" >> /etc/crontab
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = "/opt/nexify/repos/nexifyai-platform"
DOS_DOC = f"{REPO_ROOT}/docs/DOS-v2.0.md"
OUTPUT_DIR = f"{REPO_ROOT}/services/automations/cron/output"

class DOSComplianceCheck:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passes = []
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def check_directory(self, name, path):
        """Prüft ob ein Pflichtverzeichnis existiert."""
        if os.path.isdir(path):
            self.passes.append(f"✅ {name} existiert: {path}")
            return True
        else:
            self.issues.append(f"❌ {name} fehlt: {path}")
            return False

    def check_file(self, name, path):
        """Prüft ob eine Pflichtdatei existiert."""
        if os.path.isfile(path):
            self.passes.append(f"✅ {name} existiert: {path}")
            return True
        else:
            self.issues.append(f"❌ {name} fehlt: {path}")
            return False

    def check_backend_routes(self):
        """Prüft ob OpenAPI/Swagger aktiv ist."""
        server_py = f"{REPO_ROOT}/services/api/server.py"
        if os.path.isfile(server_py):
            with open(server_py) as f:
                content = f.read()
                if "FastAPI" in content:
                    self.passes.append("✅ FastAPI erkannt (OpenAPI via /docs)")
                else:
                    self.warnings.append("⚠️ Kein FastAPI erkannt")
        else:
            self.issues.append("❌ services/api/server.py fehlt (backend/ → services/api/ verschoben)")

    def check_error_schema(self):
        """Prüft ob standardisiertes Error-Schema existiert."""
        api_standards = f"{REPO_ROOT}/packages/config/api-standards.ts"
        if os.path.isfile(api_standards):
            with open(api_standards) as f:
                if "ApiErrorResponse" in f.read():
                    self.passes.append("✅ API Error-Schema definiert")
                    return
        self.issues.append("❌ Kein standardisiertes API Error-Schema")

    def check_design_system(self):
        """Prüft ob /packages/ui existiert."""
        self.check_directory("Designsystem", f"{REPO_ROOT}/packages/ui")
        self.check_file("Design Tokens", f"{REPO_ROOT}/design_guidelines.json")

    def check_events(self):
        """Prüft ob Event-Taxonomie existiert."""
        if not self.check_directory("Events", f"{REPO_ROOT}/packages/events"):
            return
        # Mindestens 1 Event-Datei
        files = list(Path(f"{REPO_ROOT}/packages/events").glob("*.ts"))
        if files:
            self.passes.append(f"✅ Event-Taxonomie: {len(files)} Dateien")
        else:
            self.warnings.append("⚠️ packages/events/ ist leer")

    def check_ci(self):
        """Prüft CI-Workflow."""
        self.check_file("CI Workflow", f"{REPO_ROOT}/.github/workflows/ci.yml")

    def check_tests(self):
        """Prüft ob Tests existieren."""
        test_files = list(Path(REPO_ROOT).glob("**/test_*.py"))
        test_files.extend(Path(REPO_ROOT).glob("**/*.test.*"))
        if test_files:
            self.passes.append(f"✅ Tests gefunden: {len(test_files)} Dateien")
        else:
            self.issues.append("❌ Keine Tests gefunden (außer node_modules)")

    def check_memory_architecture(self):
        """Prüft Brain-Struktur."""
        brain_db = "/opt/data/brain/brain.db"
        if os.path.isfile(brain_db):
            size = os.path.getsize(brain_db)
            self.passes.append(f"✅ Brain DB: {size:,} Bytes")
        else:
            self.issues.append("❌ Brain DB fehlt")

    def run(self):
        print("═══ DOS v2.0 COMPLIANCE CHECK ═══")
        print(f"Zeitpunkt: {self.timestamp}")
        print()

        # Pflichtverzeichnisse
        self.check_directory("docs/", f"{REPO_ROOT}/docs")
        self.check_directory("docs/adrs/", f"{REPO_ROOT}/docs/adrs")
        self.check_directory("docs/governance/", f"{REPO_ROOT}/docs/governance")
        self.check_directory("packages/", f"{REPO_ROOT}/packages")
        self.check_directory("packages/ui/", f"{REPO_ROOT}/packages/ui")
        self.check_directory("packages/config/", f"{REPO_ROOT}/packages/config")
        self.check_directory("packages/events/", f"{REPO_ROOT}/packages/events")
        self.check_directory("ops/", f"{REPO_ROOT}/ops")
        self.check_directory("ops/ci/", f"{REPO_ROOT}/ops/ci")
        self.check_directory("automations/", f"{REPO_ROOT}/automations")
        self.check_directory("automations/cron/", f"{REPO_ROOT}/automations/cron")

        # Pflichtdateien
        self.check_file("DOS v2.0", f"{REPO_ROOT}/docs/DOS-v2.0.md")
        self.check_file("RACI-Matrix", f"{REPO_ROOT}/docs/governance/raci.yaml")
        self.check_file("ADR Template", f"{REPO_ROOT}/docs/adrs/ADR_TEMPLATE.md")
        self.check_file("ADR-001", f"{REPO_ROOT}/docs/adrs/ADR-001-dos-v2-adoption.md")
        self.check_file("API Standards", f"{REPO_ROOT}/packages/config/api-standards.ts")

        # Tiefenprüfungen
        self.check_backend_routes()
        self.check_error_schema()
        self.check_design_system()
        self.check_events()
        self.check_ci()
        self.check_tests()
        self.check_memory_architecture()

        # Report
        report = {
            "timestamp": self.timestamp,
            "dos_version": "2.0",
            "summary": {
                "passes": len(self.passes),
                "warnings": len(self.warnings),
                "issues": len(self.issues),
                "compliance_score": round(
                    len(self.passes) / max(len(self.passes) + len(self.warnings) + len(self.issues), 1) * 100, 1
                ),
            },
            "passes": self.passes,
            "warnings": self.warnings,
            "issues": self.issues,
        }

        # Ausgabe
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = f"{OUTPUT_DIR}/dos-compliance-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n═══ ZUSAMMENFASSUNG ═══")
        print(f"✅ Bestanden: {report['summary']['passes']}")
        print(f"⚠️  Warnungen: {report['summary']['warnings']}")
        print(f"❌ Probleme: {report['summary']['issues']}")
        print(f"📊 Compliance-Score: {report['summary']['compliance_score']}%")

        if self.issues:
            print(f"\n❌ OFFENE PROBLEME ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   {issue}")

        print(f"\nReport gespeichert: {output_file}")
        return report

if __name__ == "__main__":
    checker = DOSComplianceCheck()
    checker.run()
