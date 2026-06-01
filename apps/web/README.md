# NeXifyAI Website — nexifyai.cloud

> Next.js Enterprise Website — AI-Agentur-Portal mit Brain-Integration, Admin-Panel und Kundenportal.

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Framework | React 18 + Vite |
| Styling | CSS Modules (App.css, Admin.css, etc.) |
| I18n | Custom Context-basiert (DE/EN) |
| SEO | SEOHead-Komponente + sitemap.xml + robots.txt |
| Backend-API | Supabase + Brain API (http://127.0.0.1:8420) |
| E2E-Tests | Playwright (WCAG, Security-UX) |
| Deploy | Vercel (vercel.json) |

## Struktur

```
public/             # Statische Assets (Bilder, Icons, sitemap.xml)
src/
  components/       # Wiederverwendbare UI-Komponenten
    sections/       # Seitenabschnitte
    shared/         # Geteilte Komponenten (CookieBanner, SEOHead, LanguageSwitcher, Scene3D)
  data/             # Statische Daten (Produkte, Blog, Integrationen)
  i18n/             # Mehrsprachigkeit (DE: Standard, EN: Fallback)
  lib/              # API-Clients (adminApi, supabase, tracking)
  pages/            # Seiten-Komponenten
    admin/          # Admin-Bereich
    admin-next/     # Nächste Admin-Generation
  utils/            # Hilfsfunktionen (auth)
api/cron/           # Serverlose Cron-Jobs
e2e/                # Playwright E2E-Tests
```

## Seiten

| Route | Komponente | Beschreibung |
|-------|-----------|-------------|
| `/` | index.html | Landing Page |
| `/admin` | Admin.jsx | Admin-Dashboard |
| `/blog` | BlogPage.jsx | Blog-Übersicht |
| `/blog/:slug` | BlogPostPage.jsx | Blog-Artikel |
| `/booking` | BookingPage.jsx | Buchungsseite |
| `/customer-portal` | CustomerPortal.jsx | Kundenportal |
| `/integration/:key` | IntegrationDetail.jsx | Integrationsdetails |
| `/kontakt` | KontaktPage.jsx | Kontaktseite |
| `/leistungen` | LeistungenPage.jsx | Dienstleistungen |
| `/oracle` | OracleView.jsx | Oracle-Übersicht |
| `/preise` | PreisePage.jsx | Preisseite |
| `/legal/:page` | LegalPages.jsx | Impressum/Datenschutz |

## I18n

Standard-Sprache: DE. Fallback: EN.
Übersetzungen in `src/i18n/translations.js`.
Sprachumschaltung via `LanguageSwitcher.jsx`.

## Brain-Integration

- **Store**: Entscheidungen, Konfiguration, Kundendaten
- **Search**: Kontextabfrage vor jeder Aktion
- **Sync**: AgentMemory ↔ Qdrant (alle 15 Min)

## Monitoring

- Playwright E2E-Tests in `e2e/` (WCAG, Security/UX)
- Cron-Jobs in `api/cron/` (Health, Cleanup, Competitor)
- Vercel Logs + Brain Healthchecks

## Entwicklung

```bash
npm install        # Dependencies
npm run dev        # Dev-Server (Vite)
npm run build      # Production-Build
npx playwright test # E2E-Tests
```

## Deployment

Automatisch via Vercel bei Push zu `main`.  
`vercel.json` enthält Rewrites für SPA-Routing.
