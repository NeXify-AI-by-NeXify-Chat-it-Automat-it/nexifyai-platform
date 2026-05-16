# System 11 — Documentation & Knowledge
spec_id: SYS-011 | version: 1.0 | date: 2026-05-15 | owner: context-manager

## 1. DOCUMENTATION ARCHITECTURE
```
Brain (Qdrant, 5492 vectors)
  ├── nexifyai_brain (long-term)
  │   ├── governance (rules, decisions)
  │   ├── system_architecture (12 systems)
  │   ├── system_inventory (health, state)
  │   ├── quality (audits, scores)
  │   └── knowledge_base (facts, learnings)
  ├── nexifyai_memories (runtime, TTL 7d)
  └── brain/knowledge/ (manual docs)
      └── README.md

File System (backend/docs/)
  ├── systems/ (12 system specs) ← THIS
  ├── adrs/ (architecture decisions)
  └── sop/ (standard operating procedures)
```

## 2. DOCUMENTATION STANDARD
Every system requires:
- Architecture spec (systems/sys-XXX-name.md)
- ADR for major decisions (adrs/ADR-XXX.md)
- SOP for operational procedures (SOP-XXX)

### Template
```markdown
# [Title]
spec_id: [XXX] | version: [semver] | date: [ISO] | owner: [agent]

## Context
[Why was this created?]

## Architecture
[How does it work?]

## Integration
[How does it connect to other systems?]

## Constraints
[What are the rules?]
```

## 3. SOP FRAMEWORK
See SOP-001 through SOP-010 in Brain (ID: 2000103).
New SOPs registered in Brain + docs/sop/ directory.

## 4. CONSTRAINT
- NEVER: Undocumented system in production
- NEVER: Decision without ADR
- ALWAYS: Update docs when system changes
