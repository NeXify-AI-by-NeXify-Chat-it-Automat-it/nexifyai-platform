#!/usr/bin/env python3
import glob, subprocess, json, sys, os
from datetime import datetime, timezone
import requests

LIVE_DIR = "/etc/letsencrypt/live"
WARN_DAYS = 30
CRIT_DAYS = 14
BRAIN = "http://localhost:6333/collections/nexifyai_brain/points"
KUMA = os.environ.get("DS_KUMA_DDA57B74__WEBHOOK_URL", "")

def check_cert(path):
    try:
        r = subprocess.run(["openssl", "x509", "-enddate", "-noout", "-in", path],
                          capture_output=True, text=True, timeout=5)
        line = r.stdout.strip()
        if "notAfter=" in line:
            date_str = line.split("notAfter=")[1]
            expiry = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            days = (expiry - datetime.now(timezone.utc)).days
            return {"days_left": days, "expiry": expiry.isoformat(), "ok": True}
    except:
        pass
    return {"days_left": 0, "expiry": None, "ok": False}

def main():
    certs = glob.glob(LIVE_DIR + "/*/cert.pem")
    results, alerts = [], []
    for cert_path in certs:
        domain = cert_path.split("/")[-2]
        r = check_cert(cert_path)
        r["domain"] = domain
        results.append(r)
        if not r["ok"]:
            alerts.append("ERROR: " + domain + " cert unreadable")
        elif r["days_left"] < CRIT_DAYS:
            alerts.append("CRITICAL: " + domain + " " + str(r["days_left"]) + "d")
        elif r["days_left"] < WARN_DAYS:
            alerts.append("WARNING: " + domain + " " + str(r["days_left"]) + "d")
    ts = datetime.now(timezone.utc).isoformat()
    status = "critical" if any("CRITICAL" in a for a in alerts) else ("warning" if alerts else "ok")
    msg = "SSL: " + str(len(certs)) + " certs checked, " + str(len(alerts)) + " alerts"
    try:
        requests.put(BRAIN, json={"points": [{"id": 3000000 + int(datetime.now().timestamp()) % 1000000,
            "vector": [0.0]*1024, "payload": {"timestamp": ts, "topic": "ssl-check-daily",
            "category": "infrastructure", "title": msg,
            "content": json.dumps({"results": results, "alerts": alerts}), "status": status}}]}, timeout=10)
    except:
        pass
    if alerts and KUMA:
        requests.post(KUMA, json={"message": " | ".join(alerts)}, timeout=10)
    print(msg)
    for r in results:
        print("  " + r["domain"] + ": " + str(r["days_left"]) + "d")
    for a in alerts:
        print(a)
    return 1 if status == "critical" else 0

if __name__ == "__main__":
    sys.exit(main())
