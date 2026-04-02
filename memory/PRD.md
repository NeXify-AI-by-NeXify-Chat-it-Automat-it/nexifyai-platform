# NeXifyAI Landing Page — Product Requirements Document

## Original Problem Statement
Premium DACH B2B landing page for "NeXifyAI by NeXify" — enterprise AI automation. Core claim: "Chat it. Automate it." Primary goal: generate qualified B2B strategy calls. Target: DACH + NL + Global. **Real 3D animated web experience with full multilingual support.**

## Brand & Legal
- **Name**: NeXifyAI by NeXify | **Entity**: NeXify Automate (NL, KvK: 90483944)
- **CEO**: Pascal Courbois | **USt-ID**: NL865786276B01
- **Applicable Law**: Dutch (Burgerlijk Wetboek), DSGVO/UAVG, EU AI Act

## Architecture
- Frontend: React 18 (CRA, port 3000) with Three.js 3D animations
- Backend: FastAPI (port 8001), MongoDB (motor), JWT+Argon2 auth
- 3D: @react-three/fiber v8.18.0, @react-three/drei v9.122.0, three v0.170.0
- LLM: GPT-4o-mini via Emergent LLM Key (emergentintegrations)
- Email: Resend API
- i18n: Custom React Context + translations.js (DE/NL/EN)
- SEO: react-helmet-async, JSON-LD, hreflang, Open Graph
- Chat Markdown: react-markdown + remark-gfm

## Implemented Features

### Form Label Bug Fix + i18n Completion — April 2026
- **Fixed duplicate labels**: Contact & Booking forms previously showed "Name" twice, now correctly show "Vorname/Nachname" (DE), "First Name/Last Name" (EN), "Voornaam/Achternaam" (NL)
- **Fixed hardcoded "Telefon"**: Phone label now translated across all 3 languages
- **Added separate validation messages**: firstName and lastName get individual error messages
- **Complete i18n coverage**: All form fields (firstName, lastName, email, phone, company, message) fully translated DE/EN/NL

### AI Chat Optimization — April 2026
- **Markdown Rendering**: ReactMarkdown + remark-gfm for structured chat responses (bold, lists, headings, code)
- **Upgraded System Prompt**: 7 core services, 400+ integrations, professional formatting, proactive consulting
- **Enhanced Fallback Responses**: All 8+ paths use structured markdown

### Premium 3D Graphics v2.0 — April 2026
- **Process Pipeline**: Hub nodes with wireframe icosahedrons, orbiting rings, animated particle streams
- **Orchestration Visual**: Hub-spoke with 4 satellite nodes (SAP/HubSpot, ERP/CRM, API, KI)
- **Integrations Globe**: 70 nodes, 22 connection arcs, 3 orbital rings, 120 ambient particles

### Admin CRM Calendar & Customer Management — April 2026
- Calendar with monthly grid, booking badges, slot blocking
- Customer CRM: aggregated list, detail view
- Lead management: 6 statuses, notes, search

### Multilingual System (DE/NL/EN)
- IP-based auto-detection, Language Switcher, complete translations
- Chat welcome messages in 3 languages, LLM language-aware

### Other Features
- SEO (JSON-LD, hreflang, OG), 400+ Integrations messaging, Legal pages (4 pages, 3 languages)
- Booking flow (date/time/form), Contact form with honeypot
- Analytics tracking, Cookie consent, Rate limiting

## Testing History
- Iteration 7: 28/28 (Admin Calendar, CRM, Chat translations)
- Iteration 8: 40/40 (Chat markdown, 3D graphics v2.0, orchestration visual)
- Iteration 9: 40/40 (Form labels fix, i18n completion, NL translation fix)

## File Structure
```
/app/frontend/src/
├── App.js (Main landing - translation-aware, markdown chat)
├── App.css (Premium CSS v5.0 + chat markdown + orchestration hub)
├── i18n/ (translations.js, LanguageContext.js)
├── components/ (Scene3D.js, LanguageSwitcher.js, SEOHead.js)
└── pages/ (Admin.js, Admin.css, LegalPages.js)
/app/backend/
├── server.py (FastAPI, MongoDB, JWT, LLM, Admin)
└── tests/ (test_admin_calendar.py, test_chat_markdown.py)
```

## Upcoming Tasks (Prioritized)
- P1: Automated email sequences (booking confirmation, 24h reminder, 48h follow-up)
- P1: Lighthouse Performance Optimization (3D lazy-loading, font preloading, code-splitting)
- P2: Analytics Dashboard in Admin area (conversion funnel, lead trends)
- P2: App.js Refactoring (>740 lines → split into components)

## Backlog
- Cookie settings granular page
- Admin CSV export, MFA
- A/B testing framework

---
*Last updated: 02.04.2026 — Form labels fix, i18n completion, NL translation fix. Iteration 9: 40/40 tests PASSED.*
