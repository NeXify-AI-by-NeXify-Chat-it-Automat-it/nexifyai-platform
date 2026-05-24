#!/usr/bin/env python3
"""mcp_infrastructure_integration.py -- Infrastructure MCP layer. Docker, systemd, filesystem."""
import json, logging, os, subprocess
from mcp_gateway import get_gateway
from mcp_registry import get_registry
log = logging.getLogger("mcp-infra")

class MCPInfrastructureIntegration:
    def register(self):
        gw = get_gateway(); reg = get_registry()
        gw.register_capability("infra.systemd.status", self._systemd_status, {"domain":"infrastructure","governance":"low"})
        gw.register_capability("infra.systemd.list", self._systemd_list, {"domain":"infrastructure","governance":"low"})
        gw.register_capability("infra.disk.usage", self._disk_usage, {"domain":"infrastructure","governance":"low"})
        gw.register_capability("infra.process.list", self._process_list, {"domain":"infrastructure","governance":"medium"})
        gw.register_capability("infra.file.list", self._file_list, {"domain":"infrastructure","governance":"low"})
        gw.register_capability("infra.service.restart", self._restart_service, {"domain":"infrastructure","governance":"critical","audit":True})
        for cap in ["infra.systemd.status","infra.systemd.list","infra.disk.usage","infra.process.list","infra.file.list","infra.service.restart"]: reg.register(cap, {"domain":"infrastructure"})
        log.info("Infrastructure MCP layer registered (6 capabilities)")

    def _systemd_status(self, call_id, agent, service=None, **kw):
        if service:
            try: r = subprocess.run(["systemctl","is-active",service], capture_output=True, text=True, timeout=5); return {"service":service,"status":r.stdout.strip(),"call_id":call_id}
            except: return {"error":"failed","call_id":call_id}
        return {"error":"no_service","call_id":call_id}

    def _systemd_list(self, call_id, agent, **kw):
        try: r = subprocess.run("systemctl list-units --type=service --state=running --no-pager | head -20", shell=True, capture_output=True, text=True, timeout=5); return {"services":r.stdout[:500],"call_id":call_id}
        except: return {"error":"failed","call_id":call_id}

    def _disk_usage(self, call_id, agent, **kw):
        try: r = subprocess.run("df -h / --output=pcent,used,size", shell=True, capture_output=True, text=True, timeout=5); return {"disk":r.stdout.strip(),"call_id":call_id}
        except: return {"error":"failed","call_id":call_id}

    def _process_list(self, call_id, agent, **kw):
        try: r = subprocess.run("ps aux --sort=-%mem | head -10", shell=True, capture_output=True, text=True, timeout=5); return {"processes":r.stdout[:500],"call_id":call_id}
        except: return {"error":"failed","call_id":call_id}

    def _file_list(self, call_id, agent, path="/runtime", **kw):
        try: files = os.listdir(path); return {"path":path,"files":files[:50],"count":len(files),"call_id":call_id}
        except: return {"error":"not_found","call_id":call_id}

    def _restart_service(self, call_id, agent, service=None, **kw):
        if not service: return {"error":"no_service","call_id":call_id}
        try: r = subprocess.run(["systemctl","restart",service], capture_output=True, text=True, timeout=15); return {"service":service,"rc":r.returncode,"stderr":r.stderr[:100],"call_id":call_id}
        except Exception as e: return {"error":str(e)[:50],"call_id":call_id}

INFRA = MCPInfrastructureIntegration()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); INFRA.register(); print(json.dumps(get_gateway().invoke("infra.disk.usage",agent="test"), indent=2))
