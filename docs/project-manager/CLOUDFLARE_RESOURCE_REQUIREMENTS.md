# Cloudflare Resource Requirements

## Jede externe Funktion benötigt vollständige Kette

### 1. DNS
- Subdomain eintragen (z.B. `webhook.nexifyai.cloud`)
- CNAME/Eintrag auf Tunnel-Ziel

### 2. Cloudflare Tunnel Ingress
- Tunnel: `NeXifyAI` (ID: `150653a6-2bf1-4f9e-9a47-8384a6c67b6f`)
- Ingress Rule per `cloudflared tunnel ingress update`
- Ziel: `localhost:<port>`
- Config ist remote-managed (Cloudflare API), lokale Config wird ignoriert

### 3. Origin Service
- systemd Service muss laufen
- Port muss listen
- Launched via systemd override

### 4. Auth / HMAC
- HMAC-Secret für Webhooks
- API-Token für AI-Router
- Brain API Key für externe Zugriffe

### 5. Healthchecks
- Intern: `curl http://127.0.0.1:<port>/health`
- Extern: `curl https://<subdomain>.nexifyai.cloud/<health>`
- Beide müssen OK sein

### 6. Monitoring (Kuma)
| Subdomain | Check URL | Intervall |
|:----------|:----------|:----------|
| brain | https://brain.nexifyai.cloud/health | 60s |
| ai-router | https://openrouter.ai/api/v1/models | 60s |
| webhook | https://webhook.nexifyai.cloud | 60s |

## Aktuelle Subdomain-zu-Port-Matrix

| Subdomain | Port | Service | Status | Cloudflare Ingress |
|:----------|:-----|:--------|:-------|:-------------------|
| nexifyai.cloud | 8421 | PM API | ✅ | Explicit route |
| brain.nexifyai.cloud | 8420 | Brain API | ✅ | Explicit route |
| openrouter.ai | 20128 | OpenRouter | ✅ | Explicit route |
| webhook.nexifyai.cloud | 8421 | PM API | ✅ | Explicit route |
| * (catchall) | — | — | ✅ HTTP 404 | Explicit catchall |

## Keine Fertigmeldung ohne:
- GitHub Issue / PR existiert
- Cloudflare Ingress konfiguriert
- Interne + externe Healthchecks grün
- Monitoring aktiv
- Brain Update geschrieben
- Evidence dokumentiert
