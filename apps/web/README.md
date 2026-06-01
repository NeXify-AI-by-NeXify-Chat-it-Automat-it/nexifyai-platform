# NeXifyAI Website — nexifyai.cloud

> Next.js Enterprise Website — AI-Agentur-Portal mit Brain-Integration, Admin-Panel und Kundenportal.

Frontend der NeXifyAI Enterprise Plattform — Öffentliche Website + Admin-Dashboard + Kundenportal.

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
apps/web/
├── api/              # Serverless API-Routen (Vercel)
│   └── cron/         # Cron-Jobs (health, cleanup, monitoring)
├── public/           # Statische Assets
├── src/
│   ├── components/   # Wiederverwendbare Komponenten
│   │   ├── sections/ # Page-Sections
│   │   └── shared/   # Shared UI
│   ├── data/         # Statische Daten (blog, products, integrations)
│   ├── i18n/         # Übersetzungen (DE/EN)
│   ├── lib/          # Utilities (auth, supabase, tracking)
│   ├── pages/        # Seiten (admin, blog, booking, portal, etc.)
│   └── utils/        # Hilfsfunktionen
├── index.html
├── package.json
├── vercel.json
└── vite.config.js
```

## Entwicklung

```bash
# Dependencies installieren
cd apps/web && npm install

# Dev-Server starten (localhost:3000)
npm run dev

# Build
npm run build
# Output: apps/web/build/
```

## Build-Optimierung

- Manual Chunking: react, three.js, framer-motion, @unovis in separate Bundles
- Sourcemaps disabled (Production)
- Build: ~2s, 16 Chunks

## Seiten

| Route | Seite | Status |
|-------|-------|--------|
| `/` | Landing Page | ✅ |
| `/leistungen` | Services | ✅ |
| `/preise` | Pricing | ✅ |
| `/blog` | Blog-Übersicht | ✅ |
| `/blog/:slug` | Blog-Post | ✅ |
| `/kontakt` | Kontakt | ✅ |
| `/admin` | Admin-Dashboard | ✅ |
| `/customer-portal` | Kundenportal | ✅ |
| `/booking` | Booking | ✅ |
| `/unified-login` | Login | ✅ |
| `/quote` | Quote-Portal | ✅ |
| `/legal` | Impressum/Datenschutz | ✅ |
| `/admin-next` | Admin (next-gen) | 🚧 |

## Deployment

- Automatisch via Vercel (Push to `main`)
- Vercel Analytics + Speed Insights aktiv
- Build: `vite build` → Output `/build`
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
