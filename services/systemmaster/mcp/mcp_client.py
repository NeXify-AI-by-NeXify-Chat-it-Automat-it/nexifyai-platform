#!/venv/bin/python3
"""mcp_client.py — Synchroner MCP-Client für Scratchpad/CLI-Nutzung."""
import json, os, sys, time
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus

class MCPClient:
    def __init__(self, timeout=30):
        self.bus = get_bus()
        self._timeout = timeout
        self._results = []

    def _on_result(self, event):
        self._results.append(event.get("payload", {}))

    def execute(self, capability, args=None):
        self._results = []
        reply_channel = f"mcp.response.{int(time.time()*1000000)}"
        self.bus.subscribe("mcp.result", self._on_result, f"mcp-client:{reply_channel}")
        self.bus.publish("mcp.execute", {"capability": capability, "args": args or {}, "reply_channel": "mcp.result"}, "mcp-client")
        deadline = time.time() + self._timeout
        while time.time() < deadline:
            if self._results:
                return self._results[-1].get("result")
            time.sleep(0.1)
        return {"error": "timeout"}

    def query(self, capability, args=None):
        return self.execute(capability, args)

def get_mcp():
    return MCPClient()

if __name__ == "__main__":
    mcp = get_mcp()
    r = mcp.query("systemd.list")
    print(json.dumps(r, indent=2))
