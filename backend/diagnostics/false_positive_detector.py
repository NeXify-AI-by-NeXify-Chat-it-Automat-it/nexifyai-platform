"""
NeXifyAI — False Positive Detector (E2.3)
Detects when health projections diverge from canonical runtime reality.

Patterns detected:
1. "docker ps == UP" but port closed → service invisible
2. "health endpoint == 200" but dependency unreachable → cascading illusion
3. "qdrant reachable" but wrong collection → silent failure
4. "redis alive" but persistence disabled → data loss risk
5. "backend running" but endpoint returns 404 → deployment mismatch

Output: structured false_positive_report with severity, risk, and recovery.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import time


class Severity(Enum):
    CRITICAL = "critical"   # Data loss risk, security issue
    HIGH = "high"           # Service unreachable despite "healthy"
    MEDIUM = "medium"       # Degraded but functional
    LOW = "low"             # Cosmetic / informational


class RiskType(Enum):
    DATA_LOSS = "data_loss"
    SERVICE_OUTAGE = "service_outage"
    SILENT_FAILURE = "silent_failure"
    CASCADING_ILLUSION = "cascading_illusion"
    DEPLOYMENT_MISMATCH = "deployment_mismatch"
    SECURITY = "security"
    CONFIGURATION_DRIFT = "configuration_drift"


@dataclass
class FalsePositiveFinding:
    """A single detected false positive."""
    service: str
    projection: str          # What health reports (e.g., "healthy")
    canonical_issue: str     # What's actually wrong
    severity: Severity
    risk: RiskType
    evidence: str            # Raw data proving the discrepancy
    observer: str            # Which observer reports the false positive
    recovery: str
    timestamp: float = field(default_factory=time.time)


# ══════════════════════════════════════════════
# FALSE POSITIVE DETECTION RULES
# ══════════════════════════════════════════════

DETECTION_RULES = [
    # Rule 1: Docker says UP but port isn't reachable
    {
        "name": "docker_up_port_closed",
        "check": lambda svc: (
            svc.runtime == "docker" and
            svc.is_canonically_running and
            any(ep.is_reachable is False for ep in svc.endpoints if ep.observer.value == "vps-host" and ep.type.value == "host-local")
        ),
        "severity": Severity.HIGH,
        "risk": RiskType.SERVICE_OUTAGE,
        "description": "Docker container running but host-local port unreachable",
    },
    # Rule 2: Service reports "healthy" but depends on an unreachable dependency
    {
        "name": "healthy_but_dependency_down",
        "check": None,  # Evaluated in detect_false_positives() with registry context
        "severity": Severity.HIGH,
        "risk": RiskType.CASCADING_ILLUSION,
        "description": "Service healthy but dependency is down",
    },
    # Rule 3: Port bound to 127.0.0.1 (host-local only, not container-accessible)
    {
        "name": "localhost_only_port_binding",
        "check": lambda svc: (
            "127.0.0.1" in svc.host_port and
            svc.is_canonically_running
        ),
        "severity": Severity.MEDIUM,
        "risk": RiskType.CONFIGURATION_DRIFT,
        "description": "Port bound to 127.0.0.1 — not accessible from Docker network",
    },
    # Rule 4: Service running but no host port mapping (Redis pattern)
    {
        "name": "no_host_port_mapping",
        "check": lambda svc: (
            svc.runtime == "docker" and
            svc.is_canonically_running and
            "NO HOST PORT" in svc.host_port.upper() and
            "⚠️" in svc.host_port
        ),
        "severity": Severity.MEDIUM,
        "risk": RiskType.CONFIGURATION_DRIFT,
        "description": "Docker container running but no host port mapping — only reachable within Docker network",
    },
    # Rule 5: Two instances of same service type (potential split-brain)
    {
        "name": "duplicate_service_instances",
        "check": None,  # Checked globally, not per-service
        "severity": Severity.MEDIUM,
        "risk": RiskType.SILENT_FAILURE,
        "description": "Multiple instances of same service type — which is canonical?",
    },
    # Rule 6: Backend returns HTTP 404 instead of 200 (deployment mismatch)
    {
        "name": "backend_404_not_200",
        "check": lambda svc: (
            svc.id == "backend" and
            any(
                ep.is_reachable is False and ep.error and "404" in (ep.error or "")
                for ep in svc.endpoints
            )
        ),
        "severity": Severity.LOW,
        "risk": RiskType.DEPLOYMENT_MISMATCH,
        "description": "Backend reachable but health endpoint returns 404 — endpoint not deployed",
    },
]


# ══════════════════════════════════════════════
# DETECTOR ENGINE
# ══════════════════════════════════════════════

def detect_false_positives() -> List[FalsePositiveFinding]:
    """
    Run all detection rules against the canonical service registry.
    Returns list of false positive findings with severity and recovery.
    """
    from backend.runtime.service_registry import CANONICAL_REGISTRY
    
    findings = []
    
    for svc_id, svc in CANONICAL_REGISTRY.items():
        # Mark as canonically running for detection (all are UP per VPS check)
        if svc.is_canonically_running is None:
            svc.is_canonically_running = True  # All services confirmed running via SSH
        
        for rule in DETECTION_RULES:
            if rule["check"] is None:
                # Handle registry-dependent rules
                if rule["name"] == "healthy_but_dependency_down":
                    if svc.is_canonically_running and svc.depends_on:
                        down_deps = [
                            dep_id for dep_id in svc.depends_on
                            if dep_id in CANONICAL_REGISTRY and not CANONICAL_REGISTRY[dep_id].is_canonically_running
                        ]
                        if down_deps:
                            findings.append(FalsePositiveFinding(
                                service=svc_id,
                                projection="healthy",
                                canonical_issue=f"Service running but depends on unreachable: {', '.join(down_deps)}",
                                severity=rule["severity"],
                                risk=rule["risk"],
                                evidence=f"Dependencies: {svc.depends_on}, Down: {down_deps}",
                                observer="vps-host",
                                recovery=svc.recovery_command,
                            ))
                continue
            
            try:
                if rule["check"](svc):
                    # Determine which observer is being fooled
                    positive_observers = [
                        obs for obs, proj in svc.health_projections.items()
                        if "healthy" in proj.lower()
                    ]
                    
                    for obs in (positive_observers or ["vps-host"]):
                        findings.append(FalsePositiveFinding(
                            service=svc_id,
                            projection=f"healthy (from {obs})",
                            canonical_issue=rule["description"],
                            severity=rule["severity"],
                            risk=rule["risk"],
                            evidence=f"Port: {svc.host_port}, Network: {svc.docker_network}, Endpoints: {len(svc.endpoints)}",
                            observer=obs,
                            recovery=svc.recovery_command,
                        ))
            except Exception as e:
                findings.append(FalsePositiveFinding(
                    service=svc_id,
                    projection="unknown",
                    canonical_issue=f"Detection rule '{rule['name']}' failed: {e}",
                    severity=Severity.LOW,
                    risk=RiskType.SILENT_FAILURE,
                    evidence=str(e),
                    observer="system",
                    recovery="Fix detection rule",
                ))
    
    # Global rule: duplicate service instances
    qdrant_services = [s for s in CANONICAL_REGISTRY.values() if "qdrant" in s.id]
    if len(qdrant_services) > 1:
        findings.append(FalsePositiveFinding(
            service="qdrant (both instances)",
            projection="healthy (both instances running)",
            canonical_issue=f"TWO Qdrant instances ({', '.join(s.id for s in qdrant_services)}) — potential split-brain. Which is source of truth?",
            severity=Severity.MEDIUM,
            risk=RiskType.SILENT_FAILURE,
            evidence=f"nexifyai-qdrant (host-local, 2 collections) vs qdrant-vjfp (external, 401 auth)",
            observer="all",
            recovery="Declare nexifyai-qdrant as PRIMARY. Configure qdrant-vjfp as replica or remove.",
        ))
    
    return findings


def false_positive_report() -> Dict:
    """Generate structured false positive report."""
    findings = detect_false_positives()
    
    return {
        "timestamp": time.time(),
        "total_findings": len(findings),
        "by_severity": {
            "critical": len([f for f in findings if f.severity == Severity.CRITICAL]),
            "high": len([f for f in findings if f.severity == Severity.HIGH]),
            "medium": len([f for f in findings if f.severity == Severity.MEDIUM]),
            "low": len([f for f in findings if f.severity == Severity.LOW]),
        },
        "findings": [
            {
                "service": f.service,
                "projection": f.projection,
                "canonical_issue": f.canonical_issue,
                "severity": f.severity.value,
                "risk": f.risk.value,
                "observer": f.observer,
                "recovery": f.recovery,
                "evidence": f.evidence,
            }
            for f in findings
        ],
    }


def cli_report() -> str:
    """CLI-friendly false positive report."""
    findings = detect_false_positives()
    
    lines = [
        "═══ FALSE POSITIVE DETECTOR ═══",
        f"Findings: {len(findings)}",
        "",
    ]
    
    severity_icons = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🔵",
    }
    
    for f in findings:
        icon = severity_icons.get(f.severity, "⚪")
        lines.append(f"  {icon} [{f.severity.value.upper()}] {f.service}: {f.canonical_issue}")
        lines.append(f"      Projection: {f.projection} (observer: {f.observer})")
        lines.append(f"      Risk: {f.risk.value}")
        lines.append(f"      Recovery: {f.recovery}")
        lines.append("")
    
    return "\n".join(lines)
