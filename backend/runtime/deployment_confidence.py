"""
NeXifyAI — Deployment Confidence (E4.5)
Extends the Recovery State Machine to deployments.

A deployment is a mutation. Per Constitution §I.2 + §VI:
"No mutation without re-observation."
"A deployment is not a point-in-time event — it is a continuously revalidated operational state."

Usage:
    dc = DeploymentConfidence()
    record = dc.validate_deployment(
        service="backend",
        commit_sha="abc123",
        pre_snapshots=[...],
    )
    # After 4h without re-observation:
    dc.decay_all()  # backend confidence: 1.0 → 0.41
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
from enum import Enum


class DeploymentConvergence(Enum):
    CONVERGED = "converged"
    PARTIAL = "partial"
    REGRESSED = "regressed"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass
class DeploymentRecord:
    """Complete deployment lifecycle with confidence tracking."""
    deployment_id: str
    service: str
    commit_sha: str = ""
    environment: str = "production"
    
    # Confidence
    confidence: float = 1.0
    convergence: DeploymentConvergence = DeploymentConvergence.UNKNOWN
    
    # Timing
    deployed_at: float = field(default_factory=time.time)
    last_validated_at: Optional[float] = None
    hours_since_validation: float = 0.0
    
    # Validation results
    contradictions_detected: int = 0
    observers_converged: int = 0
    observers_total: int = 0
    dependency_health_ok: bool = True
    
    # Decay tracking
    decay_events: List[Dict] = field(default_factory=list)
    
    @property
    def is_stale(self) -> bool:
        """Confidence < 0.3 or >48h without validation."""
        if self.last_validated_at is None:
            return (time.time() - self.deployed_at) > 3600  # 1h without any validation
        return self.confidence < 0.3 or self.hours_since_validation > 48
    
    @property
    def status_display(self) -> str:
        """Human-readable deployment status."""
        if self.convergence == DeploymentConvergence.CONVERGED and self.confidence > 0.8:
            return "✅ Deployed & Converged"
        elif self.convergence == DeploymentConvergence.CONVERGED and self.confidence > 0.5:
            return "⚠️  Deployed (confidence degrading)"
        elif self.convergence == DeploymentConvergence.PARTIAL:
            return "⚠️  Partially converged"
        elif self.convergence == DeploymentConvergence.STALE:
            return "⏳ Stale (re-validation needed)"
        elif self.convergence == DeploymentConvergence.REGRESSED:
            return "❌ Regressed after deploy"
        return "❓ Unknown"


class DeploymentConfidence:
    """
    Deployment confidence tracker.
    
    Same epistemic model as Recovery, but for deployments:
    - Confidence starts at 1.0 (fresh deploy)
    - Decays with time: 0.95^t_hours
    - Penalized by contradictions, observer divergence
    - Requires re-validation to restore confidence
    """
    
    DECAY_RATE = 0.95  # Per hour
    STALE_THRESHOLD_HOURS = 4  # Warn after 4h without re-observation
    STALE_CONFIDENCE_THRESHOLD = 0.5
    
    def __init__(self):
        self.records: Dict[str, DeploymentRecord] = {}
    
    def deploy(
        self,
        service: str,
        commit_sha: str = "",
        environment: str = "production",
    ) -> DeploymentRecord:
        """Register a new deployment."""
        record = DeploymentRecord(
            deployment_id=f"DEPLOY-{service}-{int(time.time())}",
            service=service,
            commit_sha=commit_sha,
            environment=environment,
        )
        self.records[service] = record
        return record
    
    def validate(
        self,
        service: str,
        contradictions_detected: int = 0,
        observers_converged: int = 0,
        observers_total: int = 0,
        dependency_health_ok: bool = True,
    ) -> DeploymentRecord:
        """Validate a deployment post-execution and recompute confidence."""
        record = self.records.get(service)
        if not record:
            record = self.deploy(service)
        
        record.last_validated_at = time.time()
        record.hours_since_validation = 0.0
        record.contradictions_detected = contradictions_detected
        record.observers_converged = observers_converged
        record.observers_total = observers_total
        record.dependency_health_ok = dependency_health_ok
        
        # Recompute confidence
        self._recompute(record)
        
        return record
    
    def _recompute(self, record: DeploymentRecord):
        """Recompute deployment confidence with penalties and bonuses."""
        confidence = 1.0  # Reset baseline
        
        # Penalties
        if record.contradictions_detected > 0:
            confidence *= 0.6
            record.decay_events.append({
                "event": "contradiction_penalty",
                "factor": 0.6,
                "timestamp": time.time(),
            })
        
        if record.observers_total > 0:
            observer_ratio = record.observers_converged / record.observers_total
            if observer_ratio < 1.0:
                confidence *= (0.7 + observer_ratio * 0.3)  # 0.7-1.0 range
        
        if not record.dependency_health_ok:
            confidence *= 0.7
        
        # Bonuses
        if record.contradictions_detected == 0:
            confidence = min(1.0, confidence + 0.1)
        
        if record.observers_converged == record.observers_total and record.observers_total > 0:
            confidence = min(1.0, confidence + 0.1)
        
        if record.dependency_health_ok:
            confidence = min(1.0, confidence + 0.05)
        
        # Determine convergence state
        if confidence >= 0.9 and record.contradictions_detected == 0:
            record.convergence = DeploymentConvergence.CONVERGED
        elif confidence >= 0.6:
            record.convergence = DeploymentConvergence.PARTIAL
        elif confidence >= 0.3:
            record.convergence = DeploymentConvergence.STALE
        else:
            record.convergence = DeploymentConvergence.REGRESSED
        
        record.confidence = round(confidence, 2)
    
    def decay_all(self) -> Dict[str, float]:
        """
        Apply temporal decay to ALL deployment records.
        Returns {service: new_confidence}.
        """
        updates = {}
        now = time.time()
        
        for service, record in self.records.items():
            if record.last_validated_at:
                age_hours = (now - record.last_validated_at) / 3600
            else:
                age_hours = (now - record.deployed_at) / 3600
            
            record.hours_since_validation = round(age_hours, 1)
            
            if age_hours > 48:
                record.confidence = 0.0
                record.convergence = DeploymentConvergence.STALE
            else:
                decay = self.DECAY_RATE ** age_hours
                record.confidence = round(record.confidence * decay, 2)
            
            # Re-evaluate convergence
            if record.confidence < 0.3:
                record.convergence = DeploymentConvergence.STALE
            
            record.decay_events.append({
                "event": "temporal_decay",
                "age_hours": round(age_hours, 1),
                "new_confidence": record.confidence,
                "timestamp": now,
            })
            
            updates[service] = record.confidence
        
        return updates
    
    def get_status(self, service: str) -> Optional[DeploymentRecord]:
        """Get current deployment status for a service."""
        return self.records.get(service)
    
    def all_stale(self) -> List[str]:
        """List all services with stale deployment confidence."""
        return [s for s, r in self.records.items() if r.is_stale]
    
    def report(self) -> Dict:
        """Full deployment confidence report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                service: {
                    "confidence": record.confidence,
                    "convergence": record.convergence.value,
                    "status": record.status_display,
                    "hours_since_validation": record.hours_since_validation,
                    "contradictions": record.contradictions_detected,
                    "deployed_at": record.deployed_at,
                }
                for service, record in self.records.items()
            },
            "stale_services": self.all_stale(),
            "average_confidence": sum(r.confidence for r in self.records.values()) / max(1, len(self.records)),
        }
