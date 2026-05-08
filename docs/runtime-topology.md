# NeXifyAI — Runtime Topology (E1.1 Inventory)
**Datum:** 2026-05-08 | **Observer:** Hermes Container → VPS via SSH
**Prinzip:** Canonical State ≠ Observed State. Jeder Observer hat eigene Sicht.

---

## 1. TOPOLOGY MAP

```
                         ┌─────────────────────────────────────────────┐
                         │              VPS HOST (72.62.152.47)        │
                         │              Hostname: mail.nexifyai.cloud  │
                         │              OS: Ubuntu 24.04               │
                         └──────────────────┬──────────────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
           ┌────────▼────────┐   ┌─────────▼─────────┐   ┌────────▼────────┐
           │  SYSTEMD (host) │   │  DOCKER (bridge)  │   │ DOCKER NETWORKS │
           │                 │   │  172.17.0.0/16    │   │  (13 isolated)  │
           │ backend :8001   │   │                    │   │                 │
           │ admin-bot       │   │ qdrant      :6333  │   │ supabase_default│
           │ email-bot       │   │ landing     :52920 │   │ honcho-network  │
           │ github-bot      │   │                    │   │ qdrant-vjfp     │
           │ whatsapp-bot    │   │ ⚠️ 127.0.0.1 ONLY  │   │ openmemory      │
           │ support-bot     │   │ (host-local, NOT   │   │ mem0-integrated │
           │ chat-webhook    │   │  container-visibl) │   │ notebook_default│
           └─────────────────┘   └────────────────────┘   └─────────────────┘
```

---

## 2. SERVICE INVENTORY (mit Observer-Perspektiven)

### 2.1 Backend (FastAPI)
| Attribut | Wert |
|----------|------|
| **Canonical State Source** | `systemctl status nexifyai-backend` |
| **Runtime** | systemd (NICHT Docker) |
| **Host Port** | 8001 (systemd, auf Host) |
| **Docker Network** | KEIN (systemd = host-nativ) |
| **Observer: VPS-Host** | ✅ `curl localhost:8001/api/health/v2` |
| **Observer: Hermes-Container** | ❌ `localhost:8001` → unerreichbar (Container-Netzwerk isoliert) |
| **Observer: Extern (Internet)** | ✅ `https://nexify-automate.com/api` via Traefik |
| **Recovery Path** | `systemctl restart nexifyai-backend` |
| **Validation Method** | `curl -sf http://localhost:8001/api/health/v2` |

### 2.2 Qdrant (Vector Database) — ZWEI Instanzen

#### Instanz A: `nexifyai-qdrant` (Host-local, PRIMARY)
| Attribut | Wert |
|----------|------|
| **Canonical State Source** | `docker ps --filter name=nexifyai-qdrant` |
| **Image** | `qdrant/qdrant:v1.17.1` |
| **Docker Network** | `bridge` (172.17.0.2) + `supabase_default` |
| **Port Mapping** | `127.0.0.1:6333-6334→6333-6334` ⚠️ **HOST-LOCAL ONLY** |
| **Observer: VPS-Host** | ✅ `curl localhost:6333/collections` |
| **Observer: Hermes-Container** | ❌ `localhost:6333` → connection_refused (verschiedene Netzwerke) |
| **Observer: Extern** | ❌ Kein externer Port |
| **Recovery Path** | `docker restart nexifyai-qdrant` |
| **Validation** | `curl -sf http://localhost:6333/collections` → 2 Collections |

#### Instanz B: `qdrant-vjfp-qdrant-1` (External-reachable)
| Attribut | Wert |
|----------|------|
| **Image** | custom |
| **Docker Network** | `qdrant-vjfp_default` |
| **Port Mapping** | `0.0.0.0:32769→6333/tcp` (extern erreichbar!) |
| **Observer: VPS-Host** | ✅ `curl localhost:32769/collections` |
| **Observer: Hermes-Container** | ✅ `curl qdrant-vjfp-qdrant-1:6333` (gleiches Netzwerk) |
| **Observer: Extern** | ✅ `curl 72.62.152.47:32769/collections` |
| **Recovery Path** | `docker restart qdrant-vjfp-qdrant-1` |

### 2.3 Redis (Cache/Queue)
| Attribut | Wert |
|----------|------|
| **Canonical State Source** | `docker ps --filter name=honcho-redis` |
| **Image** | `redis:7-alpine` |
| **Docker Network** | NUR `honcho_honcho-network` |
| **Port Mapping** | ⚠️ **KEIN Port-Mapping zum Host!** (6379/tcp, kein -p) |
| **Observer: VPS-Host** | ❌ `redis-cli -h localhost` → connection_refused |
| **Observer: Hermes-Container** | ✅ `redis-cli -h honcho-redis-1` (gleiches honcho-Netzwerk) |
| **Observer: Extern** | ❌ Kein externer Port |
| **Recovery Path** | `docker restart honcho-redis-1` |
| **Validation** | `docker exec honcho-redis-1 redis-cli PING` → PONG |

### 2.4 Supabase Stack (14 Container)
| Container | Netzwerk | Host-Port | Observer-Host | Observer-Hermes |
|-----------|----------|-----------|---------------|-----------------|
| supabase-db | supabase_default | 5432 (intern) | ✅ docker exec | ✅ supabase-db:5432 |
| supabase-pooler | supabase_default | `0.0.0.0:6543` + `0.0.0.0:5433` | ✅ localhost:6543 | ❌ (anderes Netzwerk) |
| supabase-auth | supabase_default | — | ✅ intern | ✅ supabase-auth:9999 |
| supabase-rest | supabase_default | — | ✅ intern | ✅ supabase-rest:3000 |
| supabase-studio | supabase_default | `127.0.0.1:8300` | ✅ localhost:8300 | ❌ |
| supabase-kong | supabase_default | `0.0.0.0:8002` + `0.0.0.0:8442` | ✅ localhost:8002 | ❌ |
| supabase-edge-functions | supabase_default | — | ✅ intern | ✅ |
| supabase-realtime | supabase_default | — | ✅ intern | ✅ |
| supabase-storage | supabase_default | — | ✅ intern | ✅ |
| supabase-imgproxy | supabase_default | — | ✅ intern | ✅ |
| supabase-meta | supabase_default | — | ✅ intern | ✅ |
| supabase-vector | supabase_default | — | ✅ intern | ✅ |
| supabase-analytics | supabase_default | — | ✅ intern | ✅ |
| supabase-db-proxy | supabase_default | `127.0.0.1:5435` | ✅ localhost:5435 | ❌ |

### 2.5 Open Notebook (2 Instanzen)
| Instanz | Netzwerk | Host-Port | Status |
|---------|----------|-----------|--------|
| `notebook-open_notebook-1` | notebook_default | `0.0.0.0:32770→8502` | ✅ |
| `open-notebook-y3ih-open_notebook-1` | open-notebook-y3ih_default | `0.0.0.0:32768→8502` | ✅ |

### 2.6 Weitere Dienste
| Dienst | Netzwerk | Host-Port | Observer-Host | Observer-Hermes |
|--------|----------|-----------|---------------|-----------------|
| Paperclip | paperclip-etdf + mem0 | `0.0.0.0:47967→3100` | ✅ localhost:47967 | ✅ |
| Hermes Agent | 6 Netzwerke | — | ✅ (gleicher Host) | — (das bin ich) |
| Traefik | host | 80/443 (host) | ✅ | ✅ (host network) |
| Honcho API | honcho + supabase | `127.0.0.1:8003` | ✅ localhost:8003 | ✅ |
| Honcho DB | honcho | 5432 (intern) | ✅ docker exec | ✅ |
| Landing (nginx) | bridge | `0.0.0.0:52920→80` | ✅ localhost:52920 | ❌ |
| Umami Analytics | umami_default | `127.0.0.1:8088` | ✅ localhost:8088 | ❌ |

---

## 3. NETZWERK-ISOLATIONS-MATRIX

Wer kann wen erreichen?

| Observer → | Backend | Qdrant (host) | Qdrant (vjfp) | Redis | Supabase | Notebook |
|------------|---------|---------------|----------------|-------|----------|----------|
| **VPS-Host** | ✅ :8001 | ✅ :6333 | ✅ :32769 | ❌ | ✅ :6543 | ✅ :32770 |
| **Hermes-Container** | ❌ | ❌ | ✅ :6333 | ✅ | ✅ | ✅ |
| **Extern (Internet)** | ✅ via Traefik | ❌ | ✅ :32769 | ❌ | ✅ :6543 | ✅ :32770 |

---

## 4. CRITICAL FINDINGS (Drift-Signale)

| Finding | Impact | Recovery |
|---------|--------|----------|
| **Qdrant host-local:6333** nicht vom Container erreichbar | Health v2 meldet `qdrant: down` obwohl Service läuft | Endpoint auf `qdrant-vjfp-qdrant-1:6333` ändern ODER `--add-host` |
| **Redis ohne Host-Port-Mapping** | Nur innerhalb `honcho_honcho-network` nutzbar | `docker run -p 6379:6379` ODER Container in honcho-Netzwerk |
| **Backend systemd (nicht Docker)** | Container kann `localhost:8001` nicht erreichen | `host.docker.internal:8001` ODER `--network host` |
| **nexifyai-qdrant auf 127.0.0.1** | Host-local binding = nicht von Docker-Netzwerk erreichbar | Auf `0.0.0.0:6333` ändern |
| **ZWEI Qdrant-Instanzen** | Welche ist Source of Truth? | `nexifyai-qdrant` als Primary deklarieren (enthält Collections) |

---

## 5. RECOVERY-PFADE (pro Dienst)

| Dienst | Canonical Check | Recovery-Befehl |
|--------|-----------------|-----------------|
| Backend | `systemctl is-active nexifyai-backend` | `systemctl restart nexifyai-backend` |
| Qdrant (host) | `curl -sf localhost:6333/collections` | `docker restart nexifyai-qdrant` |
| Qdrant (vjfp) | `curl -sf localhost:32769/collections` | `docker restart qdrant-vjfp-qdrant-1` |
| Redis | `docker exec honcho-redis-1 redis-cli PING` | `docker restart honcho-redis-1` |
| Supabase | `docker exec supabase-db pg_isready` | `docker restart supabase-db` |
| Paperclip | `curl -sf localhost:47967` | `docker restart paperclip-etdf-paperclip-1` |
| Notebook | `curl -sf localhost:32770/api/sources` | `docker restart notebook-open_notebook-1` |
| Traefik | `docker ps --filter name=traefik` | `docker restart traefik-tcja-traefik-1` |
| Hermes | `docker ps --filter name=hermes-agent` | `docker restart hermes-agent-ofbh-hermes-agent-1` |
