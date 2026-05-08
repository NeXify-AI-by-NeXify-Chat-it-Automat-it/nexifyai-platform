#!/bin/bash
# NeXifyAI Autopilot Heartbeat — wird via Cron */5 * * * * aufgerufen
DAEMON="/opt/nexifyai/scripts/autopilot-daemon.py"
PIDFILE="/opt/nexifyai/state/autopilot.pid"
HEARTBEAT="/opt/nexifyai/state/heartbeat.md"

# Prüfen ob Daemon läuft
if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    # Läuft bereits — Heartbeat aktuell?
    if [ -f "$HEARTBEAT" ]; then
        HEART_AGE=$(($(date +%s) - $(stat -c %Y "$HEARTBEAT")))
        if [ $HEART_AGE -gt 300 ]; then
            echo "[$(date -Iseconds)] WARN: Heartbeat zu alt (${HEART_AGE}s) — Restart"
            kill $(cat "$PIDFILE") 2>/dev/null
            sleep 2
        else
            exit 0  # Alles OK
        fi
    fi
fi

# Neustart
cd /opt/nexifyai-website-sicherheitskopie
nohup python3 "$DAEMON" >> /var/log/nexifyai-autopilot.log 2>&1 &
echo $! > "$PIDFILE"
echo "[$(date -Iseconds)] Autopilot Daemon gestartet (PID $!)"
