# NeXifyAI — Runtime Topology
**Version:** 1.0 | **Stand:** 2026-05-29
**Klassifikation:** INTERN
**Owner:** NeXifyAI (Lead Agent)

## Systemübersicht

```
Internet → Cloudflare Tunnel → Kong Gateway (8000) → Interne Services
                                ↓
                           Traefik (80/443) → Frontends
                                ↓
                      Brain API (:8420) 
                      Qdrant (:6333)
                      Redis (:6379)
                      Supabase (:5432)
```

## Service-Katalog

### Gateway Layer
| Service | Port | Status | Health | 
|---------|------|--------|--------|
| Kong API Gateway | 8000 (Proxy), 8001 (Admin) | ✅ docker-kong-1 | healthy |
| Traefik | 80, 443 | ✅ nx-traefik | healthy |
| Cloudflare Tunnel | 32769 | ✅ cloudflared.service | active |

### Brain Layer
| Service | Port | Status | Systemd |
|---------|------|--------|---------|
| Brain API v3 | 8420 | ✅ nexify-brain-api.service | active |
| Oracle Engine | 8001 | ✅ nexifyai-oracle-engine | healthy |
| Qdrant Core | 6333-6334 | ✅ qdrant-core | active |
| Brain Monitor | — | ✅ nexify-brain-monitor.service | active (60s loop) |
| Brain Chat Bridge | — | ✅ nexify-brain-chat-bridge.service | active |

### Datenbank Layer
| Service | Port | Status |
|---------|------|--------|
| Supabase DB | 5432 | ✅ docker-db-1 |
| Supabase Auth | — | ✅ docker-auth-1 |
| Supabase REST | 3000 | ✅ docker-rest-1 |
| Supabase Studio | 3000 | ✅ docker-studio-1 |
| Redis Cache | 6379 | ✅ nx-redis-cache |

### AI / Runtime Layer
| Service | Port | Status | Systemd |
|---------|------|--------|---------|
| 9Router | — | ❌ entfernt (OpenRouter aktiv) | deprecated 2026-05-29 |
| Orchestrator | — | ✅ nexify-orchestrator.service | active |
| Planner | — | ✅ nexify-planner.service | active |
| Event Bus | — | ✅ nexify-eventbus.service | active |
| MCP Runtime | — | ✅ nexify-mcp-runtime.service | active |
| Systemmaster | — | ✅ nexify-systemmaster.service | active |
| Watchdog | — | ✅ nexify-watchdog.service | active |
| Recovery | — | ✅ nexify-recovery.service | active |
| Governance | — | ✅ nexify-governance.service | active |
| CEO Autopilot | — | ✅ nexifyai-ceo-autopilot.service | active |
| Workers (4) | — | ✅ nexify-workers + analysis + engineering + main | active |

### Monitoring Layer
| Service | Port | Status |
|---------|------|--------|
| Prometheus | 9090 | ✅ prometheus |
| Grafana | 3000 | ✅ grafana (307 redirect) |
| Loki | 3100 | ✅ loki |
| Promtail | — | ✅ promtail |
| Alertmanager | 9093 | ✅ alertmanager |
| Uptime Kuma | — | ✅ uptime-kuma |
| OTEL Collector | — | ✅ nexify-otel-collector |

### Frontend Layer
| Service | Port | Status |
|---------|------|--------|
| NeXify Frontend | 80 | ✅ nx-frontend |
| NeXify Admin | 80 | ✅ nexifyai-admin |
| Admin API | 8002 | ✅ nexifyai-admin-api |

## Abhängigkeitsgraph

```
Brain API ← Qdrant, Redis
Oracle Engine ← Brain API, Qdrant
Supabase (alle) ← DB (PostgreSQL)
Kong → Brain API, Oracle Engine
Traefik → Frontend, Admin
CEO Autopilot → Oracle Engine, Brain API, Workers
Workers → Brain API, Qdrant, Supabase
Watchdog → alle Services (Health-Check)
```

## Netzwerk-Topologie

- **Interne Kommunikation:** Docker Bridge Network (172.x.x.x)
- **Externer Zugriff:** Cloudflare Tunnel → Kong → intern
- **Qdrant:** localhost:6333 (gebunden an 0.0.0.0)
- **Redis:** localhost:6379
- **Supabase DB:** localhost:5432

## Recovery-Strategie

| Szenario | Aktion | Systemd-Unit |
|----------|--------|-------------|
| Brain API down | nexify-brain-monitor restartet automatisch | nexify-brain-monitor.service |
| Backend down | systemctl restart nexifyai-backend | nexifyai-backend.service |
| Qdrant down | docker restart qdrant-core | — |
| Kong down | docker restart docker-kong-1 | — |

## Observability

- **Metriken:** Prometheus (node, otel-collector, alertmanager, loki)
- **Logs:** Loki + Promtail (/var/log/nexifyai-*.log)
- **Alerts:** Alertmanager → Alert-Webhook → Uptime Kuma
- **Health:** Brain API /health + nexify-brain-monitor (60s Loop)