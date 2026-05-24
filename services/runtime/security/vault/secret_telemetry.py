#!/usr/bin/env python3
"""Runtime Secret Telemetry -- tracks secret usage patterns, detects anomalies."""
import json, os, sys
from datetime import datetime, timezone, timedelta

class SecretTelemetry:
    """Analyzes audit log for anomalies and usage patterns."""
    def __init__(self):
        self.audit_path = "/services/runtime/security/audit/events.log"
        self.report_path = "/services/runtime/security/audit/telemetry.json"

    def analyze(self):
        if not os.path.exists(self.audit_path):
            return {"status": "no_data"}
        with open(self.audit_path) as f:
            events = [json.loads(l) for l in f.readlines() if l.strip()]

        now = datetime.now(timezone.utc)
        last_hour = [e for e in events if (now - datetime.fromisoformat(e["ts"])).total_seconds() < 3600]

        # Top accessed secrets
        counts = {}
        workers = {}
        for e in events:
            key = e.get("key", "unknown")
            counts[key] = counts.get(key, 0) + 1
            w = e.get("worker", "unknown")
            workers[w] = workers.get(w, 0) + 1

        # Anomaly: secret accessed >50 times in window
        anomalies = []
        recent_counts = {}
        for e in last_hour:
            key = e.get("key", "unknown")
            recent_counts[key] = recent_counts.get(key, 0) + 1
        for key, count in recent_counts.items():
            if count > 50:
                anomalies.append({"secret": key, "access_last_hour": count, "reason": "rate_anomaly"})

        return {
            "timestamp": now.isoformat(),
            "total_events": len(events),
            "events_last_hour": len(last_hour),
            "top_secrets": dict(sorted(counts.items(), key=lambda x: -x[1])[:10]),
            "top_workers": dict(sorted(workers.items(), key=lambda x: -x[1])[:5]),
            "anomalies": anomalies[:5],
            "unique_secrets": len(counts),
            "unique_workers": len(workers),
        }

    def report_to_brain(self):
        try:
            import requests, uuid
            data = self.analyze()
            if data.get("anomalies"):
                requests.put("http://localhost:6333/collections/nexifyai_brain/points", json={
                    "points": [{"id": str(uuid.uuid4()), "vector": [0.0]*384,
                               "payload": {"category": "security", "severity": "warning",
                                           "title": "Secret access anomaly",
                                           "detail": json.dumps(data["anomalies"]),
                                           "ts": data["timestamp"]}}]
                }, timeout=5)
        except:
            pass


if __name__ == "__main__":
    t = SecretTelemetry()
    print(json.dumps(t.analyze(), indent=2))
