# NeXifyAI Enterprise — API Reference
# =============================================================================
# Stand: 2026-05-22 16:42 UTC | Version: 1.0
# Gültig für alle internen und externen API-Endpunkte
# =============================================================================

## 1. Brain API v2 (Unified Enterprise Brain)
**Base URL:** `https://brain.nexifyai.cloud` (extern) / `http://localhost:8420` (intern)

### Status & Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| GET | `/stats` | Brain statistics (collections, points, categories) |

### Knowledge Retrieval
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search` | Semantic search across all collections |
| GET | `/collections` | List all Qdrant collections |
| GET | `/collections/{name}` | Collection details (points, dimensions) |
| POST | `/collections/{name}/search` | Search within specific collection |
| POST | `/collections/{name}/points` | Insert new knowledge point |

### Request Format: `/search`
```json
{
  "query": "string",
  "limit": 10,
  "collections": ["nexifyai_brain", "nexifyai_memories"],
  "filters": { "category": "governance", "tags": ["security"] }
}
```

### Response Format: `/search`
```json
{
  "results": [{
    "id": "uuid", "score": 0.95, "collection": "nexifyai_brain",
    "payload": {"category": "governance", "title": "Security Policy", "content": "..."}
  }],
  "total": 42, "took_ms": 15
}
```

---

## 2. OpenRouter AI Gateway
**Base URL:** `https://openrouter.ai` / `http://localhost:8420 (Brain API)`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check — `{"ok": true}` |
| GET | `/api/providers` | List AI providers |
| GET | `/api/models` | List available models |
| POST | `/api/chat/completions` | OpenAI-compatible chat |

### Auth
- Dashboard: `https://openrouter.ai` (pw in credentials.env)
- API keys: Per-provider in OpenRouter DB

---

## 3. Qdrant Vector Database
**Base URL:** `http://localhost:6333` (intern only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check |
| GET | `/collections` | List collections |
| GET | `/collections/{name}` | Collection info |
| POST | `/collections/{name}/points/search` | Semantic search |
| PUT | `/collections/{name}/points` | Upsert points |

### Collections
| Collection | Points | Dim |
|------------|--------|-----|
| nexifyai_brain | 12.997 | 4096 |
| nexifyai_memories | 5.852 | 4096 |
| company_brain | 13 | 4096 |
| hermes_knowledge | — | 4096 |
| decision_memory | — | 4096 |

---

## 4. Traefik Reverse Proxy
**Base URL:** `https://traefik.nexifyai.cloud` / `http://localhost:8080`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Dashboard (auth-protected) |
| GET | `/api/http/routers` | All routers |
| GET | `/api/http/services` | All services |
| GET | `/api/http/middlewares` | All middlewares |

---

## 5. GitHub Webhook Receiver
**Base URL:** `https://webhook.nexifyai.cloud` / `http://localhost:8011`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/github` | GitHub webhook (HMAC-validated) |
| GET | `/health` | Receiver health |


---

## 6. Customer Project APIs

| Project | Port | Health Endpoint |
|---------|------|----------------|
| Studienkolleg Aachen | 8010 | GET /api/health |
| Affilinet Portal | 8020 | GET /api/health |
| OpenCarBox | 8030 | GET /api/health |

---

## 7. Monitoring & Observability

| Service | URL | Port |
|---------|-----|------|
| Uptime Kuma | status.nexifyai.cloud | 3001 |
| Grafana | grafana.nexifyai.cloud | 3003 |
| MindsDB | mindsdb.nexifyai.cloud | 47334 |

---

## 8. Authentication

- **SERVICE_ROLE_KEY:** Centralized via `supabase_auth.py` gateway pattern
- **Never:** `os.getenv("SUPABASE_SERVICE_KEY")` directly
- **Import:** `from services.supabase_auth import supabase_select`
- **Credentials:** `/root/.secrets/credentials.env` (chmod 600)

---

## 9. Error Response Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Human-readable description",
    "timestamp": "2026-05-22T16:42:00Z",
    "request_id": "uuid"
  }
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |

---

## 10. Rate Limits
| Endpoint | Limit | Window |
|----------|-------|--------|
| Brain API | 100 req/s | Per IP |
| OpenRouter | Provider-dependent | Per key |
| Qdrant | Unlimited (internal) | — |
| Webhook | 5000 req/h | GitHub limit |

