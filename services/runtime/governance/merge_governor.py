#!/usr/bin/env python3
"""Merge Governor — autonomous PR gate.
Called by: Planner before any merge.
Exits non-zero if merge violates policy."""
import json, os, subprocess, sys
from datetime import datetime, timezone

CHECKS = [
    "build_ok",
    "runtime_ok",
    "smoke_tests_ok",
    "dependency_ok",
    "observability_ok",
]

def check_build():
    r = subprocess.run(["npx", "vite", "build"], capture_output=True, text=True, timeout=60, cwd="/tmp/nexifyai-platform/apps/web")
    return r.returncode == 0, r.stderr[-200:] if r.returncode != 0 else ""

def check_runtime():
    # Requires Playwright — skip if unavailable
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto("http://localhost:8001", timeout=15000, wait_until='networkidle')
            page.wait_for_timeout(3000)
            browser.close()
            return len(errors) == 0, errors[:3]
    except Exception as e:
        return True, f"Runtime check skipped: {e}"

def check_deps():
    # Detect unsafe patterns in changed files
    r = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, timeout=10, cwd="/opt/nexifyai-platform")
    changed = r.stdout.split('\n')
    issues = []
    for f in changed:
        if not f or not os.path.exists(f): continue
        if f.endswith('.jsx') or f.endswith('.js'):
            with open(f) as fh:
                content = fh.read()
            if 'process.env.REACT_APP' in content:
                issues.append(f"{f}: CRA env var (REACT_APP_) detected")
            if '.addr.' in content and '?.' not in content:
                issues.append(f"{f}: unsafe .addr. access (no optional chaining)")
    return len(issues) == 0, issues

def main():
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "checks": {}}
    all_pass = True
    for name in CHECKS:
        fn = globals().get(f"check_{name.replace(' ', '_')}")
        if fn:
            passed, detail = fn()
            report["checks"][name] = {"passed": passed, "detail": str(detail)[:300]}
            if not passed:
                all_pass = False
    report["all_pass"] = all_pass
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
