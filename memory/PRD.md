# NeXifyAI — Product Requirements Document

## Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator (DeepSeek Ziel), CRM, Login-Stack, Worker/Scheduler, Kommunikationskern, Outbound Lead Machine, Billing-Sync. Systemweit harmonisiertes Design, Security by Obscurity.

## Architecture
- **API-First**: Domain → Channel → Connector → Agent → Event/Audit Layer
- **Unified Auth**: /login → Admin (Passwort) / Kunde (Magic Link) / Registrierung → Role-based JWT
- **Security by Obscurity**: /admin → /login redirect, keine internen Terminologien öffentlich
- **mem0 Memory Layer**: Pflicht-Scoping (user_id, agent_id, app_id, run_id)
- **LLM-Abstraktionsschicht**: EmergentGPTProvider (TEMPORÄR) | DeepSeekProvider (ZIEL)
- **Worker/Scheduler**: asyncio JobQueue (4 Worker) + APScheduler (7 Cron-Jobs)
- **Services**: CommunicationService, BillingService, OutboundLeadMachine

## What's Implemented & Verified

### Design & Brand Harmonisierung — VERIFIZIERT (Iteration 27: 16/16 — 100%)
- **Brand-Konsistenz**: icon-mark.svg + NeXifyAI Text identisch in Header, Footer, Login, Portal, Admin
- **Einheitliche Typografie**: Plus Jakarta Sans (Display) + Inter (Body) via CSS-Variablen in allen Komponenten
- **Button-Systematik**: Solid var(--nx-accent) + dunkle Schrift (#0c1117), border-radius: 6px — einheitlich Login, Public, E-Mail
- **Input-Styling**: border-radius: 4px, var(--nx-bg) Hintergrund, accent-border on focus
- **Farbtokens**: --nx-accent (#ff9b7a), --nx-bg (#0c1117) durchgängig in CSS, E-Mail-Templates, PDFs (CI_ORANGE)
- **Footer**: IBAN via .footer-iban CSS-Klasse statt Inline-Styles, KvK/USt-ID/IBAN korrekt
- **E-Mail-Template**: Konsistente Signatur, DSGVO-Footer, Legal-Links
- **PDFs**: CI_ORANGE/CI_DARK Color-Konstanten, gleiche Brand-Anmutung

### Login — Premium Two-Column — VERIFIZIERT (Iteration 27)
- Linke Spalte: icon-mark.svg + NeXifyAI, Tagline, Feature-Bullets (Verschlüsselt/Echtzeit/DSGVO)
- Rechte Spalte: "Sicherer Zugang", E-Mail-Check → Passwort / Magic-Link / Registration
- Tablet (≤960px): Vertikal gestapelt, justify-content:flex-start, keine Leerraum-Probleme
- Mobile (≤600px): Kompakte Visual-Spalte, Features ausgeblendet
- Legal Links: Startseite · Impressum · Datenschutz · AGB
- Security by Obscurity: Kein "Admin", "Operator", "Agenten", "Interner Zugang" sichtbar
- Registration-Flow für unbekannte E-Mails (Angebotsanfragen)

### Mobile Menu Overlay — VERIFIZIERT (Iteration 27)
- position:absolute, height:calc(100dvh - var(--nav-h)), Background #0a0e14 (opak)
- Backdrop: rgba(0,0,0,0.85), z-index: 199/200
- Kein Content-Bleed-through, kein doppelter Language Switcher
- Alle Nav-Links + "Anmelden" + "Beratung starten"
- body.mobile-menu-open → nav z-index: 9999

### Floating Actions States — VERIFIZIERT (Iteration 27)
- body.mobile-menu-open → visibility:hidden für WA + Chat
- body.cookie-visible → bottom:120px
- Standard → bottom:24px
- Korrekte Transition, keine Kollisionen

### 3D-Szenen — VERIFIZIERT (Iteration 27)
- HeroScene: Wireframe-Ikosaeder, Orbits, Nodes, DataStreams, AccentGeometries
- IntegrationsGlobe: Wireframe-Kugel, Connection-Arcs, Nodes
- ProcessScene: 4 Hubs mit Orbiting-Ringen, FlowStreams

### Breakpoint-Verifizierung — VERIFIZIERT (Iteration 27)
- 1920px: Full navigation, 3D Hero, two-column login ✅
- 1440px: Footer komplett mit IBAN ✅
- 1024px: Anmelden + Beratung starten sichtbar ✅
- 768px: Tablet login vertikal gestapelt, 86px Gap ✅
- 390px: Mobile hero lesbar, login kompakt ✅
- 360px: Kein Overflow, Header 73px ✅

### Worker/Scheduler-Layer — VERIFIZIERT (Iteration 25)
### Kommunikationskern — VERIFIZIERT (Iteration 25)
### Outbound Lead Machine — VERIFIZIERT (Iteration 25)
### Billing Status-Sync — VERIFIZIERT (Iteration 25)
### LLM-Abstraktionsschicht — VERIFIZIERT (Iteration 25)
### Auth & Login — VERIFIZIERT (Iteration 26+27)
### Admin CRM — VERIFIZIERT
### Customer Portal — VERIFIZIERT

## Testing Status
- Iteration 25: 100% — 30/30 Backend
- Iteration 26: 100% — 11/11 Frontend
- Iteration 27: 100% — 16/16 Frontend (Design-Harmonisierung)

## Commercial Source of Truth
| Tarif | Kennung | Preis | Laufzeit | Anzahlung |
|-------|---------|-------|----------|-----------|
| Starter AI Agenten AG | NXA-SAA-24-499 | 499 EUR/Mo | 24 Mo | 30% = 3.592,80 EUR |
| Growth AI Agenten AG | NXA-GAA-24-1299 | 1.299 EUR/Mo | 24 Mo | 30% = 9.352,80 EUR |

## Remaining Tasks (Priorisiert)
1. Projektchat/Handover-Kontext härten
2. Contract Operating System v1 (Mastervertrag, Anlagen, digitale Signatur)
3. Revolut/Stripe Live-Webhooks
4. DeepSeek Live-Migration
5. Legal & Compliance Guardian operativ verdrahten
6. Outbound Lead Machine Produktionshärtung
7. server.py Refactoring (>4200 Zeilen → modulare Routen)
