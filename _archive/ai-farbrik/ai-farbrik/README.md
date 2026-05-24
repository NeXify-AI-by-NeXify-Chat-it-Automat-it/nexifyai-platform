# NeXifyAI — AI Fabrik

**Governed AI Operations & Knowledge Platform**

Not: LLM + Tool Calls
But: Stateful Operational Intelligence Platform

## The Brain IS the Company

The Central Oracle is not a feature. It IS the enterprise.
Every operation is governed, attributed, versioned, auditable.

## Architecture

```
Core Layer (/core/)
  brain/        — Qdrant, pgvector, SQLite, Redis, Event Store
  governance/   — Policy Engine, Capability System, Approval Flows
  runtime/      — Cognitive Bus, Workflow Execution, Replay
  memory/       — 5-Type Taxonomy, Consolidation
  identity/     — Cross-Channel Consciousness
  audit/        — Traceability, Hallucination Detection

Packages (/packages/)
  event_model/          — Global Event Contract (35 Types, 8 Domains)
  skill_runtime/        — Typed Governed Skill Manifests
  governance_kernel/    — Capability-Gated Policy Enforcement
  ingestion/            — 6-Stage Knowledge Pipeline (26 Sources)
  graph/                — Semantic Knowledge Graph (50 Nodes)
  memory/               — Unified 5-Type Operational Memory
  brain_governance/     — Brain Access Control + Audit
  runtime_connectivity/ — Service Discovery, Health, Ready Gates
  cognitive_bus/        — Event Federation + Slack Bridge
```

## Quick Start

```bash
# Bootstrap
make bootstrap

# Health check
make health

# Oracle sync
make oracle-sync

# Validate governance
make validate

# Run tests
make test

# Start runtime
make runtime-up
```

## Governance Gates

All operations pass through:
1. Capability Check — does the agent have the required token?
2. Risk Assessment — LOW/MEDIUM/HIGH/CRITICAL classification
3. Blast Radius — how many downstream systems are affected?
4. Policy Enforcement — no Stripe, no GPL/AGPL/SSPL, RLS required
5. Approval — auto-approve LOW/MEDIUM, human-approve HIGH/CRITICAL

## License

Proprietary. NeXifyAI by NeXify — Chat it. Automate it.
