#!/usr/bin/env python3
"""Drift Detector — checks for structural drift in the repository.
Runs on every cycle. Reports to Brain."""
import json, os, requests, sys
from datetime import datetime, timezone

REQUIRED_DIRS = [
    "/opt/nexifyai-platform/apps/web/src/components",
    "/opt/nexifyai-platform/apps/web/src/pages",
    "/opt/nexifyai-platform/apps/web/src/i18n",
    "/opt/nexifyai-platform/runtime/reconciliation",
    "/opt/nexifyai-platform/runtime/convergence",
    "/opt/nexifyai-platform/runtime/governance",
]
FORBIDDEN_PATTERNS = [
    ".addr.",
    "process.env.REACT_APP",
]
REQUIRED_PATTERNS = ["?.", "ErrorBoundary", "lazy("]

def check_missing_dirs():
    missing = [d for d in REQUIRED_DIRS if not os.path.exists(d)]
    return missing

def check_unsafe_patterns():
    issues = []
    for root, dirs, files in os.walk("/opt/nexifyai-platform/apps/web/src"):
        for f in files:
            if f.endswith(('.jsx', '.js')):
                path = os.path.join(root, f)
                with open(path) as fh:
                    content = fh.read()
                for pat in FORBIDDEN_PATTERNS:
                    if pat in content and '?.' not in content:
                        issues.append(f"{path}: contains '{pat}' without optional chaining")
    return issues

def main():
    report = {"timestamp": datetime.now(timezone.utc).isoformat()}
    report["missing_dirs"] = check_missing_dirs()
    report["unsafe_patterns"] = check_unsafe_patterns()
    report["drift_detected"] = bool(report["missing_dirs"] or report["unsafe_patterns"])
    print(json.dumps(report, indent=2))
    # Report to Brain if drift detected
    if report["drift_detected"]:
        try:
            requests.post("http://localhost:6333/collections/nexifyai_brain/points", json={
                "points": [{
                    "id": int(datetime.now().timestamp() * 1000),
                    "payload": {"category": "governance", "title": "Drift Detected", "detail": str(report), "ts": report["timestamp"]}
                }]
            }, timeout=5)
        except: pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
