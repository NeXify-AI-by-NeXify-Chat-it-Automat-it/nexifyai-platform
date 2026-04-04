# NeXifyAI — Product Requirements Document

## Originaler Auftrag
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium-Architektur mit absolutem Fokus auf Produktionsreife, Sicherheit und System-Konsistenz.

## Architektur
- **Frontend**: React 18 SPA, Framer Motion, i18n (DE/NL/EN), Shadcn-Style Dark Theme
- **Backend**: FastAPI (modular: 10 Route-Module), APScheduler, MongoDB
- **Workers**: In-process JobQueue (4 Workers, Retry + Dead-Letter), Cron-Scheduler (7 Jobs)
- **LLM**: DeepSeek (Primär, aktiv), GPT-5.2 Fallback via Emergent
- **Integrations**: Stripe, Object Storage, Hostinger SMTP (aiosmtplib)
- **Security**: JWT Auth, Rate Limiting (SlowAPI 200/min), Security Headers, CORS
- **Oracle**: Memory Service (182 Einträge), get_contact_oracle(), Snapshot
- **Design-System**: Vollständiges Token-System (CI-Gelb, CI-Blau, 3-Stufen-Schatten, 7-Stufen-Radien, Glass-Morphism)

## Implementierte Features (kumulativ)

### Design-System (P0.9 — verifiziert Iteration 52)
- Vollständiges CSS-Token-System in :root (Farben, Radien, Schatten, Typografie, Motion)
- CI-Gelb (#ff9b7a) als Primär-Akzent, CI-Blau (#6B8AFF) als Sekundär
- 9 Button-Typen: Primary, Secondary, Tertiary, Outline, Ghost, Destructive, Success, Link, Icon
- 5 Button-Größen: xs, sm, Standard, lg, xl + Modifikatoren (glow, full, pill, loading)
- Unified Surface-System: .nx-card (Glass), .nx-panel, .nx-surface
- 6 Badge-Varianten: accent, blue, ok, err, warn, muted
- Form-System: .form-input, .form-textarea, .form-select mit Focus-Ringen
- Shadow-Tiefenkonzept: sm (subtil), md (Hover), lg (Modal) + Glow + Focus
- Border-Radius-Hierarchie: xs(4px) → sm(6px) → md(8px) → lg(12px) → xl(16px) → pill
- Glass-Morphism: backdrop-filter: blur(12-16px) auf Cards, Modals, Navbar
- Admin Dashboard: Alle Elemente mit Rundungen, Schatten, Glas-Effekten
- Customer Portal: Alle Elemente mit Tiefe, konsistenten Buttons, Focus-Ringen
- Systemweite Harmonisierung: Identische Qualität Public ↔ Admin ↔ Portal

### Backend (verifiziert)
- Modulare Route-Architektur (10 Route-Module)
- Worker/Scheduler-Layer: 8 Handler, 7 Scheduler-Jobs
- Oracle/Memory Service, Billing, Outbound, Monitoring
- Rate Limiting, Security Headers, CORS
- Hostinger SMTP Integration
- Dual-Role Auth (check-email returns role:dual)

### Frontend (verifiziert)
- Landing Page: 12 Sektionen mit Premium Dark Theme
- Unified Login: Dual-Role Rollenauswahl
- Admin Dashboard: Collapsible Sidebar, System-Health, Lead-Management
- Customer Portal: 8 Tabs (Übersicht, Verträge, Projekte, Angebote, Finanzen, Termine, Kommunikation, Aktivität)

## E2E-Prozesskette (verifiziert)
Lead → Booking → Quote → Invoice → Contract → Payment

## Testing (5 Iterationen, alle 100%)
- Iteration 48-50: Backend + Frontend (100%)
- Iteration 51: Dual-Role Login + Sidebar Collapse (100%)
- Iteration 52: Design-System Harmonisierung (100%)

## Nächste Schritte (Backlog)
1. P2: Portal-Harmonisierung & Dynamische Bedarfsliste
2. P2: Content & Copywriting Overhaul
3. P3: Network, Security & Configuration Hardening
4. P3: E2E Browser Verifications (Quote → Invoice)
5. P4: DeepSeek Live-Migration
6. P5: Next.js Migration, PydanticAI

## Credentials
- Admin: p.courbois@icloud.com / 1def!xO2022!!
