# NeXifyAI Landing Page — Product Requirements Document

## Original Problem Statement
Premium DACH B2B landing page for "NeXifyAI by NeXify" — enterprise AI automation. Core claim: "Chat it. Automate it." Primary goal: generate qualified B2B strategy calls. Target: DACH + NL + Global. Real 3D animated web experience with full multilingual support.

## Brand Identity
- **Name**: NeXify**AI** — "AI" ALWAYS highlighted in CI accent color (#ff9b7a)
- **Entity**: NeXify Automate (NL, KvK: 90483944)
- **CSS class**: `.brand-ai` for consistent accent highlighting
- **LLM fallback**: NeXify**AI** (bold markdown)

## Architecture
- Frontend: React 18, @react-three/fiber v8, react-markdown, remark-gfm
- Backend: FastAPI, MongoDB (motor), JWT+Argon2 auth
- LLM: GPT-4o-mini via Emergent LLM Key
- Email: Resend API
- i18n: Custom React Context (DE/NL/EN)

## Implemented Features (All Verified)

### CI-konforme Markenhervorhebung — Iteration 12 (April 2026)
- BrandName component for consistent rendering across app
- .brand-ai CSS class for accent color highlighting
- Applied: Nav logo, Hero label, Chat sidebar, Footer
- System prompt instructs LLM to write NeXify**AI**

### Lead-orientierter Chat — Iteration 12
- System prompt: GESPRÄCHSFÜHRUNG section (proactive, inviting, trust-building)
- Welcome: structured 3-point menu (Prozessanalyse, Systemintegration, Use Cases)
- Presets: Lead-oriented ("Was kann KI in meiner Branche leisten?")
- CTA: "Kostenloses Strategiegespräch"

### UI Polish — Iteration 11
- All buttons rounded (6-8px), modals (12px), chat trigger (50px pill)
- Language switcher: premium pill with active glow
- Form alignment, enhanced 3D, JetBrains Mono typography

### Earlier Iterations (7-10)
- Admin CRM + Calendar, Chat markdown, Form labels, SVG icons

## Testing History
- Iteration 7: 28/28 | 8: 40/40 | 9: 40/40 | 10: 40/40 | 11: 100% | 12: 100% (14/14 backend + all frontend)

## Upcoming Tasks
- P1: Automated email sequences (booking confirmation, 24h reminder, 48h follow-up)
- P1: Lighthouse Performance Optimization
- P2: Analytics Dashboard in Admin
- P2: App.js Refactoring (>740 lines)

## Backlog
- Cookie settings granular page, Admin CSV export, MFA, A/B testing

---
*Last updated: 02.04.2026 — CI-brand highlighting, lead-oriented chat, system prompt v3. Iteration 12: 100% tests PASSED.*
