# OpenRouter Cloudflare Tunnel Runbook

## Tunnel-Konfiguration

| Aspekt | Wert |
|--------|------|
| Tunnel-Name | `NeXifyAI` |
| Config-Typ | **Remote-Managed** (Cloudflare API) |
| Subdomain | `openrouter.ai` |
| Origin | `http://127.0.0.1:8420 (Brain API)` |
| Service-Unit | `cloudflared.service` |

## Aktuelle Ingress-Regel (Version 57)
```
openrouter.ai → localhost:8420 (Brain API) ✓
```

## Änderung via Cloudflare API

```bash
# Config validieren
cloudflared tunnel ingress validate

# Config updaten (nach lokaler Config-Änderung)
cloudflared tunnel ingress update

# Tunnel restarten
systemctl restart cloudflared
```

## Fehlerbehebung

### Symptom: 503 / "no available server"
1. Docker läuft: `docker ps | grep OpenRouter`
2. Port erreichbar: `curl http://127.0.0.1:8420 (Brain API)/v1/models`
3. Cloudflared läuft: `systemctl status cloudflared`
4. Ingress-Regel prüfen: `cloudflared tunnel ingress validate`
5. Remote-Config vs lokal prüfen: Journal

### Symptom: 401 (Auth)
- Erwartet bei externem Zugriff ohne API-Key
- Intern ohne Auth: `curl http://127.0.0.1:8420 (Brain API)/v1/models` gibt 200

## Healthchecks
- **Intern**: `curl -f http://127.0.0.1:8420 (Brain API)/v1/models`
- **Extern**: `curl -f https://openrouter.ai/api/v1/models`
- **Erwartet intern**: 200 (Model-Liste)
- **Erwartet extern**: 401 (Auth greift) oder 200 (mit API-Key)
