# 9Router Monitoring and Recovery

## Healthcheck-Service

```ini
# /etc/systemd/system/nexify-9router-health.service
[Unit]
Description=9Router Health Check
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/opt/nexify/scripts/runtime/check-9router-health.sh
```

## Healthcheck-Script

```bash
#!/usr/bin/env bash
# /opt/nexify/scripts/runtime/check-9router-health.sh
set -e

# 1. Docker läuft?
if ! docker ps --format '{{.Names}}' | grep -q '9router-5afd'; then
    systemctl start 9router-watchdog.service
fi

# 2. Port erreichbar?
if ! curl -sf http://127.0.0.1:20128/v1/models > /dev/null 2>&1; then
    # 3. Recovery
    docker restart 9router-5afd-niner-router-1
fi
```

## Timer (alle 5 Minuten)

```ini
# /etc/systemd/system/nexify-9router-health.timer
[Unit]
Description=9Router Health Check Timer (5min)

[Timer]
OnCalendar=*:0/5
Unit=nexify-9router-health.service
Persistent=false

[Install]
WantedBy=timers.target
```

## Bekannte Failures

| Fehler | Ursache | Recovery | Evidence |
|--------|---------|----------|----------|
| 503 "no available server" | Cloudflare Ingress falsch | `cloudflared tunnel ingress update` | externer Healthcheck |
| 502 | Cloudflared down | `systemctl restart cloudflared` | systemctl status |
| 504 | 9Router Docker down | Watchdog oder manuell | docker ps |
| 401 Auth | Extern ohne API-Key | Kein Fix nötig (erwartet) | curl mit Key |
| Dashboard-PW-Warnung | INITIAL_PASSWORD in Env | Env entfernen + Container recreate | dashboard UI |
| Version-Warnung | Update auf v0.4.62 verfügbar | npm i -g 9router@latest + Docker Update | npm view 9router |

## Monitoring-Kette

```
9Router Docker → systemd Watchdog → cloudflared → externer Healthcheck → Issue/Brain Update
```

Bei `no available server` oder 503:
1. Issue P0 erstellen
2. Brain incident schreiben
3. PM Task erzeugen (via TaskGenerator, sobald Webhook→Task aktiv)
