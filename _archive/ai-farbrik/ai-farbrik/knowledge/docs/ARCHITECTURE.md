# AI Fabrik — Architecture

**Governed AI Operations Factory**

## System-Architektur

```
                         ┌──────────────────────┐
                         │   Hermes Agent        │
                         │   (Runtime Gateway)   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   ai-farbrik-adapter │
                         │   (Translation Layer)│
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼──────┐   ┌─────────▼──────┐   ┌─────────▼──────┐
    │  Governance     │   │  Event Ledger   │   │  Skill Runtime  │
    │  Kernel         │   │  (SQLite)       │   │  (Manifest)     │
    └─────────┬──────┘   └─────────┬──────┘   └─────────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼──────┐   ┌─────────▼──────┐   ┌─────────▼──────┐
    │  GitHub MCP     │   │  Vercel API     │   │  Supabase API   │
    │  (REST)         │   │  (REST)         │   │  (3-Layer)      │
    └────────────────┘   └────────────────┘   └────────────────┘
```

## Datenfluss

```text
User Request
  → Oracle Agent (intent parsing)
    → Planner Agent (execution plan)
      → Architect Agent (ADR)
        → Specialist Agents (frontend, backend, database)
          → QA Agent (tests)
            → Security Agent (scan)
              → Deployment Agent (Vercel)
                → Governance Agent (approval)
                  → Convergence (verify)

Jeder Schritt:
  → GlobalEvent emittiert
  → SQLite Ledger persistiert
  → Correlation ID verfolgt
  → Compensation registriert
```

## 5 Kernsysteme

### A — Knowledge Fabric
- `knowledge/docs/` → `knowledge/normalized/` → `knowledge/embeddings/` → `knowledge/graph/`
- Input: interne Docs, Paperclip Docs, ADRs, Incidents, PRs, Migration-Ledger
- Output: Semantic Knowledge Graph, Embedding Registry

### B — Skill Runtime
- `packages/skill_runtime/` — Skill Manifest System
- `skills/github/`, `skills/vercel/`, `skills/supabase/` — Governed Skills
- Jeder Skill: Capabilities, Risk, Compensation, Observability

### C — Operational Memory
- `packages/event_model/` — Global Event Contract (35 Event Types, 8 Domains)
- `packages/transaction_engine/` — DeliveryTransaction Coordinator
- SQLite Persistent Ledger mit Correlation, Causation, Idempotency

### D — AI Delivery
- `packages/delivery_dsl/` — Transaction DSL
- `packages/reconciliation/` — Desired vs Observed State

### E — Governance Kernel
- `packages/governance_kernel/` — Risk, Capability, Blast Radius, Approval
- `governance/policies/` — Policy Definitions
- `governance/risk/` — Risk Models
- `governance/approvals/` — Approval Workflows

## Tech Stack

| Layer | System |
|-------|--------|
| AI Runtime | Vercel AI SDK (NeXify via OpenRouter) |
| Orchestration | DeliveryTransaction (SQLite Event Ledger) |
| Browser | Playwright + Browserbase |
| Sandbox | E2B |
| Hosting | Vercel (Frontend) + VPS (Backend) |
| Database | Supabase (PostgreSQL + RLS) |
| Vector | Qdrant |
| CI/CD | GitHub Actions |
| Messaging | Slack |
| Governance | AI Fabrik Runtime |
| Memory | CognitiveStore |

## Stand 09.05.2026

Phase A: Real Execution — CLI wrappers → typed REST connectors (GitHub, Vercel, Supabase)
Phase B: Operational Event Layer — Correlation, Idempotency, Compensation, Reconciliation
Phase C: Delivery Transaction Layer — Golden Path cross-system transactions

Branch: `phase-a-real-execution` (6 Commits)
Runtime: `backend/integration/live_agent_runtime.py` (1512 Zeilen)
