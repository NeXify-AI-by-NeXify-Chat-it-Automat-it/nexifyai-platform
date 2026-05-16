#!/usr/bin/env python3
"""Daily memories cleanup — delete entries older than 7 days, cap at 5000."""
import requests, json
from datetime import datetime, timedelta, timezone

QD = "http://localhost:6333"
COL = "nexifyai_memories"
CUTOFF = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
MAX_LIMIT = 5000

# 1. Count
r = requests.post(f"{QD}/collections/{COL}/points/count", json={})
cnt = r.json().get("result", {}).get("count", 0)
print(f"Memories before cleanup: {cnt}")

# 2. Delete old entries
r = requests.post(f"{QD}/collections/{COL}/points/scroll", json={
    "limit": 500, "with_payload": True,
    "filter": {"must": [{"key": "timestamp", "range": {"lt": CUTOFF}}]}
}, timeout=30)
old = r.json().get("result", {}).get("points", [])
if old:
    ids = [p["id"] for p in old]
    requests.post(f"{QD}/collections/{COL}/points/delete", json={"points": ids})
    print(f"Deleted {len(ids)} entries older than {CUTOFF[:10]}")

# 3. Cap at MAX_LIMIT (FIFO)
r = requests.post(f"{QD}/collections/{COL}/points/count", json={})
cnt = r.json().get("result", {}).get("count", 0)
if cnt > MAX_LIMIT:
    excess = cnt - MAX_LIMIT
    # Scroll oldest
    r = requests.post(f"{QD}/collections/{COL}/points/scroll", json={
        "limit": excess, "with_payload": False,
        "order_by": "timestamp"
    }, timeout=30)
    old_ids = [p["id"] for p in r.json().get("result", {}).get("points", [])]
    if old_ids:
        requests.post(f"{QD}/collections/{COL}/points/delete", json={"points": old_ids})
        print(f"Capped: removed {len(old_ids)} oldest entries (limit={MAX_LIMIT})")

r = requests.post(f"{QD}/collections/{COL}/points/count", json={})
print(f"Memories after cleanup: {r.json().get('result', {}).get('count', 0)}")
