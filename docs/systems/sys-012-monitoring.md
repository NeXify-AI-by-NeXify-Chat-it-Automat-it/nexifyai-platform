# System 12 — Real-time Monitoring
spec_id: SYS-012 | version: 1.0 | date: 2026-05-15 | owner: monitoring-specialist

## 1. MONITORING ARCHITECTURE
```
Metrics Sources          Collection         Storage         Alerting        Dashboard
─────────────────────────────────────────────────────────────────────────────────
Backend (:8001)    →    Prometheus    →    TSDB       →    Alertmanager →  Grafana
Hermes (:8642)     →    (planned)         (planned)       (planned)       (planned)
Qdrant (:6333)     →    Brain health   →    Brain       →    CEO notify   →  CLI
Containers          →    docker stats  →    -           →    systemd      →  -
Agents (timers)    →    systemd        →    journald    →    Kuma webhook →  CLI
SSL certs           →    certbot        →    -           →    cron email   →  CLI
```

## 2. KPI DASHBOARD (CLI)
```
┌─────────────────────────────────────────┐
│  NEXIFY AI — HEALTH DASHBOARD           │
│  Brain: 5492   Agents: 34/34 active     │
│  API: 200ms    RAM: 4.2/15Gi            │
│  SSL: 89d      P0: 0  P1: 0            │
└─────────────────────────────────────────┘
```

## 3. ALERT MATRIX
| Condition | Threshold | Severity | Channel |
|-----------|-----------|----------|---------|
| Brain down | >30s | P0 | CEO + Uptime Kuma |
| API error rate | >5% | P1 | monitoring-specialist |
| Container stopped | Any | P1 | systemd restart |
| Agent miss heartbeat | 3x | P1 | CEO |
| SSL expiry | <14d | P2 | Email |
| Disk >80% | >80% | P1 | Gardener |
| RAM >80% | >80% | P2 | Gardener |

## 4. CURRENT MONITORING
- Uptime Kuma: webhook alerts (DS_KUMA_DDA57B74)
- Monitor Timer: 1-min systemd service
- systemd: auto-restart all services
- Gardener Timer: 30-min cleanup

## 5. PLANNED
- Prometheus + Grafana (Q3 2026)
- Distributed tracing (OpenTelemetry)
- Real-time agent dashboard
- Predictive alerting (ML-based anomaly detection)

## 6. CONSTRAINT
- NEVER: Problem detected but not alerted
- NEVER: Alert without response protocol
- ALWAYS: Monitor before deploy
- ALWAYS: Escalate unresolved alerts
