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

### AI Chat Optimization — April 2026
- **Markdown Rendering**: ReactMarkdown + remark-gfm for structured chat responses
  - Bold text, numbered lists, bullet points, headings, code blocks, blockquotes
  - Custom CSS styling (.chat-md) matching the dark premium theme
- **Upgraded System Prompt**: Detailed formatting instructions for structured responses
  - 7 core services documented with detailed descriptions
  - 400+ integrations reflected in prompt
  - Professional DACH-Business tone with clear response structure
  - Proactive consulting approach with follow-up questions
- **Enhanced Fallback Responses**: All 8+ response paths use markdown formatting

### Premium 3D Graphics v2.0 — April 2026
- **Process Pipeline**: Upgraded from 4 small diamonds to premium flow visualization
  - Hub nodes with wireframe icosahedrons, orbiting rings, and glowing cores
  - Animated particle streams flowing between nodes
  - Curved connectors with ambient environment particles
- **Orchestration Visual**: Hub-spoke diagram replacing basic spinning circles
  - Central core with animated rings
  - 4 satellite nodes (SAP/HubSpot, ERP/CRM, API, KI)
  - Animated pulse particles showing data flow
- **Integrations Globe**: Enhanced with additional rings, particles, and glow
  - 70 nodes (up from 50), 22 connection arcs (up from 16)
  - 3 orbital rings (equatorial, polar, angled)
  - 120 floating ambient particles
  - Central glow sphere

### Admin CRM Calendar & Customer Management — April 2026
- **Calendar View**: Monthly grid with booking badges and blocked slot indicators
- **Slot Blocking**: Create/delete blocked slots, affects public booking API
- **Customer CRM**: Aggregated customer list with leads/bookings count and detail view
- **Booking Management**: Status changes (6 statuses), notes, delete

### Multilingual System (DE/NL/EN) — April 2026
- IP-based auto-detection, Language Switcher, URL-based routing
- Complete translations for all sections, modals, legal pages
- Chat welcome messages in 3 languages
- LLM responds in selected language

### SEO Optimization — April 2026
- JSON-LD Structured Data, hreflang tags, Open Graph, Meta tags

### 400+ Integrations Messaging — April 2026
- 10 categories with 10 items each (100 named integrations)
- Technical badges: REST API, GraphQL, Webhooks, OAuth 2.0, SAML, gRPC

### 3D Animated Landing Page (v5.0)
- HeroScene: Neural network constellation, floating icosahedron core
- Premium CSS: glass-morphism, grain overlay, animated gradient borders

### LLM-Powered Chat
- GPT-4o-mini via Emergent key, multilingual, structured markdown responses
- Chat-based booking, dynamic date awareness, qualification tracking

### Legal & Compliance
- 4 legal pages fully translated to DE/NL/EN
- DSGVO/AVG/GDPR, EU AI Act Art. 52, Boek 6 BW

## Testing History
- Iteration 5-6: Backend 100%, Frontend 100% (multilingual, SEO)
- Iteration 7: 28/28 tests (Admin Calendar, Customer CRM, Chat translations)
- Iteration 8: 40/40 tests (Chat markdown, 3D graphics, orchestration visual, regressions)

## File Structure
```
/app/frontend/src/
├── App.js (Main landing - translation-aware, markdown chat)
├── App.css (Premium CSS v5.0 + chat markdown styles + orchestration hub)
├── index.js (HelmetProvider + LanguageProvider + Router)
├── index.css (CSS variables)
├── setupProxy.js (Custom proxy: /api only)
├── i18n/
│   ├── translations.js (DE/NL/EN)
│   └── LanguageContext.js (Provider + IP detection)
├── components/
│   ├── Scene3D.js (Premium 3D: Hero, Globe, Process Flow)
│   ├── LanguageSwitcher.js
│   └── SEOHead.js (JSON-LD + meta)
└── pages/
    ├── LegalPages.js (Translated legal content)
    ├── Admin.js
    └── Admin.css
```

## Upcoming Tasks
- P1: Automated email sequences (booking confirmation, reminders, follow-up)
- P1: Lighthouse Performance Optimization (3D lazy-loading, font preloading)
- P2: Analytics Dashboard in Admin area
- P2: App.js Refactoring (>730 lines → split into components)

## Backlog
- P1: Cookie settings granular page
- P2: Admin CSV export, MFA
- P3: A/B testing, analytics dashboard

---
*Letzte Aktualisierung: 02.04.2026 — Chat Markdown, Premium 3D Graphics v2.0, System Prompt Upgrade. All 40/40 tests PASSED.*
