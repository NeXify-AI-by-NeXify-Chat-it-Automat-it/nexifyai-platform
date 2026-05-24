#!/usr/bin/env python3
import os, re, json
from datetime import datetime, timezone
SIGS = [
    r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
]
class RSD:
    def __init__(self):
        self.log = "/services/runtime/security/scanning/runtime_detections.json"
    def scan(self, text, source="unknown"):
        hits = []
        for sig in SIGS:
            for m in re.finditer(sig, text):
                s = max(0, m.start()-30)
                e = min(len(text), m.end()+30)
                ctx = text[s:e].replace("\n"," ").strip()
                hits.append({"pat": sig[:20], "src": source, "ctx": ctx[:80]})
        return hits
    def scan_procs(self, n=10):
        r = []
        for d in os.listdir("/proc"):
            if not d.isdigit(): continue
            if len(r) >= n: break
            p = "/proc/"+d+"/environ"
            if os.path.exists(p) and os.access(p, os.R_OK):
                try:
                    with open(p, "rb") as f: data = f.read(65536)
                    t = data.decode("utf-8", errors="replace")
                    h = self.scan(t, "proc/"+d)
                    if h: r.extend(h)
                except: pass
        return r
    def save(self, hits):
        if not hits: return
        ex = []
        if os.path.exists(self.log):
            with open(self.log) as f: ex = json.load(f)
        ex.append({"ts": datetime.now(timezone.utc).isoformat(), "hits": hits})
        if len(ex) > 100: ex = ex[-100:]
        with open(self.log, "w") as f: json.dump(ex, f, indent=2)
if __name__ == "__main__":
    d = RSD()
    hits = d.scan("ghp_test_token", "test")
    print('{"hits":%d}' % len(hits))
