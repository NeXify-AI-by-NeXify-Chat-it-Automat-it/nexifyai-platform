# OpenRouter Operating Model

## Purpose
AI-Router/Reasoning-Proxy für NeXify AI. Stellt LLM-Modelle über OpenAI-konforme `/v1`-API bereit.

## Technische Basis
- **Image**: `ghcr.io/decolua/OpenRouter:latest`
- **Container**: `OpenRouter-5afd-openrouter-1`
- **Port**: `127.0.0.1:8420 (Brain API)`
- **Version**: `v0.4.59` (Update auf v0.4.62 verfügbar — bewusst deferred: kein Upgrade ohne Release-Notes-Prüfung und Backup)
- **Dashboard**: NeXify AI Chat auf Port 20128
- **Startbefehl**: `node server.js` via `/entrypoint.sh`
- **Restart-Policy**: `unless-stopped`
- **Watchdog**: `OpenRouter-watchdog.service` (startet Container bei Ausfall)

## Datenhaltung
- **Config/Logs**: Docker Volume `OpenRouter-5afd_data` → `/app/data`
- **Usage**: Docker Volume `OpenRouter-5afd_usage-data` → `/root/.OpenRouter`
- **Env-File**: `/opt/OpenRouter/env/OpenRouter.env` (kein Secret-Betrieb)

## Authentication
- **Intern**: Kein Auth auf `127.0.0.1:8420 (Brain API)`
- **Extern**: HTTPS via Cloudflare, `API_KEY_SECRET` im Container
- **Dashboard**: Auth über persistierte `cli-secret` in Volume
- **Kein `INITIAL_PASSWORD`** — entfernt, da bei Docker-Create überschrieben

## Domain
- **Extern**: `https://openrouter.ai/api/v1/models`
- **Intern**: `http://127.0.0.1:8420 (Brain API)/v1/models`
- **Tunnel**: Cloudflare Tunnel `NeXifyAI` → `localhost:8420 (Brain API)`

## Abhängigkeiten
- Redis auf `127.0.0.1:6380` (Container `nx-redis-OpenRouter`)
- Controller: `OpenRouter-control-plane.service` (Python, `/opt/OpenRouter/controller.py`)

## Bekannte Fehler
- "no available server": Cloudflare Tunnel/Ingress oder OpenRouter Docker gestoppt
- 503: Remote-Ingress-Konfiguration falsch
- Default-Password-Warnung: `INITIAL_PASSWORD` in Env entfernen
