#!/usr/bin/env python3
"""mcp_runtime_bridge.py -- Bridges MCP capabilities to runtime systems (docker, git, infra)."""
import json, logging, os, subprocess
log = logging.getLogger("mcp-bridge")

class MCPRuntimeBridge:
    def __init__(self):
        from mcp_gateway import get_gateway
        self.gateway = get_gateway()

    def register_capabilities(self):
        self.gateway.register_capability("runtime.shell", lambda call_id, agent, cmd, **kw: self._shell(call_id, cmd), {"domain":"runtime","governance":"required"})
        self.gateway.register_capability("runtime.check", lambda call_id, agent, path, **kw: {"exists": os.path.exists(path)}, {"domain":"runtime","governance":"low"})
        self.gateway.register_capability("runtime.stat", lambda call_id, agent, path, **kw: self._stat(call_id, path), {"domain":"runtime","governance":"low"})

    def _shell(self, call_id, cmd):
        try: r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30); return {"rc": r.returncode, "stdout": r.stdout[:500], "stderr": r.stderr[:200]}
        except Exception as e: return {"error": str(e)[:100]}

    def _stat(self, call_id, path):
        try: s = os.stat(path); return {"size": s.st_size, "mode": oct(s.st_mode)}
        except: return {"error": "not_found"}

BRIDGE = MCPRuntimeBridge()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); BRIDGE.register_capabilities(); print("Bridge ready")
