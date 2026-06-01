# AI Fabrik — Architecture

## System Overview

```
                         ┌──────────────────────┐
                         │   Hermes Agent        │
                         │   (Runtime Gateway)   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Cognitive Bus       │
                         │   (Event Federation)  │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼──────┐   ┌─────────▼──────┐   ┌─────────▼──────┐
    │  Brain Governor │   │  Governance     │   │  Skill Runtime  │
    │  (Access)       │   │  Kernel         │   │  (Manifests)    │
    └─────────┬──────┘   └─────────┬──────┘   └─────────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Unified Memory      │
                         │   (5-Type Taxonomy)   │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼──────┐   ┌─────────▼──────┐   ┌─────────▼──────┐
    │  GitHub MCP     │   │  Vercel API     │   │  Supabase API   │
    │  (REST)         │   │  (REST)         │   │  (3-Layer)      │
    └────────────────┘   └────────────────┘   └────────────────┘
```

## Cognitive Architecture

```
SENSORISCH              ARBEITSGEDÄCHTNIS        LANGZEITGEDÄCHTNIS
(Context Window)        (Prompt Context)         (Persistent Store)
     │                        │                 ┌─ EPISODIC   (Event Ledger)
 Millisekunden            Sekunden               │   Delivery Runs
     │                        │                 ├─ SEMANTIC   (Knowledge Graph)
     ▼                        ▼                 │   Fakten, Regeln
[LLM Input]  ────────►  [Reasoning]  ────────►  ├─ PROCEDURAL (Skill Manifests)
                                                 │   Workflows
                                                 ├─ GRAPH      (Entity Edges)
                                                 │   Kausalitäten
                                                 └─ PARAMETRIC (Model Weights)
                                                     Embeddings
```

## Tech Stack

| Layer | System |
|-------|--------|
| AI Runtime | NeXify via OpenRouter |
| Governance | BrainGovernor + GovernanceKernel |
| Event Bus | CognitiveBus (pub/sub) |
| Memory | Unified Memory (SQLite, 5-Type) |
| Knowledge | Ingestion Pipeline + Knowledge Graph |
| Skills | Skill Manifests (YAML, typed) |
| Vector | Qdrant |
| Database | Supabase (PostgreSQL + RLS) |
| Hosting | Vercel (Frontend) + VPS (Backend) |
| CI/CD | GitHub Actions |
| Communication | Slack Bridge + Cognitive Bus |
