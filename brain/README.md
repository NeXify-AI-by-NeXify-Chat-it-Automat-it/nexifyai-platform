# /brain — NeXifyAI Operational Memory
**Status:** ACTIVE | **Schema:** YAML frontmatter required for all entries

## Directory Structure

| Directory | Purpose | Status |
|-----------|---------|--------|
| `/brain/knowledge/` | Decisions, artifacts, policies, lessons learned | ✅ active |
| `/brain/state/` | Current system state (infrastructure, deployments, configs) | ✅ active |
| `/brain/context/` | Session context, preflight data, runtime snapshots | ✅ active |
| `/brain/incidents/` | Incident reports, postmortems, root-cause analyses | ✅ active |
| `/brain/decisions/` | Architectural decisions, ADR cross-references | ✅ active |
| `/brain/playbooks/` | Recovery procedures, runbooks, operational patterns | ✅ active |
| `/brain/tasks/` | Generated tasks, backlog, autopilot queue | ✅ active |
| `/brain/architecture/` | Topology maps, dependency graphs, system models | ✅ created |
| `/brain/audits/` | Design audits, security audits, compliance reports | ✅ created |

## Required YAML Frontmatter

All entries MUST include:
```yaml
---
title: "Entry Title"
created: YYYY-MM-DD
type: [knowledge|incident|decision|playbook|task|state]
tags: [relevant, tags, here]
status: [draft|reviewed|published|archived]
---
```

## Lifecycle
```
draft → reviewed → published → archived
```

Entries older than 30 days without update → `status: archived` (unless marked `permanent`).
