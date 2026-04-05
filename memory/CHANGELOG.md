# NeXifyAI — Changelog

## 2026-04-04

### External API v1 — Vollständig implementiert (Iteration 64)
- **Neues Feature**: Externe API v1 mit API-Key-Authentifizierung
  - `/api/v1/health`, `/api/v1/docs` (öffentlich)
  - Contacts CRUD: GET/POST/PUT `/api/v1/contacts`
  - Leads CRUD: GET/POST `/api/v1/leads`
  - Read-Only: `/api/v1/quotes`, `/api/v1/contracts`, `/api/v1/projects`, `/api/v1/invoices`
  - System Stats: `/api/v1/stats`
  - Webhooks: GET/POST/DELETE `/api/v1/webhooks`
- **API-Key-System**: SHA-256 Hash-Speicherung, Rate-Limiting, Scope-basierte Berechtigungen, Ablaufdatum
- **Admin-Panel**: API-Zugang View mit Key-Verwaltung, cURL-Beispiele, API-Dokumentation Link
- Neue Dateien: `/app/backend/routes/api_v1_routes.py`, Tests: `/app/backend/tests/test_api_v1_external.py`

### P1 Content & Copywriting Overhaul (Iteration 63)
- **BUGFIX**: TrustSection i18n — war immer Deutsch, jetzt korrekt DE/NL/EN via `useLanguage()` Hook
- Erweiterte Trust-Copy in 3 Sprachen (DSGVO, EU AI Act, ISO 27001/27701 Referenzen)

### P0 Rechtstexte — Verifizierung (Iteration 62)
- 21 Legal-Routen verifiziert (7 Dokumente x 3 Sprachen)
- Footer-Links, Legacy-Redirects, Sprachumschalter getestet

## 2026-04-03

### Admin Sidebar Harmonization (Iteration 60)
- Admin sidebar collapsed by default with CSS hover tooltips (::after)
- Customer Portal sidebar follows same pattern (Iteration 61)

### Customer Portal Active Features (Iteration 61)
- Added backend APIs for requests, bookings, messages, support tickets
- Full CRUD UI forms in Customer Portal
- Quote/Contract workflows functional

### Comprehensive Legal Texts Implementation
- LegalPages.js with 7 legal documents (Impressum, Datenschutz, AGB, KI-Hinweise, Widerruf, Cookies, AVV)
- Full translations for DE/NL/EN with proper URL slugs per language
- Footer updated with all 7 legal links
- LEGAL_PATHS in shared/index.js updated
