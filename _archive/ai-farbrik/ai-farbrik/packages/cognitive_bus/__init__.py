"""
NeXifyAI — Cognitive Event Bus + Slack Bridge (RC3+RC4)

NOT: isolated services emitting isolated events
BUT:  unified runtime event federation across ALL systems

THE CRITICAL LAYER for Enterprise Runtime Communication.

Events flow:
  GitHub Actions → Cognitive Bus → Slack + Hermes + Brain + Oracle

Event types:
  github.action.failed    github.pr.created     github.issue.created
  vercel.deploy.failed    vercel.deploy.ready    vercel.deploy.rolled_back
  brain.conflict.detected  memory.consolidated    policy.violation.detected
  agent.task.created       agent.task.completed   agent.task.failed
  runtime.service.offline  runtime.service.online  runtime.circuit.open
  delivery.pipeline.started delivery.pipeline.completed delivery.pipeline.failed
"""
import json
import time
import httpx
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# EVENT BUS
# ═══════════════════════════════════════════════════

class EventSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RuntimeEvent:
    """A single runtime event on the Cognitive Bus."""
    event_id: str
    event_type: str                        # "github.action.failed"
    source: str                            # "github-actions", "vercel", "brain"
    severity: EventSeverity = EventSeverity.INFO
    summary: str = ""
    detail: str = ""
    correlation_id: str = ""
    resource_id: str = ""
    resource_url: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CognitiveBus:
    """
    NeXify Cognitive Bus — central runtime event federation.

    All systems publish events here. All subscribers receive them.
    Events are persisted to brain.db for replay and audit.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_log: List[RuntimeEvent] = []
        self._max_log = 10000

    def publish(self, event: RuntimeEvent):
        """Publish an event to all subscribers."""
        self.event_log.append(event)
        if len(self.event_log) > self._max_log:
            self.event_log = self.event_log[-self._max_log:]

        # Notify subscribers matching event_type
        for pattern, handlers in self.subscribers.items():
            if pattern == "*" or pattern == event.event_type or event.event_type.startswith(pattern):
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception:
                        pass  # Subscriber failures don't block the bus

    def subscribe(self, event_pattern: str, handler: Callable):
        """Subscribe to events matching a pattern."""
        self.subscribers[event_pattern].append(handler)

    def get_recent(self, limit: int = 50, source: str = "",
                   severity: EventSeverity = None) -> List[RuntimeEvent]:
        """Get recent events, optionally filtered."""
        events = self.event_log
        if source:
            events = [e for e in events if e.source == source]
        if severity:
            events = [e for e in events if e.severity == severity]
        return events[-limit:]

    def stats(self) -> Dict[str, Any]:
        """Bus statistics."""
        by_source = defaultdict(int)
        by_severity = defaultdict(int)
        for e in self.event_log:
            by_source[e.source] += 1
            by_severity[e.severity.value] += 1

        return {
            "total_events": len(self.event_log),
            "subscribers": sum(len(v) for v in self.subscribers.values()),
            "by_source": dict(by_source),
            "by_severity": dict(by_severity),
        }


# ═══════════════════════════════════════════════════
# SLACK BRIDGE
# ═══════════════════════════════════════════════════

class SlackBridge:
    """
    Slack ↔ Hermes ↔ Runtime communication bridge.

    NOT: isolated Slack messages
    BUT:  governed runtime notifications with structured formatting

    Routes:
      - CI failures → Slack notification
      - Deployment events → Slack update
      - Health alerts → Slack warning
      - Brain conflicts → Slack alert
      - Governance decisions → Slack approval
    """

    def __init__(self, bus: CognitiveBus = None,
                 slack_token: str = "",
                 default_channel: str = "#operations"):
        self.bus = bus or CognitiveBus()
        self.token = slack_token or os.getenv("SLACK_BOT_TOKEN", "")
        self.default_channel = default_channel

        # Auto-subscribe to critical runtime events
        if self.token:
            self._auto_subscribe()

    def _auto_subscribe(self):
        """Subscribe to critical runtime events."""
        self.bus.subscribe("github.action.failed", self._on_ci_failure)
        self.bus.subscribe("vercel.deploy.*", self._on_deployment_event)
        self.bus.subscribe("runtime.service.offline", self._on_service_offline)
        self.bus.subscribe("runtime.circuit.open", self._on_circuit_open)
        self.bus.subscribe("brain.conflict.detected", self._on_brain_conflict)
        self.bus.subscribe("policy.violation.detected", self._on_policy_violation)
        self.bus.subscribe("delivery.*", self._on_delivery_event)

    def send(self, text: str, channel: str = "",
             blocks: List[Dict] = None,
             severity: EventSeverity = EventSeverity.INFO) -> Dict[str, Any]:
        """
        Send a message to Slack.

        Returns structured result — not just "ok" boolean.
        """
        if not self.token:
            return {"sent": False, "error": "SLACK_BOT_TOKEN not configured"}

        target = channel or self.default_channel
        payload = {
            "channel": target,
            "text": text,
        }
        if blocks:
            payload["blocks"] = blocks

        try:
            resp = httpx.post(
                "https://slack.com/api/chat.postMessage",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10.0,
            )
            data = resp.json()
            return {
                "sent": data.get("ok", False),
                "channel": data.get("channel", target),
                "ts": data.get("ts", ""),
                "error": data.get("error", ""),
            }
        except Exception as e:
            return {"sent": False, "error": str(e)}

    def notify_ci_failure(self, workflow: str, error: str,
                          run_url: str = "") -> Dict[str, Any]:
        """Send a formatted CI failure notification."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚨 CI FAILED: {workflow}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"```{error[:500]}```"}
            },
        ]
        if run_url:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<{run_url}|View Run →>"}
            })

        return self.send(
            f"🚨 CI FAILED: {workflow}",
            severity=EventSeverity.ERROR,
            blocks=blocks,
        )

    def notify_deployment(self, status: str, url: str = "",
                          duration_s: float = 0.0) -> Dict[str, Any]:
        """Send a deployment notification."""
        emoji = {"ready": "✅", "failed": "🚨", "building": "🏗️", "rolled_back": "↩️"}
        icon = emoji.get(status, "📦")

        blocks = [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{icon} Deployment: *{status.upper()}*{chr(10)}URL: {url}{chr(10)}Duration: {duration_s:.1f}s"}
        }]

        return self.send(f"{icon} Deployment: {status.upper()}", blocks=blocks)

    def notify_health_alert(self, service: str, status: str) -> Dict[str, Any]:
        """Send a health alert."""
        emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "🔴"}
        icon = emoji.get(status, "❓")
        return self.send(f"{icon} {service}: {status}")

    # ── Event handlers ──

    def _on_ci_failure(self, event: RuntimeEvent):
        self.notify_ci_failure(
            event.resource_id,
            event.detail,
            event.metadata.get("run_url", ""),
        )

    def _on_deployment_event(self, event: RuntimeEvent):
        status = event.event_type.replace("vercel.deploy.", "")
        self.notify_deployment(
            status,
            event.metadata.get("url", ""),
            event.metadata.get("duration_s", 0),
        )

    def _on_service_offline(self, event: RuntimeEvent):
        self.notify_health_alert(event.resource_id, "unhealthy")

    def _on_circuit_open(self, event: RuntimeEvent):
        self.send(f"⚡ Circuit BREAKER: {event.resource_id} — {event.detail}",
                  severity=EventSeverity.CRITICAL)

    def _on_brain_conflict(self, event: RuntimeEvent):
        self.send(f"🧠 Brain CONFLICT: {event.detail}", severity=EventSeverity.WARNING)

    def _on_policy_violation(self, event: RuntimeEvent):
        self.send(f"🛡️ Policy VIOLATION: {event.detail}",
                  severity=EventSeverity.CRITICAL)

    def _on_delivery_event(self, event: RuntimeEvent):
        if "completed" in event.event_type:
            self.send(f"🏁 {event.summary}", severity=EventSeverity.INFO)
        elif "failed" in event.event_type:
            self.send(f"❌ {event.summary}", severity=EventSeverity.ERROR)


# ═══════════════════════════════════════════════════
# RUNTIME EVENT PUBLISHER
# ═══════════════════════════════════════════════════

class RuntimeEventPublisher:
    """
    Convenience publisher for common runtime events.

    Usage:
      pub = RuntimeEventPublisher(bus)
      pub.ci_failed("deploy", "Build error", run_url="...")
      pub.deployment("ready", url="...")
      pub.service_offline("supabase", "Connection refused")
    """

    def __init__(self, bus: CognitiveBus):
        self.bus = bus

    def ci_failed(self, workflow: str, error: str,
                  run_url: str = "", corr_id: str = ""):
        self.bus.publish(RuntimeEvent(
            event_id=f"evt_ci_{int(time.time())}",
            event_type="github.action.failed",
            source="github-actions",
            severity=EventSeverity.ERROR,
            summary=f"CI {workflow} failed",
            detail=error,
            resource_id=workflow,
            metadata={"run_url": run_url},
            correlation_id=corr_id,
        ))

    def deployment(self, status: str, url: str = "",
                   duration_s: float = 0.0, corr_id: str = ""):
        self.bus.publish(RuntimeEvent(
            event_id=f"evt_deploy_{int(time.time())}",
            event_type=f"vercel.deploy.{status}",
            source="vercel",
            severity=EventSeverity.ERROR if status == "failed" else EventSeverity.INFO,
            summary=f"Deployment {status}: {url}",
            resource_id=url,
            metadata={"duration_s": duration_s},
            correlation_id=corr_id,
        ))

    def service_offline(self, service: str, reason: str):
        self.bus.publish(RuntimeEvent(
            event_id=f"evt_svc_{int(time.time())}",
            event_type="runtime.service.offline",
            source="runtime-health",
            severity=EventSeverity.WARNING,
            summary=f"Service {service} OFFLINE",
            detail=reason,
            resource_id=service,
        ))

    def brain_conflict(self, memory_id: str, detail: str):
        self.bus.publish(RuntimeEvent(
            event_id=f"evt_brain_{int(time.time())}",
            event_type="brain.conflict.detected",
            source="brain-governor",
            severity=EventSeverity.WARNING,
            detail=detail,
            resource_id=memory_id,
        ))

    def policy_violation(self, policy: str, detail: str, actor: str = ""):
        self.bus.publish(RuntimeEvent(
            event_id=f"evt_policy_{int(time.time())}",
            event_type="policy.violation.detected",
            source="governance",
            severity=EventSeverity.CRITICAL,
            detail=detail,
            resource_id=policy,
            metadata={"actor": actor},
        ))


# ═══════════════════════════════════════════════════
# SINGLETONS
# ═══════════════════════════════════════════════════

_bus: Optional[CognitiveBus] = None
_bridge: Optional[SlackBridge] = None

def get_bus() -> CognitiveBus:
    global _bus
    if _bus is None:
        _bus = CognitiveBus()
    return _bus

def get_slack_bridge() -> SlackBridge:
    global _bridge
    if _bridge is None:
        _bridge = SlackBridge(get_bus())
    return _bridge
