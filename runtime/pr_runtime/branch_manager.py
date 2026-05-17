#!/usr/bin/env python3
"""branch_manager.py -- Manages git branches for autonomous PR creation."""
import json, logging, os, subprocess
log = logging.getLogger("branch-mgr")

class BranchManager:
    def __init__(self, repo_path="/opt/nexifyai-platform"):
        self.repo_path = repo_path
    def ensure_branch(self, branch_name="auto-change"):
        try:
            r = subprocess.run(["git","checkout","-B",branch_name], cwd=self.repo_path, capture_output=True, text=True, timeout=10)
            return {"ok": r.returncode==0, "branch": branch_name, "output": r.stdout[:200]}
        except Exception as e: return {"ok":False,"error":str(e)[:50]}
    def commit_and_push(self, message="auto: autonomous change", branch="auto-change"):
        try:
            subprocess.run(["git","add","-A"], cwd=self.repo_path, capture_output=True, timeout=10)
            r = subprocess.run(["git","commit","-m",message], cwd=self.repo_path, capture_output=True, text=True, timeout=10)
            subprocess.run(["git","push","origin",branch,"-f"], cwd=self.repo_path, capture_output=True, timeout=30)
            return {"ok":r.returncode==0,"commit":r.stdout[:100] if r.returncode==0 else r.stderr[:100]}
        except Exception as e: return {"ok":False,"error":str(e)[:50]}

if __name__ == "__main__":
    import sys
    bm = BranchManager()
    print(json.dumps(bm.ensure_branch()))
