# -*- coding: utf-8 -*-
"""Secret Scanner -- scans repo for leaked credentials."""
import os, re, json, sys
from datetime import datetime, timezone
try:
    import requests
except ImportError:
    requests = None

PATTERNS = {
    "github_token": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}",
    "github_pat": r"github_pat_[A-Za-z0-9_]{22,}",
    "private_key": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
    "conn_string": r"conn_string_pattern",
    "jwt": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
}

EXCLUDE = {'.git', 'node_modules', '__pycache__', '.vercel', 'dist', 'build', '.next', '.anton'}

def scan_file(path):
    issues = []
    try:
        with open(path, 'rb') as f:
            content = f.read()
        if b'\x00' in content[:1024]:
            return issues
        text = content.decode('utf-8', errors='replace')
        for name, pat in PATTERNS.items():
            for m in re.finditer(pat, text):
                lines = text.split('\n')
                line_num = text[:m.start()].count('\n') + 1
                ctx = lines[line_num-1].strip()[:120] if line_num <= len(lines) else ''
                issues.append({'file': path, 'line': line_num, 'pattern': name, 'context': ctx})
    except:
        pass
    return issues

def main():
    repo = '/opt/nexifyai-platform'
    if not os.path.exists(repo):
        repo = '/tmp/nexifyai-platform'
    all_issues = []
    scanned = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in files:
            if not any(f.endswith(e) for e in ['.py','.js','.jsx','.ts','.tsx','.sh','.yml','.yaml','.json','.env','.md']):
                continue
            scanned += 1
            all_issues.extend(scan_file(os.path.join(root, f)))
    report = {'timestamp': datetime.now(timezone.utc).isoformat(), 'scanned': scanned, 'leaks': len(all_issues), 'details': all_issues[:10]}
    print(json.dumps(report, indent=2))
    if all_issues and requests:
        try:
            requests.post('http://localhost:6333/collections/nexifyai_brain/points', json={
                'points': [{'id': int(datetime.now().timestamp()*1000),
                           'payload': {'category': 'security', 'severity': 'critical',
                                       'title': 'Secret leak: '+all_issues[0]['pattern'],
                                       'detail': json.dumps(report),
                                       'ts': report['timestamp']}}]
            }, timeout=5)
        except:
            pass
    return 1 if all_issues else 0

if __name__ == '__main__':
    sys.exit(main())