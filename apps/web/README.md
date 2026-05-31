# NeXifyAI Landing Page

Frontend der NeXifyAI Enterprise Plattform — Öffentliche Website + Admin-Dashboard + Kundenportal.

## Tech Stack

| Komponente | Technologie |
|------------|-------------|
| Framework | React 19 + Vite |
| Routing | react-router-dom v7 |
| 3D | react-three-fiber / drei / three.js |
| Animation | framer-motion |
| Styling | CSS (kein Tailwind) |
| i18n | Eigenes Context-basiertes System (DE/EN) |
| Analytics | @vercel/analytics + Speed Insights |
| Backend | Supabase (Auth, DB) |
| Deployment | Vercel (vercel.json konfiguriert) |

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
