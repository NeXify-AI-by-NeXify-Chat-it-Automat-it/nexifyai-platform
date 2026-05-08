# Plausible CE — Self-Hosted Setup

## Überblick
Plausible Community Edition (CE) ist die Open-Source-Version von Plausible Analytics.
DSGVO-konform, kein Cookie-Banner nötig, selbst gehostet auf dem VPS.

## Voraussetzungen
- Docker + Docker Compose auf VPS (✅ vorhanden)
- ClickHouse (~500MB RAM, 1GB Disk)
- PostgreSQL (kann Supabase-Stack mitnutzen) oder SQLite
- Subdomain: `analytics.nexifyai.cloud` via Traefik

## Installation

### 1. Verzeichnis und Config
```bash
ssh root@72.62.152.47
mkdir -p /opt/plausible

# SECRET_KEY_BASE generieren
SECRET=$(openssl rand -hex 48)
```

### 2. docker-compose.yml
Siehe `/opt/plausible/docker-compose.yml` auf dem VPS.

### 3. Traefik-Routing
Traefik-Route für `analytics.nexifyai.cloud` → `supabase-kong:8000`
Vorhandenes Label-System nutzen.

### 4. Start
```bash
cd /opt/plausible
docker compose up -d
```

## Datenbank
Plausible benötigt:
1. **ClickHouse** — Analytics-Speicher (Container-intern)
2. **PostgreSQL** — Metadaten, Sessions (Supabase DB oder eigenständig)

Die PostgreSQL-Datenbank `plausible` muss vor dem Start existieren:
```sql
CREATE DATABASE plausible;
```

## Konfiguration
- **URL:** `https://analytics.nexifyai.cloud`
- **Admin-Zugang:** Nach erstem Start via `/register` erstellen
- **Script:** `<script defer data-domain="nexify-automate.com" src="https://analytics.nexifyai.cloud/js/script.js"></script>`

## Integration in Frontend
Nach Installation: Plausible Script in `frontend/public/index.html` einbinden.
Events werden parallel zum Backend-Tracking (POST /api/analytics/track) gesendet.

## Verwandte Dokumente
- DOS v2.0 Kapitel 11: Event-Taxonomy
- frontend/src/lib/track.ts: Event-Tracking-Library
- /docs/system/dependency-map.md: Abhängigkeitsanalyse
