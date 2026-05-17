#!/usr/bin/env python3
"""capability_priorities.py -- Priority resolution for competing MCP capability invocations."""
import json, logging
log = logging.getLogger("cap-prio")

PRIORITIES = {"critical_incident":["recover.*","rollback.*"],"deployment":["github.pr.create","deployment.run"],"maintenance":["reconcile.*","brain.*","monitor.*"],"optimization":["learning.*","pattern.*"]}

class CapabilityPriorityResolver:
    def resolve(self, caps):
        """Given a list of capability IDs, sort by organizational priority."""
        def priority(cap):
            for i, (context, patterns) in enumerate(PRIORITIES.items()):
                for p in patterns:
                    if p.endswith("*") and cap.startswith(p[:-1]): return i
                    if p == cap: return i
            return 99
        return sorted(caps, key=priority)

RESOLVER = CapabilityPriorityResolver()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(RESOLVER.resolve(["learning.pattern","recover.system","monitor.health"]), indent=2))
