#!/usr/bin/env python3
"""mcp_daemon.py -- Loads all MCP capabilities and starts MCP runtime integration."""
import json, logging, os, sys, time
sys.path.insert(0, "/services/runtime/events")
sys.path.insert(0, "/services/runtime/mcp")
sys.path.insert(0, "/services/runtime/capabilities")
from event_bus import get_bus, publish
log = logging.getLogger("mcp-daemon")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [mcpd] %(name)s: %(levelname)s: %(message)s")

log.info("=== MCP DAEMON STARTING ===")
bus = get_bus()

# Register MCP core capabilities
from mcp_tool_registry import REG; REG.register_all()

# Register MCP integration bridges
from mcp_github_integration import GITHUB; GITHUB.register()
from mcp_brain_integration import BRAIN; BRAIN.register()
from mcp_infrastructure_integration import INFRA; INFRA.register()
from mcp_security_integration import SEC; SEC.register()

# Register MCP runtime bridge
from mcp_runtime_bridge import BRIDGE; BRIDGE.register_capabilities()

# Start MCP event-driven subsystems
from mcp_capability_router import start_router; start_router()
from mcp_security_governor import start_gov; start_gov()
from mcp_event_bridge import start_bridge; start_bridge()
from mcp_audit_engine import start_audit; start_audit()
from mcp_recovery_adapter import start_adapter; start_adapter()
from mcp_context_router import start_ctx; start_ctx()
from mcp_oracle_sync import start_oracle; start_oracle()
from mcp_governance_engine import start_gov as start_mcp_gov; start_mcp_gov()
from mcp_agent_permissions import start_perms; start_perms()
from mcp_workflow_adapter import start_wf; start_wf()
from capability_learning_engine import start_learn; start_learn()

# Register capability graph
from capability_graph import GRAPH
from capability_dependencies import RESOLVER
from capability_security_matrix import MATRIX_ENGINE, MATRIX, CLASSIFICATION

# Add governance policies
mcp_gov = __import__("mcp_governance_engine").GOV
mcp_gov.add_policy("deployment.*", {"name":"deploy_policy","requires_approval":True})
mcp_gov.add_policy("infra.*", {"name":"infra_policy","requires_approval":True})
mcp_gov.add_policy("security.*", {"name":"security_policy","requires_approval":False})

log.info("=== MCP DAEMON FULLY OPERATIONAL ===")
publish("runtime.start", {"status":"operational","layer":"mcp","components":["gateway","registry","router","governance","audit","recovery","oracle","integrations"]}, "mcp-daemon")

# Publish test event
from mcp_gateway import get_gateway
gw = get_gateway()
log.info(f"MCP Gateway ready: {gw.stats()}")

# Keep alive
while True:
    time.sleep(30)
    publish("runtime.health", {"layer":"mcp","status":"ok"},"mcp-daemon")
