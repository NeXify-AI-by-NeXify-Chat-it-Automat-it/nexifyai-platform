# Brain API – Full Endpoint Documentation

**Stand:** 2026-05-22
**Status:** Active (partial implementation)

## Base URL
| Environment | URL |
|-------------|-----|
| Production  | `http://127.0.0.1:8420` |
| External (via Cloudflare Tunnel) | `https://brain.nexifyai.cloud` |

## Authentication
All non‑public endpoints require **JWT Bearer** token signed with `HS256`.
Token secret (`JWT_SECRET`) lives in `/root/.secrets/credentials.env`.

### Obtain token (OpenRouter (direct) login)
```bash
curl -X POST https://openrouter.ai/api/v1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"<INITIAL_PASSWORD>"}'
```
Response contains `{ "token": "<jwt>" }`.
Use `Authorization: Bearer <jwt>` header for all protected calls.

## Endpoints
### 1. Health Check
```
GET /health
```
*Public – no auth*
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
### 2. System Status
```
GET /system/status
```
*Protected – JWT required*
Returns consolidated health of all dependent services.
```json
{
  "status": "healthy|degraded|down",
  "services": {
    "qdrant": {"status":"healthy","collections":6,"total_points":27989},
    "openrouter": {"status":"healthy"},
    "redis": {"status":"healthy"},
    "supabase": {"status":"degraded","error":"service_role key rejected"}
  },
  "uptime_seconds": 3600,
  "last_backup": "2026-05-22T12:00:00Z",
  "version": "3.1.0",
  "timestamp": "2026-05-22T16:42:00Z"
}
```
### 3. Agent – Single Task
```
POST /api/v2/agent/run
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "task": "<description>",
  "model": "ds/nexify-v4-pro"
}
```
Returns JSON with `task_id` and initial status.

### 4. Agent – Streaming
```
POST /api/v2/agent/stream
Content-Type: application/json
Authorization: Bearer <jwt>

{ "task": "<description>", "stream": true }
```
Server‑Sent Events stream incremental assistant messages.

### 5. Oracle – Lifecycle
```
POST /api/v2/oracle/run
Authorization: Bearer <jwt>

{ "task": "<description>", "mode": "plan|act" }
```
GET `/api/v2/oracle/{task_id}` to poll status.

### 6. RAG – Query
```
POST /api/v2/rag/query
Authorization: Bearer <jwt>

{ "query": "Frage", "collection": "nexifyai_brain", "k":5, "threshold":0.7 }
```
Returns `result` and source excerpts.

### 7. RAG – Conversational
```
POST /api/v2/rag/conversation
Authorization: Bearer <jwt>

{ "messages": [{"role":"user","content":"..."}], "collection":"nexifyai_brain" }
```
Streams responses via SSE.

### 8. AI Health
```
GET /api/v2/health/ai
```
```json
{
  "llm": {"available":true,"provider":"openrouter"},
  "qdrant": {"available":true,"collections":6},
  "embeddings": {"available":true,"model":"Qwen/Qwen3-Embedding-8B","dimension":4096}
}
```

## Error handling
All error responses follow schema:
```json
{ "error": { "code": <int>, "message": "..." } }
```
Typical HTTP codes: 400 (Bad request), 401 (Unauthorized), 404 (Not found), 502 (Upstream failure).

## Rate limiting & quotas
- Global limit: 120 requests/min per JWT.
- Burst limit: 10 req/s.
- Exceeding returns `429 Too Many Requests` with `Retry-After` header.

---
*Document updated to include missing `/system/status` spec and auth details.*