#!/usr/bin/env python3
"""Risk Classifier — assesses risk of autonomous changes."""
import json, sys
from datetime import datetime, timezone

RISK_RULES = {
    "build_break": {"weight": 10, "keywords": ["package.json", "vite.config", "webpack"]},
    "runtime_change": {"weight": 8, "keywords": ["main.jsx", "App.jsx", "ErrorBoundary"]},
    "dependency_change": {"weight": 7, "keywords": ["package.json", "requirements", "Dockerfile"]},
    "governance_change": {"weight": 9, "keywords": ["governance", "policy", "constitution"]},
    "infrastructure_change": {"weight": 8, "keywords": ["systemd", "service", "Dockerfile", "nginx"]},
    "test_change": {"weight": -3, "keywords": ["test", "spec", "playwright"]},
    "documentation_change": {"weight": -5, "keywords": ["README", "docs", ".md"]},
}

def classify(changed_files):
    score = 1
    reasons = []
    for f in changed_files:
        for rule_name, rule in RISK_RULES.items():
            for kw in rule["keywords"]:
                if kw.lower() in f.lower():
                    score += rule["weight"]
                    reasons.append(f"{f}: {rule_name}")
    return min(max(score, 1), 10), reasons

if __name__ == "__main__":
    import subprocess
    r = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, timeout=10, cwd="/opt/nexifyai-platform")
    changed = [l for l in r.stdout.split('\n') if l]
    score, reasons = classify(changed)
    print(json.dumps({
        "risk_score": score,
        "risk_level": "critical" if score >= 8 else "high" if score >= 5 else "medium" if score >= 3 else "low",
        "files_changed": len(changed),
        "reasons": reasons[:5],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, indent=2))
