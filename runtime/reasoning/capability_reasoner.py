#!/usr/bin/env python3
"""capability_reasoner.py — Given a task, reasons which MCP capability to invoke."""
import json, logging
from event_bus import get_bus, publish
log = logging.getLogger("cap-reasoner")

TASK_CAP_MAP = {
    "create_issue": "github.issue.create", "list_issues": "github.issue.list",
    "create_pr": "github.pr.create", "list_prs": "github.pr.list",
    "query_brain": "brain.query", "store_brain": "brain.store",
    "check_health": "runtime.health", "restart_service": "infra.service.restart",
    "audit_log": "security.audit.log", "check_permissions": "security.permissions.check",
}

class CapabilityReasoner:
    def __init__(self):
        self.bus = get_bus()

    def start(self):
        self.bus.subscribe("planner.task", self._on_task, "capreason:task")
        log.info("Capability reasoner active")

    def reason(self, task_type, context=None):
        cap = TASK_CAP_MAP.get(task_type, "unknown")
        confidence = 0.9 if cap != "unknown" else 0.1
        return {"task_type": task_type, "recommended_capability": cap, "confidence": confidence}

    def _on_task(self, event):
        task = event.get("payload",{})
        result = self.reason(task.get("type","unknown"))
        if result["confidence"] > 0.5:
            publish("mcp.invoke", {"cap": result["recommended_capability"], "task": task}, "cap-reasoner")

REASONER = CapabilityReasoner()
def start(): REASONER.start(); return REASONER

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); start(); print(json.dumps(REASONER.reason("create_pr")))
