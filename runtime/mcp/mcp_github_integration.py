#!/usr/bin/env python3
"""mcp_github_integration.py -- GitHub MCP layer. Wraps all GitHub capabilities."""
import json, logging, os, requests
from mcp_gateway import get_gateway
from mcp_registry import get_registry
log = logging.getLogger("mcp-github")

TOKEN = os.environ.get("DS_GITHUB_9569466F__TOKEN","")
REPO = "nexifyai-dev/nexifyai-website-sicherheitskopie"
API = "https://api.github.com"
HDRS = {"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github.v3+json"} if TOKEN else {}

class MCPGitHubIntegration:
    def register(self):
        gw = get_gateway()
        reg = get_registry()
        gw.register_capability("github.issue.create", self._create_issue, {"domain":"github","governance":"required","audit":True})
        gw.register_capability("github.issue.list", self._list_issues, {"domain":"github","governance":"low"})
        gw.register_capability("github.pr.create", self._create_pr, {"domain":"github","governance":"required","audit":True,"rollback":True})
        gw.register_capability("github.pr.list", self._list_prs, {"domain":"github","governance":"low"})
        gw.register_capability("github.repo.info", self._repo_info, {"domain":"github","governance":"low"})
        for cap in ["github.issue.create","github.issue.list","github.pr.create","github.pr.list","github.repo.info"]:
            reg.register(cap, {"domain":"github"})
        log.info("GitHub MCP layer registered (5 capabilities)")

    def _create_issue(self, call_id, agent, title="auto issue", body="auto body", labels=None, **kw):
        if not TOKEN: return {"ok":False,"error":"no_token","call_id":call_id}
        try:
            r = requests.post(f"{API}/repos/{REPO}/issues", headers=HDRS, json={"title":title,"body":body,"labels":labels or ["auto-generated"]}, timeout=10)
            if r.status_code==201: d=r.json(); return {"ok":True,"num":d["number"],"url":d["html_url"],"call_id":call_id}
            return {"ok":False,"code":r.status_code,"call_id":call_id}
        except Exception as e: return {"ok":False,"error":str(e)[:50],"call_id":call_id}

    def _list_issues(self, call_id, agent, state="open", **kw):
        if not TOKEN: return {"ok":False,"error":"no_token"}
        try:
            r = requests.get(f"{API}/repos/{REPO}/issues", headers=HDRS, params={"state":state,"per_page":5}, timeout=10)
            if r.status_code==200: return {"ok":True,"issues":[{"num":i["number"],"title":i["title"],"state":i["state"]} for i in r.json()],"call_id":call_id}
            return {"ok":False,"code":r.status_code}
        except Exception as e: return {"ok":False,"error":str(e)[:50]}

    def _create_pr(self, call_id, agent, title="auto pr", head="auto-change", base="main", **kw):
        if not TOKEN: return {"ok":False,"error":"no_token"}
        try:
            r = requests.post(f"{API}/repos/{REPO}/pulls", headers=HDRS, json={"title":title,"head":head,"base":base,"body":"Autonomous PR"}, timeout=10)
            if r.status_code==201: d=r.json(); return {"ok":True,"num":d["number"],"url":d["html_url"],"call_id":call_id}
            return {"ok":False,"code":r.status_code,"call_id":call_id}
        except Exception as e: return {"ok":False,"error":str(e)[:50],"call_id":call_id}

    def _list_prs(self, call_id, agent, state="open", **kw):
        if not TOKEN: return {"ok":False,"error":"no_token"}
        try: r = requests.get(f"{API}/repos/{REPO}/pulls", headers=HDRS, params={"state":state}, timeout=10); return {"ok":r.status_code==200,"prs":[{"num":p["number"],"title":p["title"]} for p in r.json()],"call_id":call_id}
        except Exception as e: return {"ok":False,"error":str(e)[:50]}

    def _repo_info(self, call_id, agent, **kw):
        if not TOKEN: return {"ok":False,"error":"no_token"}
        try: r = requests.get(f"{API}/repos/{REPO}", headers=HDRS, timeout=10); d=r.json(); return {"ok":True,"full_name":d.get("full_name"),"stars":d.get("stargazers_count"),"open_issues":d.get("open_issues_count"),"call_id":call_id}
        except Exception as e: return {"ok":False,"error":str(e)[:50]}

GITHUB = MCPGitHubIntegration()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); GITHUB.register()
    gw = get_gateway(); r = gw.invoke("github.repo.info", agent="test")
    print(json.dumps(r, indent=2)[:300])
