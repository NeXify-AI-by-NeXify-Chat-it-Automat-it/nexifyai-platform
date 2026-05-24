# Brain: Decisions

**Purpose:** Governance decisions — approvals, denials, risk assessments, policy enforcements.

**Categories mapped from brain.db:** decision, governance, approval

**Write Policy:** GOVERNED — requires brain.decide capability.
**Read Policy:** RESTRICTED — governance agents + CEO only.

**Usage:**
- Record governance decisions
- Document risk assessments
- Store approval/rejection rationale
- Track blast radius calculations

**brain_cli.py commands:**
```
brain_cli.py store --category decision --content '{"decision_id":"...","verdict":"APPROVED"}'
```

**Governance:** All decisions must be auditable and replayable.
