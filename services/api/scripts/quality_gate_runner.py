#!/usr/bin/env python3
"""Automated Quality Gate Runner — runs gates 5-7 on every execution.
Called by agent_executor after each agent task. Stores results in Brain."""
import sys, json, os, requests
from datetime import datetime, timezone, timedelta

BRAIN = "http://localhost:6333/collections/nexifyai_brain/points"
AUTH = {"X-Internal-Auth": "nexifyai-local"}

def gate_5_performance(agent_id, task):
    """GATE 5: Performance check."""
    results = []
    try:
        # API health
        r = requests.get("http://localhost:8001/docs", timeout=3)
        results.append({"check": "api_reachable", "pass": r.status_code == 200})
        # Brain health
        r = requests.post("http://localhost:6333/collections/nexifyai_brain/points/count", json={}, timeout=3)
        cnt = r.json().get("result", {}).get("count", 0)
        results.append({"check": "brain_reachable", "pass": cnt > 100, "vectors": cnt})
    except Exception as e:
        results.append({"check": "infrastructure", "pass": False, "error": str(e)[:200]})
    return results

def gate_6_workflow(agent_id, task):
    """GATE 6: Workflow check."""
    results = []
    # Check agent has profile
    profile_path = f"/opt/nexifyai-website-sicherheitskopie/backend/agents/brain_agents/{agent_id}.md"
    results.append({"check": "profile_exists", "pass": os.path.exists(profile_path)})
    # Check order-workflow system is available
    check_path = "/opt/nexifyai-website-sicherheitskopie/docs/systems/sys-007-production-pipeline.md"
    results.append({"check": "workflow_spec_exists", "pass": os.path.exists(check_path)})
    return results

def gate_7_agent_quality(agent_id, task):
    """GATE 7: Agent quality check."""
    results = []
    profile_path = f"/opt/nexifyai-website-sicherheitskopie/backend/agents/brain_agents/{agent_id}.md"
    if os.path.exists(profile_path):
        size = os.path.getsize(profile_path)
        results.append({"check": "profile_size", "pass": size >= 4000, "size": size})
    else:
        results.append({"check": "profile_found", "pass": False})
    # Check agent has heartbeat
    try:
        r = requests.get("http://localhost:8642/health", timeout=3)
        results.append({"check": "gateway_reachable", "pass": r.status_code == 200})
    except:
        results.append({"check": "gateway_reachable", "pass": False})
    return results

def run_gates(agent_id, task):
    ts = datetime.now(timezone.utc).isoformat()
    all_results = {
        "gate_5_performance": gate_5_performance(agent_id, task),
        "gate_6_workflow": gate_6_workflow(agent_id, task),
        "gate_7_agent_quality": gate_7_agent_quality(agent_id, task),
    }
    # Calculate score
    total = 0
    count = 0
    blockers = []
    for gate_name, checks in all_results.items():
        for c in checks:
            count += 1
            if c["pass"]:
                total += 1
            else:
                blockers.append(gate_name + ": " + c["check"])

    score = total / max(count, 1)
    status = "approved" if score >= 0.85 else ("conditional" if score >= 0.70 else "blocked")

    # Store in Brain
    requests.put(BRAIN, json={"points": [{"id": 3100000 + int(datetime.now().timestamp()) % 1000000,
        "vector": [0.0]*1024, "payload": {"timestamp": ts, "topic": "quality-gate-run", "category": "quality",
        "agent": agent_id, "score": score, "status": status, "blockers": blockers,
        "title": f"QG: {agent_id} — {status} ({score:.0%})",
        "content": json.dumps({"results": all_results, "score": score, "blockers": blockers})}
    }]}, timeout=10)

    return {"score": score, "status": status, "blockers": blockers, "gate_results": all_results}

if __name__ == "__main__":
    agent = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    task = sys.argv[2] if len(sys.argv) > 2 else ""
    result = run_gates(agent, task)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] != "blocked" else 1)
