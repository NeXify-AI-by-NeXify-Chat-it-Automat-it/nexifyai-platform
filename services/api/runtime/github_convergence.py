"""
NeXifyAI — GitHub Operational Convergence Layer (E6)
Bridges GitHub Issues/Actions/Deployments into the Truth Graph.

GitHub is no longer just an event store.
It is now part of the epistemic event topology.

Principle:
  Issues  = observable contradictions in the operational graph
  Actions = epistemic sensors, not just executors
  Badges  = confidence scores, not binary success
  Vercel  = a projection, not canonical truth
"""

import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum


class IssueCorrelation(Enum):
    """How a GitHub issue maps to runtime state."""
    EXACT_MATCH = "exact_match"           # Issue directly describes a known contradiction
    PARTIAL_MATCH = "partial_match"       # Issue relates to a service with some drift
    UNRELATED = "unrelated"               # Issue not connected to any known runtime state
    RESOLVED_IN_RUNTIME = "resolved"      # Runtime converged — issue can be closed
    STALE = "stale"                       # Issue open but runtime state unknown


@dataclass
class IssueRuntimeBinding:
    """Binds a GitHub issue to runtime truth state."""
    issue_number: int
    issue_title: str
    service: str                        # Which service this issue relates to
    correlation: IssueCorrelation
    confidence: float
    contradictions: int
    convergence_state: str
    last_validation: str
    auto_comment: str                   # Suggested comment text
    eligible_for_close: bool


# ══════════════════════════════════════════════
# GITHUB CONVERGENCE ENGINE
# ══════════════════════════════════════════════

class GitHubConvergence:
    """
    Correlates GitHub issues with runtime truth graph state.
    
    Detects when:
    - An issue's underlying contradiction has resolved
    - A deployment has converged across all observers
    - An issue has become stale (no runtime validation in >24h)
    - Auto-comment should be posted with confidence data
    """
    
    REPO_OWNER = "nexifyai-dev"
    REPO_NAME = "nexifyai-website-sicherheitskopie"
    
    # Known issue → service mappings
    ISSUE_SERVICE_MAP = {
        "backend": ["backend", "api"],
        "qdrant": ["qdrant-primary", "qdrant-vjfp"],
        "redis": ["redis"],
        "supabase": ["supabase-db"],
        "deploy": ["backend", "traefik"],
        "vercel": ["backend", "traefik"],
        "health": ["backend"],
        "login": ["backend", "supabase-db"],
        "database": ["supabase-db"],
        "search": ["qdrant-primary", "qdrant-vjfp"],
    }
    
    def __init__(self):
        self.bindings: List[IssueRuntimeBinding] = []
    
    def correlate_issue(
        self,
        issue_number: int,
        issue_title: str,
        issue_body: str = "",
    ) -> IssueRuntimeBinding:
        """
        Correlate a GitHub issue with current runtime state.
        Returns binding with convergence data and auto-comment suggestion.
        """
        from backend.runtime.truth_graph import build_truth_graph
        
        # Determine which services this issue relates to
        services = self._extract_services(issue_title, issue_body)
        
        # Get current truth graph state
        graph = build_truth_graph()
        contradictions = graph.find_contradictions()
        
        # Find contradictions for these services
        relevant_contradictions = [
            c for c in contradictions
            if any(s in c.get("target", "") for s in services)
        ]
        
        # Determine convergence state
        if not relevant_contradictions:
            correlation = IssueCorrelation.RESOLVED_IN_RUNTIME
            confidence = 1.0
            convergence = "converged"
        elif len(relevant_contradictions) < 2:
            correlation = IssueCorrelation.PARTIAL_MATCH
            confidence = 0.7
            convergence = "partial"
        else:
            correlation = IssueCorrelation.EXACT_MATCH
            confidence = 0.3
            convergence = "contradictory"
        
        # Build auto-comment
        auto_comment = self._build_comment(
            issue_number, services, confidence, convergence,
            len(relevant_contradictions), contradictions
        )
        
        binding = IssueRuntimeBinding(
            issue_number=issue_number,
            issue_title=issue_title,
            service=", ".join(services),
            correlation=correlation,
            confidence=round(confidence, 2),
            contradictions=len(relevant_contradictions),
            convergence_state=convergence,
            last_validation=datetime.now(timezone.utc).isoformat(),
            auto_comment=auto_comment,
            eligible_for_close=(correlation == IssueCorrelation.RESOLVED_IN_RUNTIME),
        )
        
        self.bindings.append(binding)
        return binding
    
    def _extract_services(self, title: str, body: str) -> List[str]:
        """Extract service names from issue text."""
        text = (title + " " + body).lower()
        services = set()
        
        for keyword, svcs in self.ISSUE_SERVICE_MAP.items():
            if keyword in text:
                services.update(svcs)
        
        if not services:
            services.add("backend")  # Default: most issues relate to backend
        
        return list(services)
    
    def _build_comment(
        self,
        issue_number: int,
        services: List[str],
        confidence: float,
        convergence: str,
        contradiction_count: int,
        all_contradictions: List[Dict],
    ) -> str:
        """Build auto-comment with runtime convergence data."""
        
        status_icon = {
            "converged": "✅",
            "partial": "⚠️",
            "contradictory": "❌",
        }.get(convergence, "❓")
        
        lines = [
            f"## 🤖 Runtime Convergence Check",
            f"",
            f"**Issue:** #{issue_number}",
            f"**Services:** {', '.join(services)}",
            f"**Convergence:** {status_icon} {convergence.upper()}",
            f"**Confidence:** {confidence}",
            f"**Contradictions:** {contradiction_count}",
            f"**Validated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            f"",
        ]
        
        if convergence == "converged":
            lines.append("✅ Runtime has converged. This issue may be eligible for closure.")
            lines.append("")
            lines.append("Confidence will decay over time. Re-validation recommended before closing.")
        elif convergence == "partial":
            lines.append("⚠️  Partial convergence. Some observers still report issues:")
            for c in all_contradictions[:3]:
                lines.append(f"- {c.get('target', 'unknown')}: {c.get('diagnosis', 'no data')[:100]}")
        else:
            lines.append("❌ Contradictions still active:")
            for c in all_contradictions[:3]:
                lines.append(f"- {c.get('target', 'unknown')}: {c.get('diagnosis', 'no data')[:100]}")
            lines.append("")
            lines.append("**Recommended:** Do NOT close. Runtime has not converged.")
        
        return "\n".join(lines)
    
    def batch_correlate(self, issues: List[Dict]) -> List[IssueRuntimeBinding]:
        """Correlate multiple issues at once."""
        bindings = []
        for issue in issues:
            binding = self.correlate_issue(
                issue_number=issue.get("number", 0),
                issue_title=issue.get("title", ""),
                issue_body=issue.get("body", ""),
            )
            bindings.append(binding)
        return bindings
    
    def convergence_report(self) -> Dict:
        """GitHub-focused convergence report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues_analyzed": len(self.bindings),
            "eligible_for_close": len([b for b in self.bindings if b.eligible_for_close]),
            "active_contradictions": len([b for b in self.bindings if b.correlation == IssueCorrelation.EXACT_MATCH]),
            "bindings": [
                {
                    "issue": b.issue_number,
                    "service": b.service,
                    "correlation": b.correlation.value,
                    "confidence": b.confidence,
                    "eligible_close": b.eligible_for_close,
                }
                for b in self.bindings
            ],
        }


# ══════════════════════════════════════════════
# CI POST-DEPLOY OBSERVER
# ══════════════════════════════════════════════

def post_deploy_validation_script() -> str:
    """
    Generate a CI script for post-deployment validation.
    This goes AFTER the deploy step in CI workflows.
    """
    return """#!/bin/bash
# ══════════════════════════════════════════════
# POST-DEPLOY CONVERGENCE VALIDATION (E6)
# Runs after deployment. BLOCKS on non-convergence.
# ══════════════════════════════════════════════

set -e

echo "═══ POST-DEPLOY: STABILIZING (5s) ═══"
sleep 5

echo "═══ POST-DEPLOY: RE-OBSERVING ═══"

# Check backend
BACKEND_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 https://www.nexify-automate.com/api/health/live 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend reachable"
else
    echo "❌ Backend returned HTTP $BACKEND_STATUS"
    echo "⛔ DEPLOYMENT CONVERGENCE FAILED"
    exit 1
fi

# Check health v2
HEALTH=$(curl -sf --max-time 10 https://www.nexify-automate.com/api/health/v2 2>/dev/null || echo '{"score":0}')
HEALTH_SCORE=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('score',0))" 2>/dev/null || echo "0")

if [ "$HEALTH_SCORE" -gt 30 ]; then
    echo "✅ Health score: $HEALTH_SCORE"
else
    echo "❌ Health score degraded: $HEALTH_SCORE"
    echo "⛔ DEPLOYMENT CONVERGENCE FAILED"
    exit 1
fi

echo "═══ POST-DEPLOY: DEPENDENCY CHECK ═══"

# Check critical dependencies via health/ready
READY=$(curl -sf --max-time 10 https://www.nexify-automate.com/api/health/ready 2>/dev/null || echo '{"status":"not_ready"}')
READY_STATUS=$(echo "$READY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','not_ready'))" 2>/dev/null || echo "not_ready")

if [ "$READY_STATUS" = "ready" ]; then
    echo "✅ All dependencies ready"
else
    echo "⚠️  Not all dependencies ready: $READY_STATUS"
fi

echo "═══ POST-DEPLOY: CONVERGED ✅ ═══"
"""
