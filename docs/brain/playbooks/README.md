# Brain: Playbooks

**Purpose:** Operational playbooks — recovery procedures, runbooks, standard operating procedures.

**Categories mapped from brain.db:** playbook, procedure, runbook

**Write Policy:** GOVERNED — requires brain.governance capability.
**Read Policy:** AGENT — all authenticated agents.

**Usage:**
- Store recovery procedures
- Document standard workflows
- Cross-reference with skills and agent contracts

**brain_cli.py commands:**
```
brain_cli.py store --category playbook --content "Recovery procedure: ..."
```

**Governance:** All playbooks must be validated against current architecture.
