# NeXifyAI Platform — Architecture

## Domain
nexifyai.cloud — Cognitive Enterprise Platform

## Core Principles
1. **Governance-first** — All runtime passes Governance Bootstrap before execution
2. **Brain-centric** — Qdrant-based knowledge persistence for agents, decisions, and memory
3. **Temporal-routed** — Async workflows via Temporal.io with circuit breaker + DLQ
4. **Self-healing** — Runtime monitors, detects drift, auto-repairs within governance bounds
5. **Organizationally persistent** — Every decision, error, and insight feeds the Brain

## Stack

| Layer | Technology | Location |
|-------|-----------|----------|
| Frontend | React 18 SPA + react-three-fiber | `apps/web/` |
| Admin Panel | Next.js 14 | `apps/admin-chat/` |
| API Server | FastAPI + Uvicorn | `services/api/` |
| Temporal Workers | Python Temporal SDK | `services/temporal/` |
| Agent Runtime | Python (Hermes Gateway) | `ai-runtime/agents/` |
| Governance | Python (Governance Bootstrap) | `governance/` |
| Knowledge Base | Qdrant (4096-dim vectors) | Local :6333 |
| Database | Supabase (PostgreSQL) | Cloud |
| Queue | Redis | Local :6379 |

## Directory Layout

```
nexifyai-platform/
├── apps/              # User-facing applications
│   ├── web/           #   Landing page (React SPA)
│   └── admin-chat/    #   Admin dashboard (Next.js)
├── services/          # Backend services
│   ├── api/           #   FastAPI REST server
│   └── temporal/      #   Temporal workflow workers
├── ai-runtime/        # AI agent infrastructure
│   ├── agents/        #   Agent profiles + orchestrators
│   ├── scripts/       #   Runtime automation scripts
│   └── profiles/      #   CEO, PM, skill definitions
├── packages/          # Shared packages
│   └── ai-farbrik/    #   Cognitive kernel packages
├── infrastructure/    # Deployment & operations
│   ├── supabase/      #   Database migrations (PostgreSQL)
│   └── docker/        #   Container definitions
├── governance/        # Platform governance
│   ├── bootstrap.py   #   Startup governance checks
│   ├── circuit_breaker.py
│   ├── dlq.py
│   └── metrics.py
├── knowledge/         # Organizational knowledge base
│   ├── brain/         #   Qdrant collection schemas
│   └── emergent/      #   Historical site artifacts (rescued SourceMaps)
├── docs/              # Documentation
│   ├── systems/       #   System architecture docs (SYS-001..012)
│   ├── legal/         #   Legal documents (AGB, Impressum, DSGVO)
│   └── infrastructure/ #  Connection inventory, deployment guides
└── .anton/            # Anton workspace configuration
```

## Governance Flow

```
Startup → Runtime Discovery → Config Validation → Capability Check
  → Drift Detection → Auto-Repair → Governance Report → Workflow Gate
  
  PASS → Workflows execute (Temporal workers)
  FAIL → Block execution, log to Brain, notify admin
```

## Recovery

All services have:
- **Circuit Breaker** — Prevents cascade failures
- **DLQ (Dead Letter Queue)** — Captures failed operations for replay
- **Governance Bootstrap** — Validates runtime health before accepting work
- **Brain persistence** — Every error and recovery feeds Qdrant for learning
