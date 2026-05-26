#!/usr/bin/env bash
# 9Router Health Check — prüft Docker + Port + Recovery
set -euo pipefail

if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q '9router-5afd'; then
    systemctl start 9router-watchdog.service
    logger -t 9router-health "Container not running — watchdog triggered"
fi

if ! curl -sf http://127.0.0.1:20128/v1/models > /dev/null 2>&1; then
    docker restart 9router-5afd-niner-router-1 2>/dev/null || true
    logger -t 9router-health "Port 20128 unreachable — container restarted"
fi
