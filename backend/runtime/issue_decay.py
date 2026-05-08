"""
NeXifyAI — Open Issue Decay Model (E6.7)

Every open GitHub issue must be periodically revalidated.
Issues are NOT passive tickets — they are observable contradictions.

Decay Rules:
  Open > 1h without validation → confidence decays (0.95^h)
  Open > 4h → STALE
  Open > 12h → ESCALATION (notify operator channel)
  Open > 24h → BLOCK deploy (unresolved contradictions invalidate deployment confidence)

Close Rules:
  Issue can only be closed if:
    - RE-OBSERVED (all observers)
    - CONTRADICTION COUNT = 0
    - DEPLOYMENT CONFIDENCE >= 0.8
    - TEMPORAL FRESHNESS < 1h
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum


class IssueDecayState(Enum):
    FRESH = "fresh"           # < 1h since last validation
    AGING = "aging"           # 1-4h
    STALE = "stale"           # 4-12h
    ESCALATED = "escalated"   # 12-24h
    BLOCKING = "blocking"     # > 24h — blocks deployments


@dataclass
class OpenIssue:
    """An open GitHub issue tracked for decay."""
    number: int
    title: str
    severity: str  # P0, P1, P2, P3, P4
    opened_at: float
    last_validated_at: Optional[float] = None
    confidence: float = 1.0
    contradictions_remaining: int = 0
    convergence_state: str = "unknown"
    decay_state: IssueDecayState = IssueDecayState.FRESH
    
    @property
    def age_hours(self) -> float:
        return (time.time() - self.opened_at) / 3600
    
    @property
    def hours_since_validation(self) -> float:
        if self.last_validated_at:
            return (time.time() - self.last_validated_at) / 3600
        return self.age_hours
    
    @property
    def should_block_deploy(self) -> bool:
        """P0/P1 issues open > 24h BLOCK deployment."""
        return (
            self.severity in ("P0", "P1")
            and self.decay_state == IssueDecayState.BLOCKING
        )


class IssueDecayEngine:
    """Tracks and decays open GitHub issues against runtime state."""
    
    DECAY_RATE = 0.95  # Per hour without validation
    
    def __init__(self):
        self.issues: Dict[int, OpenIssue] = {}
    
    def register(self, number: int, title: str, severity: str = "P2") -> OpenIssue:
        """Register an open issue for decay tracking."""
        issue = OpenIssue(
            number=number,
            title=title,
            severity=severity,
            opened_at=time.time(),
        )
        self.issues[number] = issue
        return issue
    
    def validate(self, number: int, contradictions: int = 0, convergence: str = "unknown") -> OpenIssue:
        """Re-validate an issue against current runtime state."""
        issue = self.issues.get(number)
        if not issue:
            return None
        
        issue.last_validated_at = time.time()
        issue.contradictions_remaining = contradictions
        issue.convergence_state = convergence
        
        # Recompute confidence
        if contradictions == 0 and convergence == "converged":
            issue.confidence = 1.0
        elif contradictions == 0:
            issue.confidence = 0.9
        else:
            issue.confidence = max(0.1, 1.0 - (contradictions * 0.2))
        
        issue.decay_state = IssueDecayState.FRESH
        return issue
    
    def decay_all(self) -> Dict[int, IssueDecayState]:
        """Apply temporal decay to all open issues."""
        updates = {}
        
        for issue in self.issues.values():
            hours = issue.hours_since_validation
            issue.confidence = round(issue.confidence * (self.DECAY_RATE ** hours), 2)
            
            if hours > 24 and issue.severity in ("P0", "P1"):
                issue.decay_state = IssueDecayState.BLOCKING
            elif hours > 12:
                issue.decay_state = IssueDecayState.ESCALATED
            elif hours > 4:
                issue.decay_state = IssueDecayState.STALE
            elif hours > 1:
                issue.decay_state = IssueDecayState.AGING
            else:
                issue.decay_state = IssueDecayState.FRESH
            
            updates[issue.number] = issue.decay_state
        
        return updates
    
    def blocking_issues(self) -> List[OpenIssue]:
        """Issues that should block deployment."""
        self.decay_all()
        return [i for i in self.issues.values() if i.should_block_deploy]
    
    def stale_issues(self) -> List[OpenIssue]:
        """Issues that need re-validation."""
        self.decay_all()
        return [i for i in self.issues.values() if i.decay_state in (
            IssueDecayState.STALE, IssueDecayState.ESCALATED, IssueDecayState.BLOCKING
        )]
    
    def can_close(self, number: int) -> tuple:
        """
        Check if an issue can be safely closed.
        Returns (can_close: bool, reason: str).
        """
        issue = self.issues.get(number)
        if not issue:
            return False, "Issue not registered in decay engine"
        
        if issue.contradictions_remaining > 0:
            return False, f"{issue.contradictions_remaining} contradictions still active"
        
        if issue.confidence < 0.8:
            return False, f"Confidence too low: {issue.confidence}"
        
        if issue.hours_since_validation > 1:
            return False, f"Last validation {issue.hours_since_validation:.1f}h ago — re-validate before closing"
        
        if issue.convergence_state != "converged":
            return False, f"Not converged: {issue.convergence_state}"
        
        return True, "Safe to close"
    
    def report(self) -> Dict:
        """Full issue decay report."""
        self.decay_all()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_open": len(self.issues),
            "blocking_deploy": len(self.blocking_issues()),
            "stale": len(self.stale_issues()),
            "by_state": {
                state.value: len([i for i in self.issues.values() if i.decay_state == state])
                for state in IssueDecayState
            },
            "issues": [
                {
                    "number": i.number,
                    "severity": i.severity,
                    "age_hours": round(i.age_hours, 1),
                    "confidence": i.confidence,
                    "state": i.decay_state.value,
                    "blocks_deploy": i.should_block_deploy,
                }
                for i in sorted(self.issues.values(), key=lambda x: -x.age_hours)
            ],
        }


# ══════════════════════════════════════════════
# GLOBAL INSTANCE
# ══════════════════════════════════════════════

_decay_engine = IssueDecayEngine()


def register_issue(number: int, title: str, severity: str = "P2") -> OpenIssue:
    return _decay_engine.register(number, title, severity)


def reconcile_issues() -> Dict:
    """Run full reconciliation: decay all issues, return report."""
    return _decay_engine.report()


def get_blocking_issues() -> List[OpenIssue]:
    """Get issues that block deployment."""
    return _decay_engine.blocking_issues()
