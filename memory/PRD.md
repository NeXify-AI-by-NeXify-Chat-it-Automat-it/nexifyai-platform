# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. CI: #FE9B7B + White on #0c1117.

## Architecture
- Frontend: React 18 SPA | Backend: FastAPI | DB: MongoDB + Supabase PostgreSQL
- Auth: JWT + Magic Links + API Keys | LLM Master: Arcee AI (trinity-large-preview)
- LLM Sub-Agents: DeepSeek (deepseek-chat) | Memory: mem0 Brain
- Oracle: Supabase PostgreSQL (2.630+ Tasks, 10.144+ Brain-Notes, 33 AI-Agents)
- Engine: Autonomous 24/7 Task Processing (11 Scheduler-Jobs)
- Fonts: --f-display (Plus Jakarta Sans), --f-body (Inter), --f-mono (JetBrains Mono)

## Completed Features (All Verified — Iteration 76, 100% Pass)
- [x] Worker/Scheduler-Layer, Services scaffolding, Auth Security, 3D Hero
- [x] Design/Brand Harmonization (all breakpoints, unified tokens)
- [x] Admin + Customer Portal, Legal Texts (21 routes), External API v1
- [x] NeXify AI Master Chat (37+ Tools, CLI-first, Arcee AI + mem0)
- [x] P0 Fix: Right Panel Scroll & Sticky Header / Quick Action Buttons
- [x] Oracle Command Center (7 Tabs: Übersicht, Queue, Agenten, Brain, Tasks, Invoke, Engine)
- [x] Supabase PostgreSQL Integration (Live-Daten)
- [x] DeepSeek Sub-Agent Invocation (9 Agents: Nexus, Strategist, Forge, Lexi, Scout, Scribe, Pixel, Care, Rank)
- [x] 8 Oracle-Tools im Master System Prompt
- [x] Autonomous Engine: 24/7 Task Processing (PENDING→RUNNING→VERIFIED/FAILED→REASSIGNED)
- [x] Score-based Verification (score≥5 = passed, independent verifier agent)
- [x] Smart Keyword-based Agent Routing
- [x] Knowledge Aggregation (Brain + Knowledge + Memory + MongoDB → Supabase)
- [x] Font-Audit System (scans all CSS, identifies inconsistencies)
- [x] Task-Derivation (auto-derives new tasks from patterns)
- [x] Self-Learning (high-quality results stored as Brain-Notes)
- [x] Stuck Task Auto-Reset (running > 30min → pending)
- [x] DIN 5008 Communication Guidelines in System Prompt
- [x] AI-Team Structure (9 agents with roles and routing)
- [x] Health Check: Non-critical services (Email/WhatsApp) don't degrade overall status
- [x] Font Harmonization (var(--f-display/body/mono) throughout)

## Autonomous Engine — Task Lifecycle
```
PENDING → RUNNING (DeepSeek Execute with Knowledge Context)
  → REVIEW (Independent DeepSeek Verify, Score-based)
  → Score ≥ 5: COMPLETED + Brain-Note (Learning)
  → Score < 5: REASSIGNED (retry_count < 3) or FAILED (max retries)
```

## Scheduler Jobs (11)
1. Oracle Task-Processing (90s) | 2. Oracle Knowledge-Sync (30min) | 3. Oracle Task-Derivation (6h) | 4. Font-Audit (12h)
5. Zahlungsreminder (09:00) | 6. Mahnvorstufen (10:00) | 7. Lead-Follow-ups (08:30) | 8. Buchungserinnerungen (4h)
9. Angebotsablauf (12h) | 10. System-Health-Check (30min) | 11. Dead-Letter-Alerting (2h)

## Backlog
- [ ] DeepSeek Live-Migration für Master (P3)
- [ ] Legal & Compliance Guardian (P4)
- [ ] server.py Refactoring

## Testing: Iter 72-76, Final 100% Pass Rate
