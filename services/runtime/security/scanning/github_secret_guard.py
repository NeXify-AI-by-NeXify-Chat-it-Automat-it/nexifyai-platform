#!/usr/bin/env python3
"""GitHub Secret Guard — pre-commit secret detection."""
import re, subprocess, sys
PATS = [
    (r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}', 'github_token'),
    (r'github_pat_[A-Za-z0-9_]{22,}', 'github_pat'),
    (r'-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', 'private_key'),
    (r'DS_[A-Z0-9_]{10,}__[A-Z_]{3,}', 'ds_env_ref'),
]
def main():
    r = subprocess.run(["git", "diff", "--cached", "--diff-filter=ACM"], capture_output=True, text=True, timeout=10)
    issues = []
    for pat, name in PATS:
        for m in re.finditer(pat, r.stdout):
            s = max(0, m.start()-40); e = min(len(r.stdout), m.end()+40)
            issues.append({"pattern": name, "ctx": r.stdout[s:e].replace("\n"," ").strip()[:100]})
    if issues:
        print("SECRETS IN STAGED CHANGES:")
        for i in issues: print(f"  [{i['pattern']}] {i['ctx']}")
        sys.exit(1)
    print("OK - no secrets in staged changes")

if __name__ == "__main__":
    main()
