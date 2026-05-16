#!/usr/bin/env python3
"""System State Monitor — updates Brain every 60s for live agent knowledge."""
import subprocess, json, requests, os, time
from datetime import datetime, timezone

def get_state():
    state = {"timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        r = requests.get("http://localhost:8001/api/orchestration/health/full", timeout=5)
        state["backend"] = r.json()
    except:
        state["backend"] = {"overall": "unknown"}
    try:
        r = requests.get("http://localhost:8642/health", timeout=3)
        state["hermes"] = r.json()
    except:
        state["hermes"] = {"status": "unknown"}
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}:{{.Status}}"], capture_output=True, text=True, timeout=5)
    state["containers"] = [c.strip() for c in result.stdout.split("\n") if c.strip()]
    result = subprocess.run(["uptime"], capture_output=True, text=True, timeout=3)
    state["system"] = result.stdout.strip()
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=3)
    parts = result.stdout.split("\n")
    state["disk"] = parts[1].split() if len(parts) > 1 else []
    return state

def write_brain(state):
    ts = int(time.time()) % 100000
    try:
        requests.put("http://localhost:6333/collections/nexifyai_brain/points?wait=true",
            json={"points": [{"id": 2000000 + ts, "vector": [0.0]*4096,
            "payload": {"category":"live_monitoring","source":"system_monitor",
            "content": json.dumps(state), "timestamp": state["timestamp"]}}]}, timeout=5)
    except:
        pass
    try:
        requests.put("http://localhost:6333/collections/nexifyai_memories/points?wait=true",
            json={"points": [{"id": 3000000 + ts, "vector": [0.0]*1024,
            "payload": {"category":"live_state","source":"system_monitor",
            "content": json.dumps({"backend":state.get("backend",{}).get("overall","?"),
            "hermes":state.get("hermes",{}).get("status","?"),
            "containers":len(state.get("containers",[])),"timestamp":state["timestamp"]}),
            "timestamp": state["timestamp"]}}]}, timeout=5)
    except:
        pass

if __name__ == "__main__":
    s = get_state()
    write_brain(s)
    print(f"MONITOR: backend={s.get('backend',{}).get('overall','?')} containers={len(s.get('containers',[]))} {s['timestamp']}")
