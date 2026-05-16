# System 4 — AI/Agent Runtime Architecture
spec_id: SYS-004 | version: 1.0 | date: 2026-05-15 | owner: ai-engineer

## 1. EVENT SYSTEM

### Architecture
Event-driven pub/sub with Hermes Gateway as broker.
- Producer: Any agent emits event via POST to Hermes
- Broker: Hermes routes to subscribed agents (WebSocket push or HTTP callback)
- Consumer: Agents subscribe to event types at registration
- Dead Letter: Failed deliveries go to DLQ in Brain (collection: nexifyai_events_dlq)

### Event Schema
```json
{
  "event_id": "evt-{uuid4}",
  "event_type": "AGENT_HEARTBEAT|AGENT_FAILED|TASK_COMPLETED|SYSTEM_DEGRADED|AGENT_RECOVERED|DEPLOYMENT_STARTED|BRAIN_THRESHOLD|SECURITY_ALERT",
  "source_agent": "nexifyai-ceo",
  "timestamp": "ISO8601",
  "payload": {},
  "severity": "INFO|WARN|CRITICAL",
  "correlation_id": "optional"
}
```

### Delivery Guarantees
- At-least-once delivery (Hermes retries 3x with 5s backoff)
- Best-effort ordering per source agent
- Max event size: 1MB
- Persistence: All events logged to Qdrant for audit/replay

### Implementation
- FastAPI WebSocket endpoints for real-time subscriptions
- Redis for subscription registry + heartbeat storage
- BullMQ/Redis Streams for async processing
- Qdrant for event audit log

## 2. AGENT STATE MACHINE

### States
```
IDLE → BUSY → BLOCKED → RECOVERY → IDLE
  ↑       ↓        ↓          ↓
  └─── TIMEOUT ──┘  └─── RESOLVED ──┘
```

### Transitions
| From | To | Trigger | Guard | Timeout |
|------|----|---------|-------|---------|
| IDLE | BUSY | Task assigned | Agent ready | 30s to accept |
| BUSY | IDLE | Task completed | Result valid | 5min max |
| BUSY | BLOCKED | Dependency unavailable | After 3 retries | 2min detection |
| BLOCKED | RECOVERY | Dependency restored | Or timeout | 5min max |
| RECOVERY | IDLE | State restored from Brain | Heartbeat restored | 1min |
| ANY | ERROR | Watchdog kill | 3 missed heartbeats | 90s |

### Persistence
- State stored in Brain (nexifyai_brain, category: agent_state, topic: agent_state-{agent_id})
- Snapshot every 5 transitions
- Full state recovery on restart from Brain

### Implementation
- Python `transitions` library
- Hermes validates transitions via middleware
- Invalid transitions → logged + rejected

## 3. WATCHDOG SYSTEM

### Architecture
Centralized watchdog as separate Hermes agent (watchdog-agent).
- Heartbeat: Every 30s from each agent to Hermes
- Check: Watchdog scans Brain for stale heartbeats every 15s
- Alert: 90s without heartbeat → WARN (monitoring-specialist)
- Recovery: 180s without heartbeat → RECOVERY event → systemd restart
- Self-monitoring: Secondary watchdog monitors primary

### Thresholds
| Condition | Time | Action |
|-----------|------|--------|
| Missed heartbeat | 90s | WARN → monitoring-specialist |
| Agent presumed dead | 180s | RECOVERY → systemd restart |
| 3 restarts in 5min | - | P1 ALERT → CEO |
| Watchdog itself dead | 30s | Secondary watchdog takes over |

### Implementation
- Redis for heartbeat storage (TTL: 60s)
- Prometheus metrics → alerting
- Recovery actions are idempotent
- All watchdog actions logged to Brain

## 4. RECOVERY SYSTEM

### Recovery Patterns
| Failure | Detection | Action | Rollback |
|---------|-----------|--------|----------|
| Agent crash | Watchdog (180s) | systemd restart | State recovery from Brain |
| Agent hang | Watchdog timeout | SIGKILL + restart | Fresh state from last snapshot |
| Dependency failure | Agent detects 3 retries | BLOCKED state, queue task | Retry when dependency returns |
| Brain unavailable | Agent detects timeout | Fallback to local cache | Retry with exponential backoff |
| Hermes unavailable | Agent detects timeout | Queue to local buffer | Flush to Hermes on reconnect |

### Auto-recovery Flow
1. Watchdog detects failure → emits AGENT_FAILED event
2. Recovery handler checks Brain for last known state
3. systemd restarts agent process
4. Agent loads state from Brain on boot
5. Agent emits AGENT_RECOVERED event
6. Pending tasks re-queued

## 5. MULTI-AGENT ORCHESTRATION

### Priority Routing
| Priority | Preemption | Timeout | Concurrency Limit |
|----------|-----------|---------|-------------------|
| P0 | Yes (preempts lower) | 15min | 1 at a time |
| P1 | No | 60min | 2 concurrent |
| P2 | No | 4h | 3 concurrent |
| P3 | No | 24h | 5 concurrent |

### Load Balancing
- Max 3 concurrent tasks per agent
- Round-robin within same capability tier
- Load-aware: skip agents at max capacity

### Conflict Resolution
- Two agents assigned same task → CEO decides (P0) or first-claim wins (P1-P3)
- Contradicting outputs → senior-quality-auditor reviews

### Coordination Protocol
Handoff: {from_agent, to_agent, task_context, expected_output, deadline, review_by}

## 6. CONSTRAINTS
- NEVER: Agent without state machine → not deployable
- NEVER: Agent without heartbeat → not registered
- NEVER: Agent without recovery path → not approved
- ALWAYS: State persisted before task execution
- ALWAYS: Heartbeat emitted every 30s
- WHEN: 3 agents in ERROR state → CEO emergency meeting
