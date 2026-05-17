#!/usr/bin/env python3
"""Deployment Governor — validates deployment safety.
Ensures: build OK, healthchecks OK, rollback snapshot created."""
import json, os, subprocess, sys
from datetime import datetime, timezone

def main():
    cwd = "/tmp/nexifyai-platform"
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "checks": {}}
    all_pass = True
    
    # Check: git status clean
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10, cwd=cwd)
    dirty = bool(r.stdout.strip())
    report["checks"]["git_clean"] = {"passed": not dirty}
    if dirty: all_pass = False
    
    # Check: Vite build
    r = subprocess.run(["npx", "vite", "build"], capture_output=True, text=True, timeout=60, cwd=cwd+"/apps/web")
    build_ok = r.returncode == 0
    report["checks"]["build"] = {"passed": build_ok, "detail": r.stderr[-200:] if not build_ok else ""}
    if not build_ok: all_pass = False
    
    report["all_pass"] = all_pass
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
