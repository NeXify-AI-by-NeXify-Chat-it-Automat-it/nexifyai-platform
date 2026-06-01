# NeXifyAI Services – Setup & Deployment Guide

**Stand:** 2026-05-22
**OS:** Ubuntu 24.04
**Orchestration:** Docker Compose + systemd

## Prerequisites
- Host with `docker` ≥ 24, `docker compose` V2.
- `/root/.secrets/credentials.env` populated (see [Secret Management](/docs/adrs/ADR-024-secrets-vault.md)).
- Cloudflare Tunnel token (for external access).

## Service Inventory

| Service | Port | Compose file | Auth | External? |
|---------|------|-------------|------|-----------|
| OpenRouter (direct) | 127.0.0.1:20128 | `/docker/openrouter-5afd/docker-compose.yml` | JWT | ai-router.nexifyai.cloud |
| Qdrant | 127.0.0.1:6333 | `/root/sicher-repo/infrastructure/docker/docker-compose.yml` | — | ❌ |
| Redis (openrouter) | 6379 | bundled with openrouter | — | ❌ |
| Redis (cache) | 6380 | `/root/sicher-repo/infrastructure/docker/docker-compose.yml` | — | ❌ |
| Traefik | 80, 443, 8080 | `/docker/traefik/` | Basic-Auth (dash) | *.nexifyai.cloud |
| Admin Portal | 80 (internal) | `/root/nexifyai-admin/docker-compose.yml` | API‑Key | ❌ |
| Admin API Proxy | 8002 | `/root/nexifyai-admin/docker-compose.yml` | API‑Key | ❌ |
| Brain API | 8420 | Hermes Brain container | JWT + API‑Key | brain.nexifyai.cloud |
| Landing Page | 8081 | systemd or compose | — | nexifyai.cloud |
| Uptime Kuma | 3001 | compose | Basic‑Auth | ❌ |
| Grafana | 3000 | compose | Basic‑Auth | ❌ |
| Loki | 3100 | compose | — | ❌ |
| Cloudflare Tunnel | — | systemd (`cloudflared.service`) | Token | *exposes above* |

## Step‑by‑Step Startup

### 1. Secrets (mandatory)
```bash
source /root/.secrets/credentials.env
```
Missing secrets → many services silently fail.

### 2. Core Infrastructure
```bash
docker compose -f /root/sicher-repo/infrastructure/docker/docker-compose.yml up -d
```
Starts Qdrant, Redis cache, API service.

### 3. OpenRouter (direct)
```bash
cd /docker/openrouter-5afd
docker compose up -d
```
Verify: `curl https://openrouter.ai/api/v1/api/health` → `{"ok":true}`

### 4. Traefik
```bash
cd /docker/traefik
docker compose up -d
```
Dashboard at `https://traefik.nexifyai.cloud` (Basic‑Auth).

### 5. Admin Portal + API Proxy
```bash
cd /root/nexifyai-admin
docker compose up -d
```

### 6. Brain API (Hermes container)
```bash
docker compose -f /root/goose-isolated/docker-compose.yml up -d brain
```

### 7. Observability Stack
```bash
# Grafana, Loki, Promtail, Uptime-Kuma
docker compose -f /root/observability/docker-compose.yml up -d
```

### 8. Cloudflare Tunnel
```bash
systemctl enable --now cloudflared
```
Check: `systemctl status cloudflared`

## Health Verification
```bash
# Quick smoke test
curl -s http://localhost:8002/api/v1/health
curl -s http://localhost:8420/health
curl -s https://openrouter.ai/api/v1/api/health
curl -s http://localhost:6333/collections
```

Full automated health: `/root/scripts/e2e-verify.sh` (planned).

## Common Issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| OpenRouter (direct) `/api/providers` → 401 | JWT not configured | Set `JWT_SECRET` in credentials.env, restart container |
| Brain `/system/status` → 404 | Route not implemented yet | See ADR-027 |
| Supabase service_role rejected | Misconfigured RLS or key expired | Re‑generate API keys in Supabase dashboard |
| Traefik dashboard reachable without auth | `20-dashboard.yml` not loaded | Check dynamic config mount, restart Traefik |
| Admin API proxy can't reach Qdrant | Wrong internal IP (172.31.0.x) | Check Docker network attachment |

## Shutdown (graceful)
```bash
systemctl stop cloudflared
docker compose -f /docker/openrouter-5afd/docker-compose.yml down
docker compose -f /root/sicher-repo/infrastructure/docker/docker-compose.yml down
docker compose -f /root/nexifyai-admin/docker-compose.yml down
docker compose -f /root/observability/docker-compose.yml down
```

---
*Generated as part of documentation swarm – keep in sync with runtime topology.*