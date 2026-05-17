#!/usr/bin/env python3
"""mcp_security_integration.py -- Security MCP layer. Audit, permissions, threat detection."""
import json, logging, os
from mcp_gateway import get_gateway
from mcp_registry import get_registry
log = logging.getLogger("mcp-security-layer")

class MCPSecurityIntegration:
    def register(self):
        gw = get_gateway(); reg = get_registry()
        gw.register_capability("security.audit.log", self._audit_log, {"domain":"security","governance":"required","audit":True})
        gw.register_capability("security.permissions.check", self._perm_check, {"domain":"security","governance":"low"})
        gw.register_capability("security.threat.scan", self._threat_scan, {"domain":"security","governance":"required","audit":True})
        for cap in ["security.audit.log","security.permissions.check","security.threat.scan"]: reg.register(cap, {"domain":"security"})
        log.info("Security MCP layer registered (3 capabilities)")

    def _audit_log(self, call_id, agent, limit=20, **kw):
        try:
            from mcp_audit_engine import ENG; al = ENG.get_log(limit); return {"ok":True,"entries":al,"count":len(al),"call_id":call_id}
        except: return {"ok":False,"error":"audit_engine_unavailable","call_id":call_id}

    def _perm_check(self, call_id, agent, target_cap=None, target_agent=None, **kw):
        from mcp_agent_permissions import PERMS; a = target_agent or agent; c = target_cap or ""
        return {"agent":a,"capability":c,"allowed":PERMS.allowed(a,c),"call_id":call_id}

    def _threat_scan(self, call_id, agent, **kw):
        findings = []
        try:
            r = __import__("subprocess").run("systemctl list-units --type=service --state=failed --no-pager | grep -c . || true", shell=True, capture_output=True, text=True, timeout=5)
            failed = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
            if failed > 0: findings.append({"type":"failed_services","count":failed,"severity":"high"})
        except: pass
        return {"ok":True,"findings":findings,"call_id":call_id}

SEC = MCPSecurityIntegration()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); SEC.register(); print(json.dumps(get_gateway().invoke("security.permissions.check",agent="delivery",target_cap="github.pr.create",target_agent="delivery"), indent=2))
