# Brain: Architecture

**Purpose:** Architecture decisions, ADRs, system topology, dependency maps.

**Categories mapped from brain.db:** architecture, ADR, design, topology

**Write Policy:** GOVERNED — requires brain.governance capability.
**Read Policy:** AGENT — architect + governance agents.

**Usage:**
- Store Architecture Decision Records
- Document system topology
- Track dependency relationships
- Version architectural changes

**brain_cli.py commands:**
```
brain_cli.py store --category architecture --content '{"adr_id":"ADR-008","title":"..."}'
```

**Governance:** ADRs must be numbered, versioned, and linked to causal events.
