# NeXifyAI — Changelog

## 2026-04-05

### Chat-Bugfixes — Iteration 67 (100% Pass)
- **BUGFIX**: Chat-Blasen blinkten/flickerten bei jedem Re-Render
  - Ursache: CSS `animation: nxaiFadeIn` ohne Iterationslimit + React `key={index}`
  - Fix: `animation-iteration-count:1` + stabile Message-Keys (`m._key || m.message_id`)
- **BUGFIX**: AI rief JSON-Tool-Blöcke auf und konnte danach nicht mehr antworten
  - Ursache: Frontend versuchte Tools client-seitig auszuführen
  - Fix: Server-seitige Tool-Ausführung in `nexify_ai_routes.py` mit Follow-up-Streaming
  - Backend extrahiert `tool`-Blöcke, führt bis zu 5 Tools pro Turn aus, streamt Ergebnis-Interpretation
- **BUGFIX**: Chat scrollte unkontrolliert nach oben beim Tippen
  - Ursache: Auto-Scroll ohne Prüfung der User-Position
  - Fix: Smart Scroll — nur auto-scroll wenn User nah am Bottom (<150px)
- **VERBESSERUNG**: `scroll-behavior: smooth` entfernt (verhinderte verzögertes Scrolling)
- **VERBESSERUNG**: Session-Persistenz via localStorage `nx_active_convo` verifiziert

### NeXify AI Master Chat Interface — Iteration 65
- Arcee AI (trinity-large-preview) als LLM mit SSE-Streaming
- mem0 Brain-Integration: Kontextsuche vor jeder Antwort, asynchrones Speichern
- Conversation-Persistenz in MongoDB (nexify_ai_conversations + nexify_ai_messages)
- Admin-UI: Chat-Sidebar mit Konversationsliste, Brain-Toggle, Quick-Action-Buttons

### External API v1 — Iteration 64
- Externe API v1 mit API-Key-Authentifizierung (SHA-256 Hash, Rate-Limiting, Scopes)
- Endpoints: Contacts CRUD, Leads CRUD, Quotes/Contracts/Projects/Invoices Read, Stats, Webhooks

### P1 Content & Copywriting Overhaul (Iteration 63)
- TrustSection i18n Bugfix — war immer Deutsch, jetzt korrekt DE/NL/EN

### P0 Rechtstexte — Verifizierung (Iteration 62)
- 21 Legal-Routen verifiziert (7 Dokumente x 3 Sprachen)

## 2026-04-03
- Admin + Customer Portal Sidebar Harmonization (Iterations 60-61)
- Customer Portal Active Features (Requests, Bookings, Messages, Tickets)
- Comprehensive Legal Texts Implementation (7 documents x 3 languages)
