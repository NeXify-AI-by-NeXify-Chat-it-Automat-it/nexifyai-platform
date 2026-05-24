# Brain: State

**Purpose:** System state snapshots — health checks, service status, deployment states.

**Categories mapped from brain.db:** state, health, status

**Write Policy:** ATTRIBUTED — must include timestamp and observer position.
**Read Policy:** AGENT — all authenticated agents.

**Usage:**
- Record health check results
- Track deployment state transitions
- Store reconciliation results

**brain_cli.py commands:**
```
brain_cli.py store --category state --content '{"health_score":90,"timestamp":"..."}'
```

**Governance:** State entries without timestamp/correlation_id are rejected.
