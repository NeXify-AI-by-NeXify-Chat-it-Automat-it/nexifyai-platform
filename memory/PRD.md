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
- [x] Color change #FF6B00 → #FE9B7B — Iter 66
- [x] Chat flicker fix (streaming plain text) — Iter 66
- [x] Logo moved from sidebar to header — Iter 66
- [x] SMTP password updated — Iter 66
- [x] NeXify AI 18+ operative Tools (contacts, leads, email, brain, web search, db_query, etc.) — Iter 66

### Backlog
- [ ] DeepSeek Live-Migration
- [ ] Projektchat / Build-Handover-Kontext härten
- [ ] Revolut Live-Webhooks & Billing-Status-Sync
- [ ] server.py modular refactoring
- [ ] Next.js Migration

## NeXify AI Tools (19 total)
list_contacts, create_contact, list_leads, create_lead, list_quotes, list_contracts, list_projects, list_invoices, system_stats, send_email, search_brain, store_brain, list_conversations, audit_log, list_api_keys, db_query, worker_status, timeline, web_search

## Testing History
- Iteration 60-65: All 100% Pass
- Iteration 66: Full Audit — 100% Pass (14/14 backend + all frontend + color audit)
