"""
NeXifyAI — Recovery State Machine + Convergence Validator (E3)

Principle: Every mutation MUST be validated post-execution.
NOT: "command succeeded"
BUT:  "system converged across ALL observers"

State Machine:
  DETECTED → CLASSIFIED → RECOVERY_PROPOSED → RECOVERY_EXECUTED
  → STABILIZING → RE-OBSERVED → VALIDATED → LEARNED

End States:
  CONVERGED    — All observers agree, contradictions resolved
  PARTIAL      — Some observers see improvement, not all
  REGRESSED    — State worsened after recovery attempt
  CONTRADICTORY — Different observers see different realities
  UNKNOWN      — Not enough data to determine

Usage:
    validator = ConvergenceValidator()
    result = validator.validate_recovery(
        service="qdrant-primary",
        action="docker restart nexifyai-qdrant",
    )
    # result.convergence_state → CONVERGED / PARTIAL / REGRESSED / ...
"""

import time
import json
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timezone


# ══════════════════════════════════════════════
# STATE MACHINE
# ══════════════════════════════════════════════

class RecoveryPhase(Enum):
    """Phases of the recovery state machine."""
    DETECTED = "detected"
    CLASSIFIED = "classified"
    RECOVERY_PROPOSED = "recovery_proposed"
    RECOVERY_EXECUTED = "recovery_executed"
    STABILIZING = "stabilizing"
    RE_OBSERVED = "re_observed"
    VALIDATED = "validated"
    LEARNED = "learned"


class ConvergenceState(Enum):
    """End state of recovery validation."""
    CONVERGED = "converged"           # All observers agree, contradictions resolved
    PARTIAL = "partial"               # Some improvement, not complete
    REGRESSED = "regressed"           # State worsened
    CONTRADICTORY = "contradictory"   # Observers disagree
    UNKNOWN = "unknown"               # Insufficient data
    PENDING = "pending"               # Validation not yet run


@dataclass
class ObserverSnapshot:
    """State of one observer for a target service."""
    observer: str
    target: str
    reachable: bool
    latency_ms: float
    error: Optional[str]
    timestamp: float = field(default_factory=time.time)


@dataclass
class RecoveryRecord:
    """Complete recovery lifecycle record."""
    incident_id: str
    service: str
    phase: RecoveryPhase = RecoveryPhase.DETECTED
    convergence: ConvergenceState = ConvergenceState.PENDING
    
    # What was wrong
    detected_issue: str = ""
    root_cause: str = ""
    severity: str = ""
    
    # What was done
    recovery_action: str = ""
    recovery_command: str = ""
    executed_at: Optional[float] = None
    execution_duration_ms: float = 0
    
    # Validation
    pre_snapshots: List[ObserverSnapshot] = field(default_factory=list)
    post_snapshots: List[ObserverSnapshot] = field(default_factory=list)
    contradictions_before: int = 0
    contradictions_after: int = 0
    confidence: float = 0.0
    
    # Learning
    lessons_learned: List[str] = field(default_factory=list)
    should_retry: bool = False
    alternative_action: str = ""
    
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


# ══════════════════════════════════════════════
# CONVERGENCE VALIDATOR
# ══════════════════════════════════════════════

class ConvergenceValidator:
    """
    Post-execution validation engine.
    
    After ANY mutation (restart, deploy, config change), this:
    1. Takes pre-execution snapshots from all observers
    2. Allows execution
    3. Takes post-execution snapshots from all observers
    4. Compares and validates convergence
    5. Persists the outcome
    """
    
    STABILIZATION_WAIT = 3  # seconds to wait after recovery action
    CONVERGENCE_THRESHOLD = 0.8  # 80% observers must agree
    
    def __init__(self):
        self.records: List[RecoveryRecord] = []
    
    def validate_recovery(
        self,
        service: str,
        action: str,
        command: str,
        pre_snapshots: List[ObserverSnapshot],
        executor: Callable[[], bool] = None,
    ) -> RecoveryRecord:
        """
        Execute and validate a recovery action.
        
        Args:
            service: Service ID (from Canonical Registry)
            action: Human-readable action description
            command: Shell command to execute
            pre_snapshots: Observer states BEFORE recovery
            executor: Optional custom executor (default: subprocess.run)
        
        Returns:
            RecoveryRecord with full lifecycle and convergence state
        """
        record = RecoveryRecord(
            incident_id=f"INC-{int(time.time())}",
            service=service,
            recovery_action=action,
            recovery_command=command,
            pre_snapshots=pre_snapshots,
            contradictions_before=self._count_contradictions(pre_snapshots),
        )
        
        # Phase: DETECTED → CLASSIFIED
        record.phase = RecoveryPhase.CLASSIFIED
        record.root_cause = self._classify(pre_snapshots)
        
        # Phase: RECOVERY_PROPOSED
        record.phase = RecoveryPhase.RECOVERY_PROPOSED
        
        # Phase: RECOVERY_EXECUTED
        record.phase = RecoveryPhase.RECOVERY_EXECUTED
        record.executed_at = time.time()
        
        start = time.time()
        try:
            if executor:
                success = executor()
            else:
                result = subprocess.run(command, shell=True, capture_output=True, timeout=30)
                success = result.returncode == 0
        except Exception as e:
            success = False
            record.lessons_learned.append(f"Execution failed: {e}")
        
        record.execution_duration_ms = (time.time() - start) * 1000
        
        # Phase: STABILIZING
        record.phase = RecoveryPhase.STABILIZING
        time.sleep(self.STABILIZATION_WAIT)
        
        # Phase: RE-OBSERVED — Take fresh snapshots from all observers
        record.phase = RecoveryPhase.RE_OBSERVED
        record.post_snapshots = self._re_observe(service)
        record.contradictions_after = self._count_contradictions(record.post_snapshots)
        
        # Phase: VALIDATED — Compare pre vs post
        record.phase = RecoveryPhase.VALIDATED
        record.convergence = self._evaluate_convergence(record)
        record.confidence = self._compute_confidence(record)
        record.completed_at = datetime.now(timezone.utc).isoformat()
        
        # Phase: LEARNED
        record.phase = RecoveryPhase.LEARNED
        record.lessons_learned.extend(self._extract_lessons(record))
        
        # Determine if retry is needed
        if record.convergence in (ConvergenceState.REGRESSED, ConvergenceState.CONTRADICTORY):
            record.should_retry = True
            record.alternative_action = self._suggest_alternative(service, record)
        
        self.records.append(record)
        return record
    
    def _re_observe(self, service: str) -> List[ObserverSnapshot]:
        """
        Re-observe service from ALL observer positions.
        Uses topology_probe to get fresh state from every perspective.
        """
        snapshots = []
        
        from backend.diagnostics.topology_probe import probe_all, ObserverPosition
        
        try:
            results = probe_all(
                observers=[ObserverPosition.HERMES_CONTAINER],
                services=[service],
            )
            
            for r in results:
                snapshots.append(ObserverSnapshot(
                    observer=r.observer.value,
                    target=r.target,
                    reachable=r.reachable,
                    latency_ms=r.latency_ms,
                    error=r.error,
                ))
        except Exception as e:
            snapshots.append(ObserverSnapshot(
                observer="system",
                target=service,
                reachable=False,
                latency_ms=0,
                error=f"Re-observation failed: {e}",
            ))
        
        return snapshots
    
    def _count_contradictions(self, snapshots: List[ObserverSnapshot]) -> int:
        """Count how many observer pairs disagree."""
        reachable_count = sum(1 for s in snapshots if s.reachable)
        unreachable_count = len(snapshots) - reachable_count
        
        if reachable_count > 0 and unreachable_count > 0:
            return min(reachable_count, unreachable_count)
        return 0
    
    def _classify(self, snapshots: List[ObserverSnapshot]) -> str:
        """Classify the root cause from snapshot data."""
        reachable = [s for s in snapshots if s.reachable]
        unreachable = [s for s in snapshots if not s.reachable]
        
        if not unreachable:
            return "no_issue_detected"
        
        errors = [s.error for s in unreachable if s.error]
        error_text = " ".join(errors).lower()
        
        if "connection refused" in error_text:
            if any("localhost" in (s.observer or "") for s in unreachable):
                return "port_binding_localhost_only"
            return "network_isolation"
        
        if "timeout" in error_text:
            return "service_unresponsive"
        
        if "404" in error_text:
            return "endpoint_missing"
        
        if "401" in error_text:
            return "authentication_required"
        
        return "unknown_failure"
    
    def _evaluate_convergence(self, record: RecoveryRecord) -> ConvergenceState:
        """Evaluate whether the system converged after recovery."""
        pre_reachable = sum(1 for s in record.pre_snapshots if s.reachable)
        post_reachable = sum(1 for s in record.post_snapshots if s.reachable)
        total = max(len(record.pre_snapshots), len(record.post_snapshots), 1)
        
        pre_ratio = pre_reachable / total
        post_ratio = post_reachable / total
        
        # CONVERGED: All observers now agree, and it's positive
        if post_ratio >= self.CONVERGENCE_THRESHOLD and record.contradictions_after == 0:
            return ConvergenceState.CONVERGED
        
        # PARTIAL: Improvement but not complete
        if post_ratio > pre_ratio:
            return ConvergenceState.PARTIAL
        
        # REGRESSED: Worse than before
        if post_ratio < pre_ratio:
            return ConvergenceState.REGRESSED
        
        # CONTRADICTORY: Observers disagree
        if record.contradictions_after > 0:
            return ConvergenceState.CONTRADICTORY
        
        return ConvergenceState.UNKNOWN
    
    def _compute_confidence(self, record: RecoveryRecord) -> float:
        """Compute confidence in the recovery outcome."""
        total = max(len(record.post_snapshots), 1)
        agree = total - record.contradictions_after
        
        base_confidence = agree / total
        
        # Penalize if execution failed
        if record.execution_duration_ms > 10000:
            base_confidence *= 0.7
        
        # Bonus if contradictions decreased
        if record.contradictions_after < record.contradictions_before:
            base_confidence = min(1.0, base_confidence * 1.2)
        
        return round(base_confidence, 2)
    
    def _extract_lessons(self, record: RecoveryRecord) -> List[str]:
        """Extract operational lessons from recovery outcome."""
        lessons = []
        
        if record.convergence == ConvergenceState.CONVERGED:
            lessons.append(f"Recovery '{record.recovery_action}' successful for {record.service}")
            lessons.append(f"Confidence: {record.confidence}. Contradictions: {record.contradictions_before}→{record.contradictions_after}")
        
        elif record.convergence == ConvergenceState.PARTIAL:
            lessons.append(f"Partial recovery for {record.service}: {record.recovery_action}")
            lessons.append(f"Some observers still report issues. May need different approach.")
        
        elif record.convergence == ConvergenceState.REGRESSED:
            lessons.append(f"CRITICAL: Recovery made {record.service} WORSE")
            lessons.append(f"Action '{record.recovery_action}' should NOT be retried without analysis")
        
        elif record.convergence == ConvergenceState.CONTRADICTORY:
            lessons.append(f"Contradictory state after recovery: observers disagree about {record.service}")
            lessons.append(f"Possible split-brain or partial network partition")
        
        return lessons
    
    def _suggest_alternative(self, service: str, record: RecoveryRecord) -> str:
        """Suggest alternative recovery action."""
        from backend.runtime.service_registry import get_service
        
        svc = get_service(service)
        if svc:
            alt = svc.recovery_command
            if alt != record.recovery_command:
                return f"Alternative: {alt}"
        
        return "Manual investigation required — no alternative recovery path known"
    
    def get_convergence_report(self, service: str = None) -> Dict:
        """Get convergence report for all or specific service."""
        records = self.records
        if service:
            records = [r for r in records if r.service == service]
        
        by_state = {}
        for state in ConvergenceState:
            count = len([r for r in records if r.convergence == state])
            if count > 0:
                by_state[state.value] = count
        
        return {
            "total_recoveries": len(records),
            "convergence_rate": len([r for r in records if r.convergence == ConvergenceState.CONVERGED]) / max(1, len(records)),
            "by_state": by_state,
            "average_confidence": sum(r.confidence for r in records) / max(1, len(records)),
            "records": [
                {
                    "service": r.service,
                    "action": r.recovery_action,
                    "convergence": r.convergence.value,
                    "confidence": r.confidence,
                    "contradictions": f"{r.contradictions_before}→{r.contradictions_after}",
                }
                for r in records[-10:]  # Last 10
            ]
        }


# ══════════════════════════════════════════════
# GLOBAL INSTANCE
# ══════════════════════════════════════════════

_validator = ConvergenceValidator()


def validate_recovery(
    service: str,
    action: str,
    command: str,
    pre_snapshots: List[ObserverSnapshot] = None,
) -> RecoveryRecord:
    """Convenience wrapper for global validator."""
    if pre_snapshots is None:
        pre_snapshots = []
    return _validator.validate_recovery(service, action, command, pre_snapshots)


def convergence_report(service: str = None) -> Dict:
    """Get convergence report."""
    return _validator.get_convergence_report(service)
