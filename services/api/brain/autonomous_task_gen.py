"""
NeXifyAI — Autonomous Task Generator (REAL v2.0)
Generates tasks from: file system analysis, health-score output, brain.db data.

All scanners now use REAL data sources. No `pass` stubs.
"""

import os
import json
import sqlite3
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class TaskSource(Enum):
    ERROR = "error"
    CI_FAILURE = "ci_failure"
    BRAIN_GAP = "brain_gap"
    ADR_CONFLICT = "adr_conflict"
    MISSING_TEST = "missing_test"
    SECURITY = "security"
    HEALTH_DEVIATION = "health_deviation"
    ARCHITECTURE_VIOLATION = "architecture_violation"
    DEPENDENCY_OUTDATED = "dependency_outdated"


class TaskPriority(Enum):
    P0_CRITICAL = 0
    P1_HIGH = 1
    P2_MEDIUM = 2
    P3_LOW = 3
    P4_NICE_TO_HAVE = 4


@dataclass
class GeneratedTask:
    title: str
    description: str
    source: TaskSource
    priority: TaskPriority
    affected_system: str
    evidence: str
    suggested_fix: Optional[str] = None
    related_docs: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    rice_score: int = 0


REPO_ROOT = "/opt/nexify/repos/nexifyai-platform"
BRAIN_DB = "/opt/data/brain/brain.db"
HEALTH_SCRIPT = f"{REPO_ROOT}/automations/cron/health-score.py"


class TaskGenerator:

    def __init__(self):
        self.tasks: List[GeneratedTask] = []

    def scan_and_generate(self) -> List[GeneratedTask]:
        self.tasks = []
        self._scan_errors()
        self._scan_brain_gaps()
        self._scan_missing_tests()
        self._scan_health()
        return self.tasks

    # ══════════════════════════════════════════
    # REAL SCANNERS
    # ══════════════════════════════════════════

    def _scan_errors(self):
        """Scan health-score script output for backend/connection failures."""
        try:
            if not os.path.exists(HEALTH_SCRIPT):
                return

            result = subprocess.run(
                ["python3", HEALTH_SCRIPT],
                capture_output=True, text=True, timeout=15
            )
            output = result.stdout + result.stderr

            if "backend_alive\": false" in output.lower() or "uptime: 0.0%" in output.lower():
                self.tasks.append(GeneratedTask(
                    title="Backend nicht erreichbar",
                    description="Health-Score zeigt backend_alive=false. Backend-Service prüfen und neu starten.",
                    source=TaskSource.ERROR,
                    priority=TaskPriority.P0_CRITICAL,
                    affected_system="backend",
                    evidence="health-score.py: backend_alive: false",
                    suggested_fix="VPS-SSH: systemctl restart nexifyai-backend.service",
                    rice_score=95,
                ))

            for line in output.split("\n"):
                if "❌" in line and "fehlgeschlagen" in line:
                    self.tasks.append(GeneratedTask(
                        title=f"Connection down: {line.strip()[:80]}",
                        description="Connection-Health-Check zeigt Ausfall. Verbindung prüfen.",
                        source=TaskSource.ERROR,
                        priority=TaskPriority.P2_MEDIUM,
                        affected_system="infrastructure",
                        evidence=line.strip(),
                        rice_score=60,
                    ))

        except Exception as e:
            print(f"[task_gen] Error scan failed: {e}")

    def _scan_brain_gaps(self):
        """Scan filesystem for missing docs, ADRs, policies."""
        required_docs = [
            "docs/DOS-v2.0.md",
            "docs/leitfassung-v1.0.md",
            "docs/architecture/zielarchitektur-v2.md",
            "docs/architecture/bauplan.md",
            "docs/governance/raci.yaml",
            "docs/policies/vulnerability-policy.md",
            "docs/policies/license-policy.md",
        ]

        for doc in required_docs:
            full_path = os.path.join(REPO_ROOT, doc)
            if not os.path.exists(full_path):
                self.tasks.append(GeneratedTask(
                    title=f"Dokumentation fehlt: {doc}",
                    description=f"Erstelle {doc}. Wichtiges Dokument für DOS-Compliance.",
                    source=TaskSource.BRAIN_GAP,
                    priority=TaskPriority.P2_MEDIUM,
                    affected_system="documentation",
                    evidence=f"Datei nicht gefunden: {full_path}",
                    rice_score=50,
                ))

        # Check ADR gaps
        adrs_dir = os.path.join(REPO_ROOT, "docs/adrs")
        if os.path.exists(adrs_dir):
            existing = [f for f in os.listdir(adrs_dir) if f.startswith("ADR-") and f.endswith(".md")]
            required_adrs = ["005", "006", "007", "008", "009"]
            for num in required_adrs:
                if not any(num in f for f in existing):
                    self.tasks.append(GeneratedTask(
                        title=f"ADR-{num} fehlt",
                        description=f"Erstelle ADR-{num}. Architekturentscheidung muss dokumentiert werden.",
                        source=TaskSource.BRAIN_GAP,
                        priority=TaskPriority.P3_LOW,
                        affected_system="documentation",
                        evidence=f"Keine ADR mit Nummer {num} in {adrs_dir}",
                        rice_score=40,
                    ))

        # Check brain.db size/health
        if os.path.exists(BRAIN_DB):
            try:
                conn = sqlite3.connect(BRAIN_DB)
                count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                conn.close()
                if count < 100:
                    self.tasks.append(GeneratedTask(
                        title="Brain-Wissensbasis klein",
                        description=f"Nur {count} Einträge in brain.db memories. Brain-Pipeline aktivieren.",
                        source=TaskSource.BRAIN_GAP,
                        priority=TaskPriority.P3_LOW,
                        affected_system="brain",
                        evidence=f"memories table: {count} rows",
                        rice_score=35,
                    ))
            except Exception:
                pass

    def _scan_missing_tests(self):
        """Compare backend source files against test files."""
        backend_dir = os.path.join(REPO_ROOT, "services/api")
        test_dir = os.path.join(backend_dir, "tests")

        if not os.path.exists(backend_dir) or not os.path.exists(test_dir):
            self.tasks.append(GeneratedTask(
                title="Testverzeichnis fehlt",
                description="backend/tests/ existiert nicht. Testsystem aufbauen.",
                source=TaskSource.MISSING_TEST,
                priority=TaskPriority.P1_HIGH,
                affected_system="backend",
                evidence=f"Verzeichnis fehlt: {test_dir}",
                rice_score=75,
            ))
            return

        source_files = set()
        for root, _, files in os.walk(backend_dir):
            if 'tests' in root or 'migrations' in root or '__pycache__' in root:
                continue
            for f in files:
                if f.endswith('.py') and not f.startswith('__'):
                    # Convert: agents/security_agent.py -> test_security_agent
                    rel = os.path.relpath(os.path.join(root, f), backend_dir)
                    source_files.add(rel.replace('/', '_').replace('.py', ''))

        test_files = set()
        for root, _, files in os.walk(test_dir):
            for f in files:
                if f.startswith('test_') and f.endswith('.py'):
                    test_files.add(f.replace('test_', '').replace('.py', ''))

        missing = source_files - test_files
        if len(missing) > 0:
            top_missing = sorted(missing)[:5]
            self.tasks.append(GeneratedTask(
                title=f"{len(missing)} Module ohne Tests",
                description=f"Fehlende Tests für: {', '.join(top_missing)}...",
                source=TaskSource.MISSING_TEST,
                priority=TaskPriority.P1_HIGH,
                affected_system="backend",
                evidence=f"{len(missing)}/{len(source_files)} Module ungetestet",
                suggested_fix="pytest tests/test_<module>.py für jedes Modul erstellen",
                rice_score=75,
            ))

    def _scan_health(self):
        """Parse health-score.py for real metrics."""
        try:
            if not os.path.exists(HEALTH_SCRIPT):
                return

            result = subprocess.run(
                ["python3", HEALTH_SCRIPT],
                capture_output=True, text=True, timeout=15
            )
            output = result.stdout + result.stderr

            for line in output.split("\n"):
                if "HEALTH SCORE:" in line:
                    try:
                        score_str = line.split("HEALTH SCORE:")[1].split("%")[0].strip()
                        score = float(score_str)
                        if score < 50:
                            self.tasks.append(GeneratedTask(
                                title=f"Health-Score CRITICAL: {score}%",
                                description=f"System Health bei {score}%. Sofortmaßnahmen erforderlich.",
                                source=TaskSource.HEALTH_DEVIATION,
                                priority=TaskPriority.P0_CRITICAL,
                                affected_system="infrastructure",
                                evidence=line.strip(),
                                rice_score=95,
                            ))
                        elif score < 70:
                            self.tasks.append(GeneratedTask(
                                title=f"Health-Score DEGRADED: {score}%",
                                description=f"System Health bei {score}%. Komponenten prüfen.",
                                source=TaskSource.HEALTH_DEVIATION,
                                priority=TaskPriority.P1_HIGH,
                                affected_system="infrastructure",
                                evidence=line.strip(),
                                rice_score=70,
                            ))
                    except ValueError:
                        pass
        except Exception as e:
            print(f"[task_gen] Health scan failed: {e}")

    def to_supabase(self) -> List[Dict]:
        return [
            {
                "title": t.title,
                "context": t.description,
                "source": t.source.value,
                "priority": t.priority.name.lower(),
                "affected_systems": t.affected_system,
                "rice_score": t.rice_score,
                "status": "waiting",
                "relevant_docs": json.dumps(t.related_docs),
                "forbidden": json.dumps(["Stripe", "MiniMax", "Goose"]),
                "model_policy": "deepseek-v4-flash",
            }
            for t in self.tasks
        ]
