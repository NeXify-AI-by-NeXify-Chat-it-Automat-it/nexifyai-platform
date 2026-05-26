# 9Router Operating Model

## Purpose
AI-Router/Reasoning-Proxy für NeXify AI. Stellt LLM-Modelle über OpenAI-konforme `/v1`-API bereit.

## Technische Basis
- **Image**: `ghcr.io/decolua/9router:latest`
- **Container**: `9router-5afd-niner-router-1`
- **Port**: `127.0.0.1:20128`
- **Version**: `v0.4.59` (Update auf v0.4.62 verfügbar — bewusst deferred: kein Upgrade ohne Release-Notes-Prüfung und Backup)
- **Dashboard**: NeXify AI Chat auf Port 20128
- **Startbefehl**: `node server.js` via `/entrypoint.sh`
- **Restart-Policy**: `unless-stopped`
- **Watchdog**: `9router-watchdog.service` (startet Container bei Ausfall)

## Datenhaltung
- **Config/Logs**: Docker Volume `9router-5afd_data` → `/app/data`
- **Usage**: Docker Volume `9router-5afd_usage-data` → `/root/.9router`
- **Env-File**: `/opt/9router/env/9router.env` (kein Secret-Betrieb)

## Authentication
- **Intern**: Kein Auth auf `127.0.0.1:20128`
- **Extern**: HTTPS via Cloudflare, `API_KEY_SECRET` im Container
- **Dashboard**: Auth über persistierte `cli-secret` in Volume
- **Kein `INITIAL_PASSWORD`** — entfernt, da bei Docker-Create überschrieben

## Domain
- **Extern**: `https://ai-router.nexifyai.cloud/v1/models`
- **Intern**: `http://127.0.0.1:20128/v1/models`
- **Tunnel**: Cloudflare Tunnel `NeXifyAI` → `localhost:20128`

## Abhängigkeiten
- Redis auf `127.0.0.1:6380` (Container `nx-redis-9router`)
- Controller: `9router-control-plane.service` (Python, `/opt/9router/controller.py`)

## Bekannte Fehler
- "no available server": Cloudflare Tunnel/Ingress oder 9Router Docker gestoppt
- 503: Remote-Ingress-Konfiguration falsch
- Default-Password-Warnung: `INITIAL_PASSWORD` in Env entfernen
