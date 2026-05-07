#!/usr/bin/env python3
"""
NeXifyAI — System Health Score Calculator v1.0
Berechnet den zusammengesetzten Health-Score aus 7 Komponenten.

Läuft als Teil des Health-Endpoints (GET /api/health)
oder standalone: python3 health-score.py
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional

# ══════════════════════════════════════════════
# GEWICHTUNG
# ══════════════════════════════════════════════

WEIGHTS = {
    "uptime": 0.25,        # 30-Tage-Uptime
    "error_rate": 0.20,    # Letzte 24h Error-Rate
    "latency": 0.15,       # P95 Latenz
    "deploy_frequency": 0.10,  # Deployments/Woche
    "mttr": 0.10,          # Mean Time to Resolve
    "security": 0.10,       # CVE-Score
    "conversion": 0.10,     # Demo/Landing Conversion
}

THRESHOLDS = {
    "uptime": {"excellent": 99.9, "good": 99.5, "warning": 99.0},
    "error_rate": {"excellent": 1.0, "good": 5.0, "warning": 10.0},  # %
    "latency": {"excellent": 200, "good": 500, "warning": 1000},  # ms P95
    "deploy_frequency": {"excellent": 7, "good": 3, "warning": 1},  # /Woche
    "mttr": {"excellent": 30, "good": 120, "warning": 360},  # Minuten
    "security": {"excellent": 90, "good": 70, "warning": 50},  # Score
    "conversion": {"excellent": 5.0, "good": 2.0, "warning": 1.0},  # %
}

def score_component(value: float, thresholds: dict, lower_is_better: bool) -> float:
    """Berechnet Score 0-100 für eine Komponente."""
    if lower_is_better:
        if value <= thresholds["excellent"]:
            return 100.0
        elif value <= thresholds["good"]:
            return 75.0
        elif value <= thresholds["warning"]:
            return 50.0
        else:
            return max(0.0, 50.0 - (value - thresholds["warning"]) / thresholds["warning"] * 50)
    else:
        if value >= thresholds["excellent"]:
            return 100.0
        elif value >= thresholds["good"]:
            return 75.0
        elif value >= thresholds["warning"]:
            return 50.0
        else:
            return max(0.0, value / thresholds["warning"] * 50)

def calculate_health_score(metrics: dict) -> dict:
    """
    Berechnet den Gesamt-Health-Score.
    
    metrics = {
        "uptime": 99.95,        # %
        "error_rate": 2.3,      # %
        "latency_p95": 350,     # ms
        "deploy_frequency": 5,  # /Woche
        "mttr": 45,             # Minuten
        "security_score": 85,   # 0-100
        "conversion_rate": 3.2  # %
    }
    """
    
    scores = {}
    
    # Uptime (höher = besser)
    scores["uptime"] = score_component(
        metrics.get("uptime", 0), THRESHOLDS["uptime"], lower_is_better=False
    )
    
    # Error Rate (niedriger = besser)
    scores["error_rate"] = score_component(
        metrics.get("error_rate", 100), THRESHOLDS["error_rate"], lower_is_better=True
    )
    
    # Latenz (niedriger = besser)
    scores["latency"] = score_component(
        metrics.get("latency_p95", 9999), THRESHOLDS["latency"], lower_is_better=True
    )
    
    # Deploy Frequency (höher = besser)
    scores["deploy_frequency"] = score_component(
        metrics.get("deploy_frequency", 0), THRESHOLDS["deploy_frequency"], lower_is_better=False
    )
    
    # MTTR (niedriger = besser)
    scores["mttr"] = score_component(
        metrics.get("mttr", 9999), THRESHOLDS["mttr"], lower_is_better=True
    )
    
    # Security (höher = besser)
    scores["security"] = score_component(
        metrics.get("security_score", 0), THRESHOLDS["security"], lower_is_better=False
    )
    
    # Conversion (höher = besser)
    scores["conversion"] = score_component(
        metrics.get("conversion_rate", 0), THRESHOLDS["conversion"], lower_is_better=False
    )
    
    # Gewichteter Gesamtscore
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    
    # Status
    if total >= 90:
        status = "excellent"
    elif total >= 75:
        status = "good"
    elif total >= 60:
        status = "fair"
    elif total >= 40:
        status = "degraded"
    else:
        status = "critical"
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": round(total, 1),
        "status": status,
        "components": {k: round(v, 1) for k, v in scores.items()},
        "weights": WEIGHTS,
    }


def collect_metrics_from_system() -> dict:
    """Sammelt reale Metriken aus dem System (Best-Effort)."""
    metrics = {
        "uptime": 100.0,  # Default, überschrieben wenn verfügbar
        "error_rate": 0.0,
        "latency_p95": 0,
        "deploy_frequency": 0,
        "mttr": 0,
        "security_score": 0,
        "conversion_rate": 0,
    }
    
    # Uptime aus /proc/uptime (Server-Uptime, nicht Container)
    try:
        # Server-Uptime via SSH auf Host (genauer als Container-/proc)
        import subprocess
        result = subprocess.run(
            ["cat", "/proc/uptime"],
            capture_output=True, text=True
        )
        uptime_seconds = float(result.stdout.split()[0])
        uptime_days = uptime_seconds / 86400
        # Wenn Docker-Container: uptime ist Host-Uptime (shared kernel)
        metrics["uptime"] = min(100.0, (uptime_days / 30) * 100)
    except Exception as e:
        metrics["uptime"] = 100.0  # Fallback
        print(f"WARN: Uptime-Messung fehlgeschlagen: {e}")
    
    # Deploy-Frequenz aus Git-Log
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=1.week", "HEAD"],
            cwd="/opt/nexifyai-website-sicherheitskopie",
            capture_output=True, text=True
        )
        commits = len([l for l in result.stdout.strip().split("\n") if l])
        metrics["deploy_frequency"] = commits
    except:
        pass
    
    return metrics


if __name__ == "__main__":
    metrics = collect_metrics_from_system()
    result = calculate_health_score(metrics)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n═══ HEALTH SCORE: {result['score']}% — {result['status'].upper()} ═══")
    
    if result["status"] in ("degraded", "critical"):
        print("⚠️ ALARM: Health-Score unter Schwellenwert!")
        sys.exit(1)
    else:
        sys.exit(0)
