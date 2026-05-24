#!/usr/bin/env python3
"""mcp_capability_router.py -- Routes capability requests to the right MCP handler based on task type."""
import json, logging
from event_bus import get_bus, publish
from mcp_registry import get_registry
from mcp_gateway import get_gateway
log = logging.getLogger("cap-router")

CAP_TO_TASK = {
    "reconcile": ["brain.query", "brain.reconcile"],
    "deploy": ["github.pr.create", "deployment.run"],
    "recover": ["infra.restart", "deployment.rollback"],
    "govern": ["governance.policy.check", "governance.audit"],
    "observe": ["watchdog.run", "monitor.health"],
    "learn": ["brain.store", "learning.pattern"],
}

class CapabilityRouter:
    def __init__(self):
        self.bus = get_bus(); self.registry = get_registry(); self.gateway = get_gateway()

    def start(self):
        self.bus.subscribe("planner.task", self._on_task, "cap-router:task")
        log.info("Capability router active")

    def _on_task(self, event):
        payload = event.get("payload", {})
        task_type = payload.get("type", payload.get("task_type", ""))
        caps = CAP_TO_TASK.get(task_type, [])
        for cap_id in caps:
            if self.registry.get(cap_id):
                self.gateway.invoke(cap_id, {"source": "planner", "task": task_type}, "capability-router")
                break

ROUTER = CapabilityRouter()
def start_router(): ROUTER.start(); return ROUTER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start_router()
