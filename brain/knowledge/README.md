# Brain: Knowledge

**Purpose:** Structured enterprise knowledge — facts, documentation, policies, architectural decisions.

**Categories mapped from brain.db:** knowledge, documentation, wiki, fact

**Write Policy:** ATTRIBUTED — every entry MUST have source attribution.
**Read Policy:** AGENT — authenticated agents only.

**Usage:**
- Store enterprise facts and documentation
- Version-controlled knowledge entries
- Cross-reference with ADRs and policies

**brain_cli.py commands:**
```
brain_cli.py store --category knowledge --content "..." --source "..."
brain_cli.py store --category fact --content "..." --source "..."
```

**Governance:** BrainGovernor.enforce_write("knowledge", source="...", confidence=...)
