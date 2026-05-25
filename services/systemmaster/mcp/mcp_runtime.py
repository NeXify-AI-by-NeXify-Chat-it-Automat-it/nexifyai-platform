#!/venv/bin/python3
"""mcp_runtime.py — MCP Capability Gateway. 25+ echte Capabilities."""
import sys, json, logging, os, subprocess, threading, time, urllib.request
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [mcp] %(levelname)s: %(message)s")
log = logging.getLogger("mcp")

class MCPGateway:
    def __init__(self):
        self.bus = get_bus()
        self.bus.subscribe("mcp.execute", self._on_execute, "mcp:gateway")
        self.bus.subscribe("mcp.query", self._on_query, "mcp:gateway")
        self._caps = self._discover()
        log.info("MCP ready: %d capabilities", len(self._caps))

    def _discover(self):
        caps = {}
        caps["systemd.service.status"] = {"type":"query","desc":"Check service status"}
        caps["systemd.service.restart"] = {"type":"exec","desc":"Restart service"}
        caps["systemd.list"] = {"type":"query","desc":"List nexify services"}
        caps["file.read"] = {"type":"query","desc":"Read file"}
        caps["file.write"] = {"type":"exec","desc":"Write file"}
        caps["file.exists"] = {"type":"query","desc":"Check file exists"}
        caps["process.list"] = {"type":"query","desc":"List processes"}
        caps["log.tail"] = {"type":"query","desc":"Tail log file"}
        caps["state.get"] = {"type":"query","desc":"Read state"}
        caps["state.set"] = {"type":"exec","desc":"Write state"}
        caps["env.get"] = {"type":"query","desc":"Read env var"}
        caps["network.ping"] = {"type":"query","desc":"HTTP ping"}

        # Externe Systeme (Credentials from Data Vault)
        if os.environ.get("DS_GITHUB_35B6CCD0__TOKEN") or os.environ.get("DS_GITHUB_9569466F__TOKEN"):
            caps["github.repos"] = {"type":"query","desc":"List repos"}
            caps["github.issues"] = {"type":"query","desc":"List issues"}
            caps["github.prs"] = {"type":"query","desc":"List PRs"}
            caps["github.orgs"] = {"type":"query","desc":"List orgs"}
        if os.environ.get("DS_QDRANT_BE8BC82B__URL"):
            caps["qdrant.collections"] = {"type":"query","desc":"List collections"}
            caps["qdrant.count"] = {"type":"query","desc":"Count points"}
        if os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL") or os.environ.get("DS_SUPABASE_25682EBE__PROJECT_URL"):
            caps["supabase.query"] = {"type":"query","desc":"Query table"}
        if os.environ.get("DS_VERCEL_B333D197__TOKEN") or os.environ.get("DS_VERCEL_F2F9EC1F__TOKEN"):
            caps["vercel.projects"] = {"type":"query","desc":"List projects"}
            caps["vercel.deployments"] = {"type":"query","desc":"List deployments"}
        return caps

    def _on_query(self, event):
        p = event.get("payload",{}); cap = p.get("capability","")
        log.info("Query: %s", cap)
        self.bus.publish("mcp.result", {"capability":cap,"result":self._exec(cap,p.get("args",{}))}, "mcp")

    def _on_execute(self, event):
        p = event.get("payload",{}); cap = p.get("capability","")
        log.info("Execute: %s", cap)
        self.bus.publish("mcp.result", {"capability":cap,"result":self._exec(cap,p.get("args",{}))}, "mcp")

    def _exec(self, cap, args):
        try:
            res = self._route(cap, args)
            return res
        except Exception as e:
            log.error("Cap %s failed: %s", cap, e)
            return {"error": str(e)}

    def _route(self, cap, args):
        if cap == "systemd.service.status":
            r = subprocess.run(["systemctl","is-active",args.get("service","")], capture_output=True, text=True, timeout=10)
            return {"status": r.stdout.strip(), "exit": r.returncode}
        if cap == "systemd.service.restart":
            r = subprocess.run(["systemctl","restart",args.get("service","")], capture_output=True, text=True, timeout=30)
            return {"ok": r.returncode==0}
        if cap == "systemd.list":
            r = subprocess.run(["systemctl","list-units","--type=service","--no-legend"], capture_output=True, text=True, timeout=10)
            return [{"name":l.split()[0],"status":l.split()[3] if len(l.split())>3 else "?"} for l in r.stdout.splitlines() if "nexify-" in l]
        if cap == "file.read":
            p = args.get("path","")
            with open(p) as f: c = f.read()
            return {"content": c[:50000], "size": os.path.getsize(p)}
        if cap == "file.write":
            p = args.get("path",""); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p,"w") as f: f.write(args.get("content",""))
            return {"ok": True, "size": len(args.get("content",""))}
        if cap == "file.exists":
            return {"exists": os.path.exists(args.get("path",""))}
        if cap == "process.list":
            r = subprocess.run(["ps","aux","--sort=-%mem"], capture_output=True, text=True, timeout=10)
            return [{"pid":l.split()[1],"cpu":l.split()[2],"mem":l.split()[3],"cmd":" ".join(l.split()[10:])[:60]} for l in r.stdout.splitlines()[1:26]]
        if cap == "log.tail":
            r = subprocess.run(["tail",f"-{args.get('lines',20)}",args.get("path","/systemmaster/logs/systemmaster.log")], capture_output=True, text=True, timeout=5)
            return {"lines": r.stdout.splitlines()}
        if cap == "state.get":
            p = f"/systemmaster/state/{args.get('key','')}.json"
            if os.path.exists(p):
                with open(p) as f: return json.load(f)
            return None
        if cap == "state.set":
            with open(f"/systemmaster/state/{args.get('key','')}.json","w") as f: json.dump(args.get("value",{}), f)
            return {"ok": True}
        if cap == "env.get":
            return {"key": args.get("key",""), "value": os.environ.get(args.get("key",""),"")}
        if cap == "network.ping":
            r = urllib.request.urlopen(args.get("url",""), timeout=10)
            return {"status": r.status, "size": len(r.read())}
        if cap == "github.repos":
            org = args.get("org","nexifyai"); tok = os.environ.get("DS_GITHUB_35B6CCD0__TOKEN") or os.environ.get("DS_GITHUB_9569466F__TOKEN","")
            import requests; r = requests.get(f"https://api.github.com/orgs/{org}/repos?per_page=20", headers={"Authorization": f"Bearer {tok}"}, timeout=15)
            return [{"name":i["name"],"stars":i["stargazers_count"],"private":i["private"]} for i in r.json()] if r.ok else {"error":r.text[:200]}
        if cap == "github.issues":
            tok = os.environ.get("DS_GITHUB_35B6CCD0__TOKEN") or os.environ.get("DS_GITHUB_9569466F__TOKEN","")
            import requests; r = requests.get(f"https://api.github.com/repos/{args.get('repo','')}/issues?state=open&per_page=20", headers={"Authorization": f"Bearer {tok}"}, timeout=15)
            return [{"number":i["number"],"title":i["title"],"labels":[l["name"] for l in i["labels"]]} for i in r.json() if "pull_request" not in i] if r.ok else {"error":r.text[:200]}
        if cap == "github.prs":
            tok = os.environ.get("DS_GITHUB_35B6CCD0__TOKEN") or os.environ.get("DS_GITHUB_9569466F__TOKEN","")
            import requests; r = requests.get(f"https://api.github.com/repos/{args.get('repo','')}/pulls?state=open&per_page=20", headers={"Authorization": f"Bearer {tok}"}, timeout=15)
            return [{"number":i["number"],"title":i["title"],"user":i["user"]["login"]} for i in r.json()] if r.ok else {"error":r.text[:200]}
        if cap == "qdrant.collections":
            url = os.environ.get("DS_QDRANT_BE8BC82B__URL","http://localhost:6333")
            import requests; r = requests.get(f"{url}/collections", timeout=10)
            if r.ok: return [c["name"] for c in r.json().get("result",{}).get("collections",[])]
            return {"error":r.text[:200]}
        if cap == "qdrant.count":
            col = args.get("collection","nexifyai_brain"); url = os.environ.get("DS_QDRANT_BE8BC82B__URL","http://localhost:6333")
            import requests; r = requests.post(f"{url}/collections/{col}/points/count", json={"exact":True}, timeout=10)
            return r.json().get("result",{}) if r.ok else {"error":r.text[:200]}
        if cap == "supabase.query":
            token = os.environ.get("DS_SUPABASE_1E93118D__SECRET_KEY") or os.environ.get("DS_SUPABASE_25682EBE__SECRET_KEY","")
            project = os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL") or os.environ.get("DS_SUPABASE_25682EBE__PROJECT_URL","")
            import requests; r = requests.get(f"{project}/rest/v1/{args.get('table','')}?select=*&limit={args.get('limit',10)}", headers={"apikey":token,"Authorization":f"Bearer {token}"}, timeout=15)
            return r.json() if r.ok else {"error":r.text[:200]}
        if cap == "vercel.projects":
            tok = os.environ.get("DS_VERCEL_B333D197__TOKEN") or os.environ.get("DS_VERCEL_F2F9EC1F__TOKEN","")
            import requests; r = requests.get("https://api.vercel.com/v9/projects", headers={"Authorization":f"Bearer {tok}"}, timeout=15)
            return [{"name":p["name"],"updated":p.get("updatedAt","")} for p in r.json().get("projects",[])] if r.ok else {"error":r.text[:200]}
        if cap == "vercel.deployments":
            tok = os.environ.get("DS_VERCEL_B333D197__TOKEN") or os.environ.get("DS_VERCEL_F2F9EC1F__TOKEN","")
            import requests; r = requests.get(f"https://api.vercel.com/v6/deployments?projectId={args.get('project','')}&limit=10", headers={"Authorization":f"Bearer {tok}"}, timeout=15)
            return [{"uid":d["uid"],"state":d.get("state",""),"created":d.get("createdAt","")} for d in r.json().get("deployments",[])] if r.ok else {"error":r.text[:200]}
        return {"error": f"unknown: {cap}"}

    def run(self):
        log.info("MCP gateway ready — %d capabilities registered", len(self._caps))
        threading.Event().wait()

if __name__ == "__main__":
    MCPGateway().run()
