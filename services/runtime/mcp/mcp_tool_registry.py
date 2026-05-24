#!/usr/bin/env python3
"""
DEPRECATED: Wird durch services/tool_registry.py ersetzt.
            Nutze get_all_tools() oder get_agent_tools() mit @tool-Decorator.
            Migration: from services.tool_registry import get_all_tools
            Entfernung geplant: 2026-06-21
"""

"""mcp_tool_registry.py -- Registers concrete tool implementations as MCP capabilities."""
import json, logging, os, subprocess
log = logging.getLogger("mcp-tools")

class MCPToolRegistry:
    def __init__(self):
        from mcp_gateway import get_gateway
        self.gateway = get_gateway()
        self._registered_count = 0

    def register_github_tools(self):
        from mcp_gateway import get_gateway
        gw = get_gateway()
        gw.register_capability("github.issue.create", self._create_issue, {"domain":"github","governance":"required","audit":True})
        gw.register_capability("github.pr.create", self._create_pr, {"domain":"github","governance":"required","audit":True,"rollback":True})
        gw.register_capability("github.issue.list", self._list_issues, {"domain":"github","governance":"low"})
        self._registered_count += 3

    def register_brain_tools(self):
        from mcp_gateway import get_gateway
        gw = get_gateway()
        gw.register_capability("brain.query", self._brain_query, {"domain":"brain","governance":"low"})
        gw.register_capability("brain.store", self._brain_store, {"domain":"brain","governance":"required"})
        self._registered_count += 2

    def register_runtime_tools(self):
        from mcp_gateway import get_gateway
        gw = get_gateway()
        gw.register_capability("runtime.health", self._health, {"domain":"runtime","governance":"low"})
        gw.register_capability("runtime.shell", self._shell, {"domain":"runtime","governance":"required"})
        self._registered_count += 2

    def _create_issue(self, call_id, agent, **kw): return {"status": "simulated", "call_id": call_id}
    def _create_pr(self, call_id, agent, **kw): return {"status": "simulated", "call_id": call_id}
    def _list_issues(self, call_id, agent, **kw): return {"issues": [], "call_id": call_id}
    def _brain_query(self, call_id, agent, **kw): return {"vectors": 0, "call_id": call_id}
    def _brain_store(self, call_id, agent, **kw): return {"stored": True, "call_id": call_id}
    def _health(self, call_id, agent, **kw): return {"status": "ok", "call_id": call_id}
    def _shell(self, call_id, agent, cmd, **kw):
        try: r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30); return {"rc": r.returncode, "stdout": r.stdout[:300]}
        except Exception as e: return {"error": str(e)[:50], "call_id": call_id}

    def register_all(self):
        self.register_github_tools(); self.register_brain_tools(); self.register_runtime_tools()
        log.info(f"Registered {self._registered_count} MCP tools")

REG = MCPToolRegistry()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); REG.register_all(); print("Tools registered")
