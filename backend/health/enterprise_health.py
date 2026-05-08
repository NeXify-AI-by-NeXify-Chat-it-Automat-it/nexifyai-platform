"""
NeXifyAI — Enterprise Health System
10-component health score with dashboards, alerts, trends, and forecasting.

Usage:
    from backend.health.enterprise_health import EnterpriseHealth
    health = EnterpriseHealth()
    score = health.compute_score()
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone


class HealthStatus(Enum):
    EXCELLENT = "excellent"  # ≥ 90
    GOOD = "good"            # ≥ 80
    FAIR = "fair"            # ≥ 65
    DEGRADED = "degraded"    # ≥ 50
    CRITICAL = "critical"    # < 50


@dataclass
class HealthComponent:
    """Single health component with weight and score."""
    name: str
    weight: float  # 0.0 - 1.0 (sum of all weights = 1.0)
    score: float = 0.0  # 0.0 - 100.0
    status: HealthStatus = HealthStatus.CRITICAL
    metrics: Dict[str, Any] = field(default_factory=dict)
    trend: str = "stable"  # 'improving', 'stable', 'declining'
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


# ══════════════════════════════════════════════
# ENTERPRISE HEALTH SYSTEM (10 Components)
# ══════════════════════════════════════════════

class EnterpriseHealth:
    """
    10-component enterprise health scoring system.
    
    Components (DOS v2.1 extended):
    1. Reliability (15%) — Uptime, error rate, MTTR
    2. Performance (10%) — Latency P95, response times
    3. Security (15%) — CVE count, secrets exposed, scan results
    4. Cost Efficiency (10%) — Budget adherence, per-tenant cost
    5. AI Accuracy (10%) — Model performance, prompt effectiveness
    6. Test Stability (10%) — Pass rate, coverage, flaky tests
    7. Deployment Quality (10%) — Deploy success rate, rollback rate
    8. Incident Frequency (10%) — SEV events per week, MTTR
    9. Technical Debt (5%) — Deprecated deps, TODO count, code churn
    10. Knowledge Completeness (5%) — Brain gaps, ADR coverage, doc freshness
    """
    
    COMPONENT_WEIGHTS = {
        "reliability": 0.15,
        "performance": 0.10,
        "security": 0.15,
        "cost_efficiency": 0.10,
        "ai_accuracy": 0.10,
        "test_stability": 0.10,
        "deployment_quality": 0.10,
        "incident_frequency": 0.10,
        "technical_debt": 0.05,
        "knowledge_completeness": 0.05,
    }
    
    def __init__(self):
        self.components: Dict[str, HealthComponent] = {}
        self._init_components()
    
    def _init_components(self):
        """Initialize all health components with default values."""
        for name, weight in self.COMPONENT_WEIGHTS.items():
            self.components[name] = HealthComponent(
                name=name.replace('_', ' ').title(),
                weight=weight,
            )
    
    # ══════════════════════════════════════════
    # SCORING
    # ══════════════════════════════════════════
    
    def compute_score(self) -> float:
        """Compute weighted health score across all components."""
        total = sum(c.weighted_score for c in self.components.values())
        return round(total, 1)
    
    def get_status(self, score: float = None) -> HealthStatus:
        """Get health status from score."""
        score = score or self.compute_score()
        if score >= 90:
            return HealthStatus.EXCELLENT
        elif score >= 80:
            return HealthStatus.GOOD
        elif score >= 65:
            return HealthStatus.FAIR
        elif score >= 50:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.CRITICAL
    
    # ══════════════════════════════════════════
    # METRICS UPDATE
    # ══════════════════════════════════════════
    
    def update_component(self, name: str, score: float, metrics: Dict = None):
        """Update a single health component."""
        if name in self.components:
            self.components[name].score = min(100.0, max(0.0, score))
            if metrics:
                self.components[name].metrics.update(metrics)
            self.components[name].last_updated = datetime.now(timezone.utc).isoformat()
            self.components[name].status = self._component_status(score)
    
    def _component_status(self, score: float) -> HealthStatus:
        if score >= 90:
            return HealthStatus.EXCELLENT
        elif score >= 80:
            return HealthStatus.GOOD
        elif score >= 65:
            return HealthStatus.FAIR
        elif score >= 50:
            return HealthStatus.DEGRADED
        return HealthStatus.CRITICAL
    
    # ══════════════════════════════════════════
    # REPORTING
    # ══════════════════════════════════════════
    
    def to_dict(self) -> Dict:
        """Full health report as dict."""
        score = self.compute_score()
        return {
            "overall_score": score,
            "status": self.get_status(score).value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                name: {
                    "name": comp.name,
                    "weight": comp.weight,
                    "score": comp.score,
                    "weighted_score": comp.weighted_score,
                    "status": comp.status.value,
                    "trend": comp.trend,
                    "metrics": comp.metrics,
                }
                for name, comp in self.components.items()
            },
            "alerts": self.generate_alerts(score),
        }
    
    def to_cli_dashboard(self) -> str:
        """CLI-friendly dashboard format."""
        score = self.compute_score()
        status = self.get_status(score)
        
        status_icons = {
            HealthStatus.EXCELLENT: "🟢",
            HealthStatus.GOOD: "🟢",
            HealthStatus.FAIR: "🟡",
            HealthStatus.DEGRADED: "🟠",
            HealthStatus.CRITICAL: "🔴",
        }
        
        lines = [
            f"═══ ENTERPRISE HEALTH: {score:.1f}% — {status.value.upper()} {status_icons[status]} ═══",
            "",
            "| Component              | Weight | Score  | Status   | Trend     |",
            "|------------------------|--------|--------|----------|-----------|",
        ]
        
        for comp in self.components.values():
            trend_icon = {"improving": "↑", "stable": "→", "declining": "↓"}.get(comp.trend, "→")
            lines.append(
                f"| {comp.name:<22} | {comp.weight:.0%}    | {comp.score:5.1f} | {comp.status.value:<8} | {trend_icon}         |"
            )
        
        lines.append("")
        lines.extend(self.generate_alerts(score))
        
        return "\n".join(lines)
    
    def generate_alerts(self, score: float = None) -> List[str]:
        """Generate alerts based on health state."""
        score = score or self.compute_score()
        alerts = []
        
        if score < 50:
            alerts.append("🚨 CRITICAL: System health critical. Immediate action required.")
        elif score < 65:
            alerts.append("⚠️  WARNING: System degraded. Investigate failing components.")
        
        # Component-specific alerts
        for name, comp in self.components.items():
            if comp.score < 50:
                alerts.append(f"🔴 {comp.name}: {comp.score:.0f}% — needs attention")
            elif comp.score < 70:
                alerts.append(f"🟡 {comp.name}: {comp.score:.0f}% — below target")
        
        return alerts
    
    # ══════════════════════════════════════════
    # FORECASTING (Linear Regression)
    # ══════════════════════════════════════════
    
    def forecast(self, history: List[float], days_ahead: int = 7) -> float:
        """
        Simple linear trend forecast based on historical scores.
        Returns predicted score in N days.
        """
        if len(history) < 2:
            return self.compute_score()
        
        n = len(history)
        x_mean = (n - 1) / 2
        y_mean = sum(history) / n
        
        # Linear regression: y = mx + b
        numerator = sum((i - x_mean) * (history[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return history[-1]
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict N days ahead
        predicted = intercept + slope * (n + days_ahead - 1)
        return max(0.0, min(100.0, predicted))
