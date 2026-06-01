# NeXifyAI — Setup-Guide für alle Services

**Stand:** 2026-05-22
**Status:** Active

## Voraussetzungen

- Docker + Docker Compose v2
- Cloudflare Tunnel (token-basiert)
- Python 3.12 (für Admin-Proxy)
- Node.js 20 (für Admin-Frontend)

## Service-Übersicht

| Service | Port | Container | Compose |
|---------|------|-----------|--------|
| Traefik | 80,443,8080 | nx-traefik | sicher-repo/infrastructure/docker/ |
| Qdrant | 6333,6334 | nexifyai-qdrant | sicher-repo/infrastructure/docker/ |
| Redis Cache | 6379 | nx-redis-cache | sicher-repo/infrastructure/docker/ |
| Redis OpenRouter (direct) | 6380 | nx-redis-openrouter | openrouter/ |
| OpenRouter (direct) | 20128 | openrouter-5afd-niner-router-1 | /docker/openrouter-5afd/ |
| Admin Portal | 5173 | nexifyai-admin | /root/nexifyai-admin/ |
| Admin API Proxy | 8002 | nexifyai-admin-api | /root/nexifyai-admin/ |
| Uptime Kuma | 3001 | uptime-kuma | sicher-repo/ |
| Grafana | 3000 | grafana | sicher-repo/ |
| Loki | 3100 | loki | sicher-repo/ |
| Promtail | — | promtail | sicher-repo/ |
| MindsDB | 47334 | mindsdb | sicher-repo/ |
| MongoDB | 27017 | mongo | sicher-repo/ |
| Cloudflared | — | cloudflared | systemd |

## Quick-Start

### 1. Secrets einrichten

```bash
# secrets Datei erstellen
mkdir -p /root/.secrets
chmod 700 /root/.secrets
cat > /root/.secrets/credentials.env << 'EOF'
JWT_SECRET=<generieren-mit-openssl-rand-hex-32>
SUPABASE_ANON_KEY=eyJh...
SUPABASE_SERVICE_ROLE_KEY=eyJh...
VITE_AI_API_KEY=sk-...
INITIAL_PASSWORD=<sicheres-passwort>
API_KEY_SECRET=<generieren>
MACHINE_ID_SALT=<generieren>
NEXIFY_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-...
VERCEL_AI_GATEWAY_KEY=...
NEXIFY_API_KEY=...
EOF
chmod 600 /root/.secrets/credentials.env
source /root/.secrets/credentials.env
```

### 2. Infrastruktur starten

```bash
# Proxy-Netzwerk erstellen
docker network create proxy

# Basis-Infra (Qdrant, Redis, API)
cd /root/sicher-repo/infrastructure/docker
docker compose up -d
```

### 3. Traefik starten

```bash
cd /root/sicher-repo/infrastructure/docker
docker compose up -d nx-traefik
# Dashboard: http://127.0.0.1:8080
```

### 4. OpenRouter (direct) starten

```bash
cd /docker/openrouter-5afd
docker compose up -d
# Health: curl https://openrouter.ai/api/v1/api/health
```

### 5. Admin Portal starten

```bash
cd /root/nexifyai-admin
docker compose up -d
# Portal: http://127.0.0.1:5173
```

### 6. Monitoring starten

```bash
cd /root/sicher-repo
docker compose up -d grafana loki promtail uptime-kuma
```

### 7. Cloudflare Tunnel starten

```bash
systemctl start cloudflared
systemctl status cloudflared
# Verify: curl https://nexifyai.cloud/api/health
```

## Health-Checks

```bash
# Alle Services prüfen
/root/scripts/e2e-verify.sh 2>/dev/null || \
for s in qdrant:6333 openrouter:20128 admin:5173 traefik:8080 brain:8420; do
  svc=${s%%:*}; port=${s##*:}
  curl -s http://localhost:$port >/dev/null && echo "$svc: ✅" || echo "$svc: ❌"
done
```

## Service-spezifische Konfiguration

### Qdrant
- **Config:** environment in compose
- **Daten:** volume `qdrant_data`
- **Backup:** `/root/backups/qdrant-snapshot-*.tar.gz`

### OpenRouter (direct)
- **Config:** environment + `/app/data/db/data.sqlite`
- **Env:** JWT_SECRET, INITIAL_PASSWORD, API_KEY_SECRET, MACHINE_ID_SALT
- **Backup:** `/root/backups/openrouter-db-*.sqlite`

### Admin-API-Proxy
- **Code:** `/root/nexifyai-admin/api_proxy.py`
- **Deploy:** `docker compose restart admin-api-proxy`
- **Logs:** `docker logs nexifyai-admin-api`

### Traefik
- **Static config:** `traefik/traefik.yml`
- **Dynamic config:** `traefik/dynamic/`
- **Netzwerk:** externes Netzwerk `proxy`

## Backup-Strategie

```bash
# Tägliches Backup aller stateful Volumes
/root/scripts/backup-all.sh

# Manuell
# Qdrant snapshot
curl -X POST http://localhost:6333/collections/nexifyai_brain/snapshots
# OpenRouter (direct) DB
cp /docker/openrouter-5afd/data/db/data.sqlite /root/backups/openrouter-db-$(date +%Y%m%d).sqlite
# Secrets
cp /root/.secrets/credentials.env /root/backups/credentials-backup-$(date +%Y%m%d).env
```

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| OpenRouter (direct) 401 Unauthorized | `JWT_SECRET` nicht gesetzt | `source /root/.secrets/credentials.env` |
| Brain API 404 /system/status | Route nicht registriert | Siehe ADR-027, Service neustarten |
| Supabase invalid API key | Service-Role falsch | Supabase Dashboard → API Settings |
| Traefik 404 /api/overview | API deaktiviert | Traefik static config: `api: {dashboard: true}` |
| Qdrant unreachable | Container down | `docker restart nexifyai-qdrant` |
| Cloudflare Tunnel down | systemd status | `systemctl restart cloudflared` |
