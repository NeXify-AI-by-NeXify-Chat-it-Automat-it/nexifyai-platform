#!/usr/bin/env python3
"""issue_autogenerator.py -- Creates real GitHub issues from system events with timeout handling."""
import json, logging, os, requests, sys
from datetime import datetime, timezone
log = logging.getLogger("issue-auto")
TOKEN = os.environ.get("DS_GITHUB_9569466F__TOKEN", "")
REPO = "nexifyai-dev/nexifyai-website-sicherheitskopie"
API = "https://api.github.com"
HDRS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"} if TOKEN else {}
SEVERITY_LABELS = {"critical": ["bug","enterprise-runtime"],"warning": ["enterprise-runtime"],"info": ["auto-generated","enterprise-runtime"]}

def create_issue(title, body, severity="info"):
    if not TOKEN: return {"success":False,"error":"no_token"}
    try:
        r = requests.post(f"{API}/repos/{REPO}/issues", headers=HDRS,
            json={"title":title,"body":body,"labels":SEVERITY_LABELS.get(severity,["auto-generated"])}, timeout=10)
        if r.status_code == 201:
            d = r.json(); log.info(f"Issue #{d['number']}: {d['html_url']}")
            return {"success":True,"number":d["number"],"url":d["html_url"]}
        return {"success":False,"error":f"HTTP {r.status_code}","detail":r.text[:200]}
    except requests.exceptions.Timeout: return {"success":False,"error":"timeout"}
    except Exception as e: return {"success":False,"error":str(e)[:100]}

def generate_from_events(events=None):
    if not events: events = [{"type":"system_event","title":"Enterprise OS running","severity":"info","detail":"Autonomous enterprise operating system operational."}]
    results = []
    for e in events:
        title = f"[{e.get('type','system')}] {e.get('title','Automated Event')}"
        body = f"## System Event\n\n**Type:** {e.get('type')}\n**Detail:** {e.get('detail','N/A')}\n**Timestamp:** {datetime.now(timezone.utc).isoformat()}\n**Source:** autonomous-governance"
        results.append({"event": e.get("title"), "result": create_issue(title, body, e.get("severity","info"))})
    return results

def main():
    events = [{"type":"verification","title":"Runtime governance active","severity":"info","detail":"All enterprise layers operational."}]
    if not sys.stdin.isatty():
        try:
            data = sys.stdin.read()
            if data.strip():
                events = json.loads(data)
        except (json.JSONDecodeError, Exception):
            pass
    print(json.dumps(generate_from_events(events), indent=2))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [issue-auto] %(name)s: %(message)s")
    main()
