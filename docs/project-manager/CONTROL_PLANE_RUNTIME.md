# Control Plane Runtime

## Services

| Service | Port | Status | Beschreibung |
|:--------|:-----|:-------|:-------------|
| `nexify-project-manager-api.service` | 8421 | ✅ Active | Task Queue, Policy Gate, Evidence, Skill Registry |
| `nexify-brain-api.service` | 8420 | ✅ Active | Qdrant Vector Store, Embeddings, Retrieval |
| `nexify-goose-worker.timer` | — | ✅ Active | Pollt alle 30s GET /tasks/next |
| `nexify-goose-worker.service` | — | ✅ Active (oneshot) | Führt Task aus, sendet Callback |
| `goose-acp-server.service` | 3284 | ✅ Active | Goose ACP Server (HTTP/WS) |
| `nexify-embedding-health.service` | — | ✅ Active | Embedding Health Monitor |

## Task Flow

```
POST /tasks (API)
→ TaskRecord(status=queued) in Registry
→ Worker pollt GET /tasks/next
→ POST /tasks/{id}/run (status=running)
→ Brain-Kontext laden
→ Goose run mit Task-Prompt
→ Evidence speichern
→ POST /worker/callback (status=completed/failed)
→ Brain Update
```

## Healthchecks

```bash
# PM API
curl http://127.0.0.1:8421/health

# Brain
curl http://127.0.0.1:8420/health

# Qdrant
curl http://127.0.0.1:6333/healthz

# Goose ACP
curl http://127.0.0.1:3284/health

# 9Router (AI Router)
curl http://localhost:20128/v1/models
```
