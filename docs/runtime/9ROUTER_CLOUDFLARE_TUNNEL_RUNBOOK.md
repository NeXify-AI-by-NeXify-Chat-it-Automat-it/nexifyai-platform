# 9Router Cloudflare Tunnel Runbook

## Tunnel-Konfiguration

| Aspekt | Wert |
|--------|------|
| Tunnel-Name | `NeXifyAI` |
| Config-Typ | **Remote-Managed** (Cloudflare API) |
| Subdomain | `ai-router.nexifyai.cloud` |
| Origin | `http://127.0.0.1:20128` |
| Service-Unit | `cloudflared.service` |

## Aktuelle Ingress-Regel (Version 57)
```
ai-router.nexifyai.cloud → localhost:20128 ✓
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
1. Docker läuft: `docker ps | grep 9router`
2. Port erreichbar: `curl http://127.0.0.1:20128/v1/models`
3. Cloudflared läuft: `systemctl status cloudflared`
4. Ingress-Regel prüfen: `cloudflared tunnel ingress validate`
5. Remote-Config vs lokal prüfen: Journal

### Symptom: 401 (Auth)
- Erwartet bei externem Zugriff ohne API-Key
- Intern ohne Auth: `curl http://127.0.0.1:20128/v1/models` gibt 200

## Healthchecks
- **Intern**: `curl -f http://127.0.0.1:20128/v1/models`
- **Extern**: `curl -f https://ai-router.nexifyai.cloud/v1/models`
- **Erwartet intern**: 200 (Model-Liste)
- **Erwartet extern**: 401 (Auth greift) oder 200 (mit API-Key)
