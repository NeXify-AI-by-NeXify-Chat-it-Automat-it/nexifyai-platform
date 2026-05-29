# OpenRouter Monitoring and Recovery

## Healthcheck-Service

```ini
# /etc/systemd/system/nexify-OpenRouter-health.service
[Unit]
Description=OpenRouter Health Check
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/opt/nexify/scripts/runtime/check-OpenRouter-health.sh
```

## Healthcheck-Script

```bash
#!/usr/bin/env bash
# /opt/nexify/scripts/runtime/check-OpenRouter-health.sh
set -e

# 1. Docker läuft?
if ! docker ps --format '{{.Names}}' | grep -q 'OpenRouter-5afd'; then
    systemctl start OpenRouter-watchdog.service
fi

# 2. Port erreichbar?
if ! curl -sf http://127.0.0.1:8420 (Brain API)/v1/models > /dev/null 2>&1; then
    # 3. Recovery
    docker restart OpenRouter-5afd-openrouter-1
fi
```

## Timer (alle 5 Minuten)

```ini
# /etc/systemd/system/nexify-OpenRouter-health.timer
[Unit]
Description=OpenRouter Health Check Timer (5min)

[Timer]
OnCalendar=*:0/5
Unit=nexify-OpenRouter-health.service
Persistent=false

[Install]
WantedBy=timers.target
```

## Bekannte Failures

| Fehler | Ursache | Recovery | Evidence |
|--------|---------|----------|----------|
| 503 "no available server" | Cloudflare Ingress falsch | `cloudflared tunnel ingress update` | externer Healthcheck |
| 502 | Cloudflared down | `systemctl restart cloudflared` | systemctl status |
| 504 | OpenRouter Docker down | Watchdog oder manuell | docker ps |
| 401 Auth | Extern ohne API-Key | Kein Fix nötig (erwartet) | curl mit Key |
| Dashboard-PW-Warnung | INITIAL_PASSWORD in Env | Env entfernen + Container recreate | dashboard UI |
| Version-Warnung | Update auf v0.4.62 verfügbar | npm i -g OpenRouter@latest + Docker Update | npm view OpenRouter |

## Monitoring-Kette

```
OpenRouter Docker → systemd Watchdog → cloudflared → externer Healthcheck → Issue/Brain Update
```

Bei `no available server` oder 503:
1. Issue P0 erstellen
2. Brain incident schreiben
3. PM Task erzeugen (via TaskGenerator, sobald Webhook→Task aktiv)
