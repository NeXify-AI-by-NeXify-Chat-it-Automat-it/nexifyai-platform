# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-first commercial system "Starter/Growth AI Agenten AG" for NeXifyAI. Full-stack platform with React frontend, FastAPI backend, MongoDB. Multi-language (DE/NL/EN). Revolut Merchant API for payments. Enterprise-grade compliance (DSGVO, EU AI Act).

## Core Requirements (Static)
1. Landing page with 3D, multi-language, Trust/Compliance, Chat Discovery
2. Commercial Engine: Quotes, Invoices, PDF generation, Revolut payment
3. Magic Link customer portal for quote acceptance
4. Admin Dashboard for commercial management
5. Premium Integrations section (categorized, SEO-linked)
6. Dedicated SEO landing pages per integration (/integrationen/:slug)
7. KI-gesteuertes SEO as standalone product with pricing, FAQ, bundles
8. Full Services + Bundles pricing architecture
9. PDF tariff comparison sheets (CI-branded, per category)
10. Legal compliance (AGB, Datenschutz, KI-Hinweise) — trilingual
11. Trust section with operational security visibility
12. AI advisor with full product matrix mapping

## Central Tariff System
All products managed in `commercial.py`:
- TARIFF_CONFIG: KI-Agenten (2 tiers, 24 months, 30% deposit)
- SERVICE_CATALOG: 10 services (3 websites, 2 apps, 3 SEO, 2 add-ons)
- BUNDLE_CATALOG: 3 bundles (Digital Starter, Growth Digital, Enterprise Digital)
- PRODUCT_DESCRIPTIONS: 12 professional product descriptions (starter, growth, web_starter, web_professional, web_enterprise, app_mvp, app_professional, seo_starter, seo_growth, seo_enterprise, ai_addon_chatbot, ai_addon_automation)

## API Endpoints
- GET /api/product/tariff-sheet?category=all|agents|websites|seo|apps|addons|bundles
- GET /api/product/descriptions (12 products)
- GET /api/product/tariffs
- GET /api/product/services
- GET /api/product/faq (18 items)
- GET /api/product/compliance
- POST /api/commercial/quote
- GET /api/commercial/portal/{token}
- POST /api/chat/message
- POST /api/booking
- GET /api/booking/slots

## Architecture (Post-Refactoring)
```
/app/frontend/src/
├── App.js (482 lines — Nav, Hero, Solutions, UseCases, AppDev, Process, Governance, Pricing, FAQ, Contact, Footer, CookieConsent)
├── components/
│   ├── sections/
│   │   ├── Integrations.js (119 lines)
│   │   ├── LiveChat.js (113 lines)
│   │   ├── SEOProductSection.js (82 lines)
│   │   ├── ServicesAll.js (79 lines)
│   │   ├── TrustSection.js (63 lines)
│   │   └── BookingModal.js (76 lines)
│   ├── shared/
│   │   └── index.js (61 lines — API, COMPANY, animations, utilities)
│   ├── Scene3D.js, SEOHead.js, LanguageSwitcher.js
│   └── ui/ (Shadcn components)
├── data/ (integrations.js, products.js)
├── pages/ (IntegrationDetail.js, LegalPages.js, QuotePortal.js)
└── i18n/ (LanguageContext.js, translations.js)
```

## Testing Status
- Iteration 16: 100% (23/23 automated tests)
- Iteration 17: 100% Backend (19/19) + 100% Frontend (13 feature categories all PASS)

## Completed (Phase 3 — 2026-04-03)
- 76 ASCII umlaut corrections across 7 files, zero remaining
- Header/Nav breakpoints verified on 1920px, 1100px, 375px — all clean
- Frontend/Backend data sync verified — 15 products perfectly matched
- PRODUCT_DESCRIPTIONS expanded from 6 to 12 (all services covered)
- FAQ expanded with corrected bundle descriptions + SEO tariffs (18 items total)
- PDF tariff sheets verified — 4 pages, no encoding errors, correct company data
- All API endpoints functional and tested
- App.js refactored from 1049 → 482 lines (6 component files extracted)
- Documentation updated (CHANGELOG, TECHNICAL_DOCS, PRD)

## Prioritized Backlog
### P0 — None remaining

### P1 (Next)
- Resend live API key activation (email sending)
- Revolut Merchant API live keys (payment processing)
- Dunning logic for overdue invoices
- Admin CSV export for quotes/invoices
- Subscription API for recurring billing

### P2 (Future)
- A/B testing CTAs
- Customer dashboard beyond magic link portal
- Multi-tenant support
- Swagger/OpenAPI documentation
- CI/CD pipeline with E2E tests
- Performance optimization (Lighthouse 95+)
