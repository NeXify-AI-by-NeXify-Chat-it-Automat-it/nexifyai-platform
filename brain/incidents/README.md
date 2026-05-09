# Brain: Incidents

**Purpose:** Incident records — SEV1/SEV2/SEV3 events, root causes, resolutions.

**Categories mapped from brain.db:** incident, SEV, error

**Write Policy:** CORROBORATED — requires confidence >= 0.6.
**Read Policy:** AGENT — incident responders only.

**Usage:**
- Record incident timeline
- Document root cause analysis
- Link to compensating actions
- Track resolution status

**brain_cli.py commands:**
```
brain_cli.py store --category incident --content '{"severity":"SEV1","title":"..."}'
```

**Governance:** Auto-triggers compensation engine for SEV1 events.
