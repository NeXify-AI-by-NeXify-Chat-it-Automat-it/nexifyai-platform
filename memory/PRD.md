# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium, secure architecture. CI: #FE9B7B + White on #0c1117.

## Architecture
- Frontend: React 18 SPA | Backend: FastAPI | DB: MongoDB + Supabase PostgreSQL
- Auth: JWT + Magic Links + API Keys | LLM Master: Arcee AI (trinity-large-preview)
- LLM Sub-Agents: DeepSeek (deepseek-chat) | Memory: mem0 Brain
- Oracle System: Supabase PostgreSQL (2.625+ Tasks, 10.144+ Brain-Notes, 156 Knowledge, 33 AI-Agenten, 5.800+ Audit-Logs)
- Autonomous Engine: APScheduler (11 Jobs) — Tasks processing every 90s, Knowledge-Sync every 30min, Task-Derivation every 6h, Font-Audit every 12h
- Workers: APScheduler (Hintergrund-Jobs)
- Fonts: --f-display: Manrope, --f-body: Inter, --f-mono: JetBrains Mono

## Completed Features
- [x] Worker/Scheduler-Layer, Services scaffolding, Auth Security, 3D Hero
- [x] Design/Brand Harmonization (all breakpoints, unified tokens)
- [x] Admin + Customer Portal, Legal Texts (21 routes), External API v1
- [x] NeXify AI Master Chat (37+ Tools, CLI-first, Arcee AI + mem0)
- [x] P0 Fix: Right Panel Scroll & Sticky Header Bug
- [x] P0 Fix: Chat Quick Action Buttons
- [x] Oracle Command Center (7 Tabs): Übersicht, Task-Queue, Agenten, Brain, Oracle-Tasks, Agent aufrufen, Autonome Engine
- [x] Supabase PostgreSQL Integration (Live-Daten)
- [x] DeepSeek Sub-Agent Invocation (Strategist, Forge, Lexi, Care, Scout, Scribe, Rank, Nexus)
- [x] 8 Oracle-Tools im Master System Prompt
- [x] Autonomous Oracle Engine: 24/7 Task Processing (PENDING→ASSIGNED→RUNNING→VERIFIED/FAILED→REASSIGNED)
- [x] Independent Verification Loop (Verifikation durch zweiten DeepSeek-Agenten)
- [x] Knowledge Aggregation (Brain, Knowledge, Memory, MongoDB → Supabase)
- [x] Font-Audit System (scannt alle CSS, identifiziert Inkonsistenzen)
- [x] Task-Derivation (automatisch neue Tasks aus Daten ableiten)
- [x] Self-Learning (hochwertige Ergebnisse als Brain-Notes speichern)
- [x] Font-Harmonisierung (JetBrains Mono → var(--f-mono))

## Autonomous Engine — Task Lifecycle
```
PENDING → ASSIGNED (Agent via AGENT_ROUTING) → RUNNING (DeepSeek Execute)
  → REVIEW (Independent DeepSeek Verify) → VERIFIED (✓ → Brain-Note + Completed)
                                          → FAILED (← retry_count < 3 → REASSIGNED)
                                          → DEAD (retry_count >= 3)
```

## Scheduler Jobs (11 total)
1. Oracle Task-Processing (90s) | 2. Oracle Knowledge-Sync (30min)
3. Oracle Task-Derivation (6h) | 4. Oracle Font-Audit (12h)
5. Zahlungsreminder (09:00) | 6. Dunning (10:00) | 7. Lead-Follow-ups (08:30)
8. Booking-Reminder (4h) | 9. Quote-Expiry (12h) | 10. Health-Check (30min) | 11. Dead-Letter (2h)

## Backlog
- [ ] Typography/DIN-Norm Harmonisierung (P1)
- [ ] Full e2e UI Audit aller Views (P2)
- [ ] DeepSeek Live-Migration für Master (P3)
- [ ] Legal & Compliance Guardian (P4)
- [ ] server.py Refactoring (nach P1-P4)

## Testing: Iter 72-74 — 93-100% pass rates
