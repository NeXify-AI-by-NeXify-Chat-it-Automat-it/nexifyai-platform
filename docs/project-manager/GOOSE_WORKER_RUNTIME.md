# Goose Worker Runtime

## Service-Definition

**Service**: `nexify-goose-worker.service` (oneshot)
**Timer**: `nexify-goose-worker.timer` (alle 30s)
**Script**: `/opt/nexify/goose-runtime/bin/nexify-goose-worker.sh`

## Flow

1. Timer triggert alle 30s
2. Worker pollt `GET /tasks/next` von PM API
3. Wenn Task: claimen → Brain-Kontext laden → Goose run → callback → Brain Update
4. Wenn kein Task: exit 0 (graceful)

## Task-Driven Operation (Bewiesen)

- ✅ `POST /tasks` (PM API) → Task queued
- ✅ `GET /tasks/next` (Worker) → Task returned
- ✅ `POST /tasks/{id}/run` → Status running
- ✅ Goose run mit Task-Prompt → Evidence
- ✅ POST /worker/callback → Status completed/failed
- ✅ Brain Update

## Evidence

```bash
# Worker logs
journalctl -u nexify-goose-worker.service -n 50 --no-pager

# Timer status
systemctl status nexify-goose-worker.timer --no-pager

# Tasks in queue
curl http://127.0.0.1:8421/tasks

# Next queued task
curl http://127.0.0.1:8421/tasks/next
```

## Legacy

`nexify-goose-loop.service`: Deaktiviert. War ein statischer Prompt-Runner ohne Task-Queue-Integration.
