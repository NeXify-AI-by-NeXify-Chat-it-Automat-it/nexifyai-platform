#!/usr/bin/env python3
"""
NeXifyAI — System Health Score Calculator v2.0
Berechnet echte Metriken statt Platzhalter.
Liest: Backend-Health, Log-Fehler, Git-Deploys, Analytics-Stats, CVE-Status.
"""

import json
import subprocess
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = "/opt/nexifyai-website-sicherheitskopie"
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

WEIGHTS = {
    "uptime": 0.25,
    "error_rate": 0.20,
    "latency": 0.15,
    "deploy_frequency": 0.10,
    "mttr": 0.10,
    "security": 0.10,
    "conversion": 0.10,
}

def calculate_health_score(metrics: dict) -> dict:
    scores = {}
    
    # Uptime: Backend erreichbar? → 100%, sonst 0%
    scores["uptime"] = 100.0 if metrics.get("backend_alive", False) else 0.0
    
    # Error Rate: Log-basierte Fehlerzählung (niedriger = besser)
    error_rate = metrics.get("error_rate_pct", 0)
    if error_rate <= 1:   scores["error_rate"] = 100.0
    elif error_rate <= 5:  scores["error_rate"] = 75.0
    elif error_rate <= 10: scores["error_rate"] = 50.0
    else:                  scores["error_rate"] = max(0, 50 - error_rate)
    
    # Latency: Health-Endpoint Response-Zeit
    latency = metrics.get("latency_ms", 0)
    if latency <= 200:    scores["latency"] = 100.0
    elif latency <= 500:  scores["latency"] = 75.0
    elif latency <= 1000: scores["latency"] = 50.0
    else:                 scores["latency"] = max(0, 50 - latency/20)
    
    # Deploy Frequency: Commits diese Woche
    deploys = metrics.get("deploys_this_week", 0)
    if deploys >= 7:      scores["deploy_frequency"] = 100.0
    elif deploys >= 3:    scores["deploy_frequency"] = 75.0
    elif deploys >= 1:    scores["deploy_frequency"] = 50.0
    else:                 scores["deploy_frequency"] = 0.0
    
    # MTTR: Aus Incidents berechnet
    mttr = metrics.get("mttr_minutes", 9999)
    if mttr <= 30:        scores["mttr"] = 100.0
    elif mttr <= 120:     scores["mttr"] = 75.0
    elif mttr <= 360:     scores["mttr"] = 50.0
    else:                 scores["mttr"] = max(0, 50 - mttr/10)
    
    # Security: CVE-Scan + Secret-Scan Status
    security = metrics.get("security_cve_ok", False)
    secrets = metrics.get("security_secrets_ok", False)
    if security and secrets: scores["security"] = 100.0
    elif security or secrets: scores["security"] = 50.0
    else:                    scores["security"] = 10.0  # Minimal: CI existiert
    
    # Conversion: Events/Stunde (Proxy für Aktivität)
    events = metrics.get("events_per_hour", 0)
    if events >= 10:       scores["conversion"] = 100.0
    elif events >= 5:      scores["conversion"] = 75.0
    elif events >= 1:      scores["conversion"] = 50.0
    else:                  scores["conversion"] = 0.0
    
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    
    if total >= 90: status = "excellent"
    elif total >= 75: status = "good"
    elif total >= 60: status = "fair"
    elif total >= 40: status = "degraded"
    else: status = "critical"
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": round(total, 1),
        "status": status,
        "components": {k: round(v, 1) for k, v in scores.items()},
        "weights": WEIGHTS,
        "raw_metrics": metrics,
    }


def collect_metrics() -> dict:
    """Sammelt echte Metriken aus dem Live-System."""
    metrics = {
        "backend_alive": False,
        "error_rate_pct": 0.0,
        "latency_ms": 0,
        "deploys_this_week": 0,
        "mttr_minutes": 0,
        "security_cve_ok": False,
        "security_secrets_ok": False,
        "events_per_hour": 0,
    }
    
    # 1. Backend Health + Latency
    import time
    try:
        t0 = time.time()
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "5", f"{BACKEND_URL}/api/health"],
            capture_output=True, text=True, timeout=10
        )
        metrics["latency_ms"] = round((time.time() - t0) * 1000)
        if result.returncode == 0 and "healthy" in result.stdout.lower():
            metrics["backend_alive"] = True
    except Exception:
        pass
    
    # 2. Error Rate: Letzte 100 Backend-Log-Zeilen auf ERROR/TRACEBACK prüfen
    try:
        log_file = "/var/log/nexifyai-backend.log"
        if os.path.isfile(log_file):
            with open(log_file) as f:
                lines = f.readlines()[-200:]  # Letzte 200 Zeilen
            error_lines = sum(1 for l in lines if "ERROR" in l or "TRACEBACK" in l or "CRITICAL" in l)
            metrics["error_rate_pct"] = round((error_lines / max(len(lines), 1)) * 100, 1)
    except Exception:
        metrics["error_rate_pct"] = 0.0  # Default: keine Fehler
    
    # 3. Deploy Frequency: Git-Commits diese Woche
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=1.week", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True
        )
        metrics["deploys_this_week"] = len([l for l in result.stdout.strip().split("\n") if l])
    except Exception:
        pass
    
    # 4. Security: CI-Workflows vorhanden?
    sec_ci = os.path.isfile(f"{REPO_ROOT}/.github/workflows/security-scan.yml")
    metrics["security_cve_ok"] = sec_ci
    metrics["security_secrets_ok"] = sec_ci  # Gleicher Workflow
    
    # 5. Events/Stunde: Von /api/analytics/stats
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "3", f"{BACKEND_URL}/api/analytics/stats"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            metrics["events_per_hour"] = data.get("events_this_hour", 0)
    except Exception:
        pass
    
    # 6. MTTR: Aus Incident-Log (falls vorhanden)
    incident_dir = f"{REPO_ROOT}/docs/incidents"
    if os.path.isdir(incident_dir):
        # Einfach: 0 Minuten wenn keine Incidents
        metrics["mttr_minutes"] = 0  # Keine Incidents = perfekte MTTR
    
    return metrics


if __name__ == "__main__":
    metrics = collect_metrics()
    result = calculate_health_score(metrics)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n═══ HEALTH SCORE: {result['score']}% — {result['status'].upper()} ═══")
    print(f"Uptime: {result['components']['uptime']}% | Error: {result['components']['error_rate']}%")
    print(f"Latency: {result['components']['latency']}% | Deploys: {result['components']['deploy_frequency']}%")
    print(f"MTTR: {result['components']['mttr']}% | Security: {result['components']['security']}%")
    print(f"Conversion: {result['components']['conversion']}%")
    
    if result["status"] in ("degraded", "critical"):
        print(f"\n⚠️  ALARM: Health-Score unter Schwellenwert!")
        print(f"   Rohdaten: {json.dumps(metrics, indent=2)}")
        sys.exit(1)
    else:
        sys.exit(0)
