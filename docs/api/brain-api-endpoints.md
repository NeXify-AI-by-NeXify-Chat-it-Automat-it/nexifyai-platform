# Brain API — Endpoint-Dokumentation

**Stand:** 2026-05-22
**Status:** Active (partial: einige Endpoints noch in Entwicklung)

## Basis-URL

| Umgebung | URL |
|----------|-----|
| Production | `http://127.0.0.1:8420` |
| Extern (via Tunnel) | `https://brain.nexifyai.cloud` |

## Endpoints

### 1. Health-Check

```
GET /health
```

Prüft ob der Service läuft.

**Response 200:**
```json
{
  "status": "ok",
  "service": "brain-api",
  "timestamp": "2026-05-22T16:42:00Z"
}
```

### 2. System-Status

```
GET /system/status
```

**Status:** 🟡 Noch nicht implementiert (404) — geplant für Brain API v3.2.

**Geplanter Endpoint:**
Der Endpoint `/system/status` ist Teil der Roadmap und soll einen umfassenden Überblick
über den Zustand aller angebundenen Dienste liefern.

**Geplante Antwort:**
```json
{
  "status": "healthy|degraded|down",
  "services": {
    "qdrant": {"status": "healthy", "collections": 6, "total_points": 27989},
    "openrouter": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "supabase": {"status": "degraded", "error": "service_role key rejected"}
  },
  "uptime_seconds": 3600,
  "last_backup": "2026-05-22T12:00:00Z",
  "version": "3.1.0",
  "timestamp": "2026-05-22T16:42:00Z"
}
```

**Aktuelle Alternative:**
Derzeit liefert `GET /` (Root) eine vollständige Service-Übersicht:
```json
{
  "service": "Nexify Brain API v3 — Unified",
  "version": "3.1.0",
  "qdrant": "http://127.0.0.1:6333",
  "embeddings": "https://openrouter.ai/api/v1 (nexify/Qwen/Qwen3-Embedding-8B)",
  "collections": ["nexifyai_brain", "nexifyai_memories"],
  "endpoints": {
    "health": "GET /health",
    "stats": "GET /stats",
    "categories": "GET /categories (scroll-basiert)",
    "query": "POST /query (vector search with fallback)",
    "store": "POST /store (with embeddings + retry)",
    "delete": "DELETE /delete/{id}",
    "reindex": "POST /reindex (fix zero-vector points)"
  },
  "features": [
    "Retry-Logik (3 Versuche, exponentielles Backoff)",
    "Connection-Pool (20 max, 5 keepalive)",
    "Input-Validierung (Content/Query-Limits)",
    "Request-ID Tracing",
    "Graceful Shutdown (FastAPI Lifespan)"
  ]
}
```

**Health-Endpoint (bereits live):**
```
GET /health
```
```json
{
  "status": "ok",
  "qdrant": true,
  "openrouter": true,
  "embedding_model": "nexify/Qwen/Qwen3-Embedding-8B",
  "collections": 6,
  "total_points": 27989,
  "timestamp": "2026-05-22T20:39:46Z"
}
```

### 3. Agent Endpoints

#### Single-Task Agent
```
POST /api/v2/agent/run
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "task": "<task-description>",
  "model": "ds/nexify-v4-pro"
}
```

#### Streaming Agent
```
POST /api/v2/agent/stream
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "task": "<task-description>",
  "stream": true
}

→ Server-Sent Events
```

### 4. Oracle Endpoints

#### Oracle Lifecycle starten
```
POST /api/v2/oracle/run
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "task": "<task-description>",
  "mode": "plan|act"
}
```

#### Task-Status abfragen
```
GET /api/v2/oracle/{task_id}
Authorization: Bearer <jwt-token>

Response: {
  "task_id": "uuid",
  "status": "running|completed|failed",
  "result": {...},
  "started": "...",
  "completed": "..."
}
```

### 5. RAG Endpoints

#### RAG Query
```
POST /api/v2/rag/query
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "query": "Was ist der Zeitplan?",
  "collection": "nexifyai_brain",
  "k": 5,
  "threshold": 0.7
}

Response: {
  "result": "...",
  "sources": [
    {"id": "...", "text": "...", "score": 0.92}
  ]
}
```

#### Conversational RAG
```
POST /api/v2/rag/conversation
```

### 6. Health (AI-spezifisch)

```
GET /api/v2/health/ai

Response: {
  "llm": {"available": true, "provider": "openrouter"},
  "qdrant": {"available": true, "collections": 6},
  "embeddings": {"available": true, "model": "Qwen/Qwen3-Embedding-8B", "dimension": 4096}
}
```

## Auth

| Endpoint | Auth | Auth-Methode |
|----------|------|-------------|
| `/health` | ❌ | Keine |
| `/system/status` | ⚠️ | JWT (geplant) |
| `/api/v2/*` | ✅ | JWT Bearer |

## Service-Architektur

```
┌─────────────────────┐
│   Brain API Server   │
│   (0.0.0.0:8420)    │
├─────────────────────┤
│ FastAPI + LangChain  │
│ + LangGraph          │
├─────────────────────┤
│ Services:            │
│ • Qdrant (RAG)      │
│ • OpenRouter (direct) (LLM)     │
│ • Redis (Cache)    │
│ • Supabase (Auth)  │
└─────────────────────┘
```
