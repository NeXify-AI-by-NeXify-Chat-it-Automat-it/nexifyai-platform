#!/usr/bin/env python3
import json, logging, os, requests, sys
from datetime import datetime, timezone
log = logging.getLogger("gh-sync")
TOKEN = os.environ.get("DS_GITHUB_9569466F__TOKEN", "")
REPO = "nexifyai-dev/nexifyai-website-sicherheitskopie"
API = "https://api.github.com"
HDRS = {"Authorization": f"Bearer {TOKEN}","Accept":"application/vnd.github.v3+json"} if TOKEN else {}

def get_projects() -> list:
    if not TOKEN: return []
    r = requests.get(f"{API}/repos/{REPO}/projects", headers=HDRS, timeout=10)
    if r.status_code == 200: return [{"id":p["id"],"name":p["name"],"state":p["state"]} for p in r.json()]
    return []

def sync(state: dict = None) -> dict:
    projs = get_projects()
    if not projs: return {"status":"no_projects","note":"No token or no projects"}
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"projects":projs,"count":len(projs)}

def main():
    print(json.dumps(sync(), indent=2))
    return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
