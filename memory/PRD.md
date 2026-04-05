# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Fully premium, highly secure architecture with D/A/CH localization (EUR only, no $). CI design system relying strictly on coral accent (#FE9B7B) and White.

## Architecture
- Frontend: React 18 SPA | Backend: FastAPI (Python) | DB: MongoDB
- Auth: JWT + Magic Links (internal), API Keys (external)
- LLM: Arcee AI (trinity-large-preview) via OpenAI-compatible API
- Memory: mem0 Brain (pascal-courbois / nexify-ai-master / nexify-automate-core)
- Workers: APScheduler | CI: #FE9B7B and White only

## What's Been Implemented

### Completed (all verified 100%)
- [x] Worker/Scheduler-Layer (APScheduler)
- [x] Services scaffolding (comms, outbound, billing, llm_provider)
- [x] Public Auth Security + Hero 3D Scene
- [x] Design/Brand Harmonization (all breakpoints)
- [x] Admin + Customer Portal Sidebars (collapsed, tooltips)
- [x] Customer Portal Active Features (Requests, Bookings, Messages, Tickets)
- [x] Comprehensive Legal Texts (21 routes) — Iter 62
- [x] TrustSection i18n Fix — Iter 63
- [x] External API v1 (API Keys, 18+ endpoints) — Iter 64
- [x] NeXify AI Master Chat Interface — Iter 65
- [x] Color change #FF6B00 -> #FE9B7B — Iter 66
- [x] Chat flicker fix (streaming plain text) — Iter 66
- [x] Logo moved from sidebar to header — Iter 66
- [x] NeXify AI 37 operative Tools — Iter 66
- [x] Chat Bubble Flickering Fix (CSS animation-iteration-count:1 + stable keys) — Iter 67
- [x] Server-side Tool Execution Loop (backend executes tools, streams follow-up) — Iter 67
- [x] Smart Scroll Behavior (only auto-scroll near bottom) — Iter 67
- [x] Session Persistence (localStorage nx_active_convo) — Iter 67

### Backlog
- [ ] DeepSeek Live-Migration (P1)
- [ ] Legal & Compliance Guardian (P2)
- [ ] Outbound Lead Machine hardening (P3)
- [ ] server.py modular refactoring (after P1-P3 stable)
- [ ] Next.js Migration
- [ ] PydanticAI + LiteLLM + Temporal Adoption

## NeXify AI Tools (37 total)
list_contacts, create_contact, list_leads, create_lead, list_quotes, list_contracts, list_projects, list_invoices, system_stats, send_email, search_brain, store_brain, list_conversations, audit_log, list_api_keys, db_query, db_write, worker_status, timeline, web_search, http_request, scrape_url, execute_python, execute_shell, list_agents, create_agent, update_agent, delete_agent, invoke_agent, schedule_task, list_scheduled_tasks, delete_scheduled_task, read_file, write_file, list_files, self_status, update_config

## Testing History
- Iteration 60-65: All 100% Pass
- Iteration 66: Full Audit — 100% Pass (14/14 backend + all frontend + color audit)
- Iteration 67: Chat Bug Fixes — 100% Pass (9/9 backend + all frontend UI verified)
