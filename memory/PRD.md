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

## Implemented Features

### Multilingual System (DE/NL/EN) — April 2026
- **IP-based auto-detection**: Uses ipapi.co (fallback: ip-api.com) for country → language mapping
  - DE/AT/CH → German, NL/BE → Dutch, rest → English
- **Language Switcher**: Premium pill-buttons (DE|NL|EN) in header nav + mobile menu
- **URL-based routing**: /:lang prefix (e.g., /de, /nl, /en)
- **Complete translations**: All landing page sections, modals (chat, booking), cookie consent, footer
- **Legal pages in 3 languages**: Language-specific URL slugs
  - DE: /de/impressum, /de/datenschutz, /de/agb, /de/ki-hinweise
  - NL: /nl/impressum, /nl/privacybeleid, /nl/voorwaarden, /nl/ai-informatie
  - EN: /en/imprint, /en/privacy, /en/terms, /en/ai-transparency
- **Legacy redirect**: /impressum → /:lang/impressum (based on stored preference)
- **localStorage persistence**: Key `nx_lang`
- **Backend language support**: Chat API accepts `language` parameter, LLM responds in correct language
- **Admin excluded**: /admin stays language-neutral (German)

### SEO Optimization — April 2026
- **JSON-LD Structured Data**: Organization, WebSite, Service schemas
- **hreflang tags**: de, nl, en, x-default
- **Open Graph**: Locale-aware OG tags (de_DE, nl_NL, en_GB)
- **Meta tags**: Language-specific title, description, keywords
- **Canonical URLs**: Per-language canonicals
- **HTML lang attribute**: Dynamic (de-DE, nl-NL, en-GB)

### 400+ Integrations Messaging — April 2026
- Counter updated from 64+ to 400+ across all languages
- 10 categories with 10 items each (100 named integrations)
- Custom note: "Every integration is achievable" in all 3 languages
- Technical badges: REST API, GraphQL, Webhooks, OAuth 2.0, SAML, gRPC

### 3D Animated Landing Page (v5.0)
- HeroScene: Neural network constellation, floating icosahedron core
- IntegrationsGlobe: Wireframe sphere with connection arcs
- ProcessScene: Pipeline nodes with glow rings
- Premium CSS: glass-morphism, grain overlay, animated gradient borders

### LLM-Powered Chat
- GPT-4o-mini via Emergent key, now with multilingual responses
- Context-aware, chat-based booking, dynamic date awareness

### Admin CRM (/admin)
- JWT login (Argon2), dashboard with stats/leads/bookings
- Search, filter, sort, status management, rate limiting

### Legal & Compliance
- 4 legal pages fully translated to DE/NL/EN
- DSGVO/AVG/GDPR, EU AI Act Art. 52, Boek 6 BW

## Testing (Iterations 5-6) — April 2026
- Backend: 100% (15/15 multilingual API tests passed)
- Frontend: 100% (all features verified including language switching, legal pages, SEO)

## File Structure
```
/app/frontend/src/
├── App.js (Main landing - translation-aware)
├── App.css (Premium CSS v5.0)
├── index.js (HelmetProvider + LanguageProvider + Router)
├── index.css (CSS variables)
├── setupProxy.js (Custom proxy: /api only)
├── i18n/
│   ├── translations.js (DE/NL/EN)
│   └── LanguageContext.js (Provider + IP detection)
├── components/
│   ├── Scene3D.js (Three.js scenes)
│   ├── LanguageSwitcher.js
│   └── SEOHead.js (JSON-LD + meta)
└── pages/
    ├── LegalPages.js (Translated legal content)
    ├── Admin.js
    └── Admin.css
```

## Upcoming Tasks
- P1: Lighthouse Performance Optimization (3D lazy-loading, font preloading)
- P2: Final E2E Visual Audit across all languages

## Backlog
- P1: Cookie settings granular page
- P2: Admin CSV export, MFA
- P3: A/B testing, analytics dashboard

---
*Letzte Aktualisierung: 02.04.2026 — Multilingual (DE/NL/EN), SEO, 400+ Integrations deployed. All tests PASSED.*
