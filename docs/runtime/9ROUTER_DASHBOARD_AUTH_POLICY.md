# OpenRouter Dashboard Auth Policy

## Aktuelle Konfiguration

| Aspekt | Wert |
|--------|------|
| Dashboard-Port | 20128 (gleicher Port wie API) |
| Dashboard-Typ | NeXify AI Chat (Next.js) |
| Auth-Speicher | Docker Volume `OpenRouter-5afd_data` → `/app/data/auth/cli-secret` |
| Secret-Name | `OpenRouter_DASHBOARD_PASSWORD` |

## Wichtige Regel

**`INITIAL_PASSWORD` darf NICHT in der Docker-Env gesetzt sein.** 
Wenn gesetzt, überschreibt der Container-Entrypoint bei jedem Start das persistierte Auth.

## Auth-Reset (nur bei Bedarf)

1. Container stoppen: `docker stop OpenRouter-5afd-openrouter-1`
2. Volume-Pfad: `/var/lib/docker/volumes/OpenRouter-5afd_data/_data/auth/`
3. Datei `cli-secret` löschen
4. Container starten: `docker start OpenRouter-5afd-openrouter-1`
5. Dashboard fordert Neu-Registrierung auf

## Secret Registry

| Secret-Name | Storage | Scope | Owner |
|-------------|---------|-------|-------|
| `OpenRouter_DASHBOARD_PASSWORD` | Docker Volume (auth/cli-secret) | Container | pascal |
| `API_KEY_SECRET` | Docker Env | Container | pascal |
| `JWT_SECRET` | Docker Env | Container | pascal |
| `REDIS_PASSWORD` | `/opt/OpenRouter/event_layer.py` | Controller (Python) | pascal |
| `CAMBO_AUTH_CREDENTIALS` | `/opt/OpenRouter/config/services.yaml` | Provider-Login | pascal |
