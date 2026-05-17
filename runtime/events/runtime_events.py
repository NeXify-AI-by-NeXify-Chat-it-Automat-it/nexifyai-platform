#!/usr/bin/env python3
"""runtime_events.py -- Event type constants and standard publishers."""
import logging, json
from event_bus import get_bus
log = logging.getLogger("runtime-events")

EVENTS = {
    "RUNTIME_START": "runtime.start", "RUNTIME_STOP": "runtime.stop",
    "WATCHDOG_ALERT": "watchdog.alert", "WATCHDOG_DRIFT": "watchdog.drift",
    "INCIDENT_DETECTED": "incident.detected", "INCIDENT_RESOLVED": "incident.resolved",
    "PLANNER_CYCLE": "planner.cycle", "PLANNER_TASK": "planner.task",
    "GOVERNANCE_PASS": "governance.pass", "GOVERNANCE_FAIL": "governance.fail",
    "DELIVERY_PR": "delivery.pr_created", "DELIVERY_DEPLOY": "delivery.deploy",
    "BRAIN_STORE": "brain.store", "BRAIN_SYNC": "brain.sync",
    "ORG_TEAM": "org.team_assembled", "ORG_ESCALATION": "org.escalation",
    "SYSTEM_ERROR": "system.error", "SYSTEM_WARNING": "system.warning",
}

def pub(et, payload=None, source="runtime"):
    return get_bus().publish(et, payload or {}, source)

def watchdog_alert(detail, severity="warning"):
    return pub("watchdog.alert", {"detail": detail, "severity": severity}, "watchdog")

def incident_detected(title, severity="critical"):
    return pub("incident.detected", {"title": title, "severity": severity}, "incident")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"Runtime events: {len(EVENTS)} types")
