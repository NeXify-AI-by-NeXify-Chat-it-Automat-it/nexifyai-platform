#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone, timedelta
import requests, uuid

LOG = "/services/runtime/security/audit/events.log"

class AnomalyDetector:
    def __init__(self):
        self.thresholds = {
            "max_access_per_min": 30,
            "max_failed_per_hour": 10,
            "max_workers_per_secret": 5,
        }
    def analyze(self, window_minutes=60):
        if not os.path.exists(LOG): return {"status": "no_data"}
        with open(LOG) as f:
            lines = f.readlines()
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=window_minutes)
        recent = []
        for l in lines:
            try:
                e = json.loads(l)
                if datetime.fromisoformat(e["ts"]) > cutoff:
                    recent.append(e)
            except: pass
        # Per-secret access count
        per_secret = {}
        per_worker = {}
        failed = 0
        for e in recent:
            s = e.get("secret","unknown")
            w = e.get("worker","unknown")
            per_secret[s] = per_secret.get(s,0)+1
            per_worker[w] = per_worker.get(w,0)+1
            if not e.get("found", True):
                failed += 1
        anomalies = []
        for s, c in per_secret.items():
            if c > self.thresholds["max_access_per_min"] * window_minutes:
                anomalies.append({"type": "rate", "secret": s, "count": c, "window_min": window_minutes})
        for w, c in per_worker.items():
            if c > self.thresholds["max_access_per_min"] * window_minutes * 2:
                anomalies.append({"type": "worker_rate", "worker": w, "count": c})
        if failed > self.thresholds["max_failed_per_hour"]:
            anomalies.append({"type": "failed_lookups", "count": failed})
        if anomalies:
            self._report_brain(anomalies)
        return {"ts": now.isoformat(), "events_in_window": len(recent),
                "anomalies": anomalies, "top_secrets": dict(sorted(per_secret.items(), key=lambda x:-x[1])[:5])}
    def _report_brain(self, anomalies):
        try:
            requests.put("http://localhost:6333/collections/nexifyai_brain/points", json={
                "points": [{"id": str(uuid.uuid4()), "vector": [0.0]*384,
                           "payload": {"category": "security", "severity": "warning",
                                       "title": f"Secret anomaly: {len(anomalies)} issues",
                                       "detail": json.dumps(anomalies),
                                       "ts": datetime.now(timezone.utc).isoformat()}}]
            }, timeout=3)
        except: pass

if __name__ == "__main__":
    d = AnomalyDetector()
    print(json.dumps(d.analyze(5), indent=2))
