"""
NeXifyAI — Autonomous Task Generator
Generates tasks from: errors, logs, CI failures, brain gaps, ADR conflicts,
missing tests, security issues, health deviations, architecture violations.

Usage:
    from backend.brain.autonomous_task_gen import TaskGenerator
    gen = TaskGenerator()
    tasks = gen.scan_and_generate()
"""

import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
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
    """Auto-generated task from system analysis."""
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


# ══════════════════════════════════════════════
# TASK GENERATOR
# ══════════════════════════════════════════════

class TaskGenerator:
    """
    Autonomous task generator.
    Scans system state and produces actionable tasks.
    """
    
    def __init__(self):
        self.tasks: List[GeneratedTask] = []
    
    def scan_and_generate(self) -> List[GeneratedTask]:
        """Run all scanners and return generated tasks."""
        self.tasks = []
        
        self._scan_errors()
        self._scan_ci_failures()
        self._scan_brain_gaps()
        self._scan_missing_tests()
        self._scan_security()
        self._scan_health()
        
        return self.tasks
    
    # ══════════════════════════════════════════
    # SCANNERS
    # ══════════════════════════════════════════
    
    def _scan_errors(self):
        """Scan error logs for patterns."""
        try:
            # Check backend error logs
            # TODO: Integrate with Sentry/logging
            pass
        except Exception as e:
            print(f"[task_gen] Error scan failed: {e}")
    
    def _scan_ci_failures(self):
        """Check GitHub Actions for failed workflows."""
        try:
            # TODO: GitHub API integration
            # GET /repos/{owner}/{repo}/actions/runs?status=failure
            pass
        except Exception as e:
            print(f"[task_gen] CI scan failed: {e}")
    
    def _scan_brain_gaps(self):
        """
        Detect gaps in the Brain knowledge base:
        - Missing ADRs for architectural decisions
        - Undocumented incidents
        - Stale entries (>30 days without update)
        - Missing policy documents
        """
        required_adrs = [
            "automation-layer",
            "queue-system", 
            "observability",
            "agent-runtime",
            "event-bus",
        ]
        
        # Check which ADRs exist (placeholder)
        existing_adrs = []  # TODO: scan /docs/adrs/
        
        for adr in required_adrs:
            if adr not in existing_adrs:
                self.tasks.append(GeneratedTask(
                    title=f"ADR fehlt: {adr}",
                    description=f"Erstelle ADR für {adr}. Architekturentscheidung dokumentieren.",
                    source=TaskSource.BRAIN_GAP,
                    priority=TaskPriority.P2_MEDIUM,
                    affected_system="documentation",
                    evidence=f"ADR '{adr}' nicht in /docs/adrs/ gefunden",
                    rice_score=60,
                ))
    
    def _scan_missing_tests(self):
        """
        Detect code without tests.
        Compares source files against test files.
        """
        try:
            import os
            backend_dir = "backend"
            test_dir = "backend/tests"
            
            if os.path.exists(backend_dir) and os.path.exists(test_dir):
                source_files = set()
                test_files = set()
                
                for root, _, files in os.walk(backend_dir):
                    if 'tests' in root or 'migrations' in root:
                        continue
                    for f in files:
                        if f.endswith('.py') and not f.startswith('__'):
                            source_files.add(f.replace('.py', ''))
                
                for root, _, files in os.walk(test_dir):
                    for f in files:
                        if f.startswith('test_'):
                            test_files.add(f.replace('test_', '').replace('.py', ''))
                
                missing_tests = source_files - test_files
                if len(missing_tests) > 0:
                    self.tasks.append(GeneratedTask(
                        title=f"{len(missing_tests)} Module ohne Tests",
                        description=f"Füge Tests hinzu für: {', '.join(list(missing_tests)[:5])}",
                        source=TaskSource.MISSING_TEST,
                        priority=TaskPriority.P1_HIGH,
                        affected_system="backend",
                        evidence=f"Test-Coverage < 80%: {len(missing_tests)} ungetestete Module",
                        auto_fixable=False,
                        rice_score=75,
                    ))
        except Exception as e:
            print(f"[task_gen] Test scan failed: {e}")
    
    def _scan_security(self):
        """Check for security issues."""
        # TODO: Integrate with Gitleaks, Trivy, Dependabot results
        pass
    
    def _scan_health(self):
        """Check health score deviations."""
        try:
            # TODO: Check health-score.py output
            # If < 70 → P0_CRITICAL task
            pass
        except Exception as e:
            print(f"[task_gen] Health scan failed: {e}")
    
    # ══════════════════════════════════════════
    # OUTPUT
    # ══════════════════════════════════════════
    
    def to_supabase(self) -> List[Dict]:
        """Convert tasks to Supabase INSERT format."""
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
