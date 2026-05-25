#!/usr/bin/env bash
set -u

REPO_DIR="/opt/nexify/repos/nexifyai-platform"
RECIPE="$REPO_DIR/.goose/nexify-continuous.yaml"
LOG_DIR="$REPO_DIR/logs/goose"
LOCK_FILE="$REPO_DIR/.goose/continuous.lock"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR" || exit 1

# Lockfile-Handling mit PID-Prüfung
if [ -f "$LOCK_FILE" ]; then
  OLD_PID="$(cat "$LOCK_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Loop läuft bereits mit PID $OLD_PID"
    exit 1
  fi
  echo "Altes Lockfile gefunden, aber Prozess läuft nicht mehr. Entferne Lockfile."
  rm -f "$LOCK_FILE"
fi

echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"; echo "Gestoppt."; exit 0' INT TERM EXIT

export GOOSE_MODE=auto
export GOOSE_CONTEXT_STRATEGY=summarize
export GOOSE_DISABLE_SESSION_NAMING=true

ITERATION=1

while true; do
  TS="$(date '+%Y-%m-%d_%H-%M-%S')"
  LOG_FILE="$LOG_DIR/continuous_${TS}_iteration_${ITERATION}.log"

  {
    echo "============================================================"
    echo "NeXify Goose Continuous Run #$ITERATION - $TS"
    echo "Repo: $REPO_DIR"
    echo "Recipe: $RECIPE"
    echo "============================================================"
  } | tee -a "$LOG_FILE"

  # Prüfe ob --no-session unterstützt wird
  if goose run --help 2>&1 | grep -q -- "--no-session"; then
    timeout 45m goose run \
      --recipe "$RECIPE" \
      --with-builtin developer,github \
      --max-turns 1000 \
      --max-tool-repetitions 12 \
      --output-format text \
      --no-session \
      < /dev/null \
      2>&1 | tee -a "$LOG_FILE"
  else
    timeout 45m goose run \
      --recipe "$RECIPE" \
      --with-builtin developer,github \
      --max-turns 1000 \
      --max-tool-repetitions 12 \
      --output-format text \
      < /dev/null \
      2>&1 | tee -a "$LOG_FILE"
  fi

  EXIT_CODE=${PIPESTATUS[0]}

  {
    echo ""
    echo "Goose Exit Code: $EXIT_CODE"
    echo "Iteration #$ITERATION beendet."
  } | tee -a "$LOG_FILE"

  if [ "$EXIT_CODE" -eq 124 ]; then
    echo "⚠️ Timeout (45m) erreicht. Starte nächsten Durchlauf nach 20s." | tee -a "$LOG_FILE"
    sleep 20
  elif [ "$EXIT_CODE" -ne 0 ]; then
    echo "❌ Goose-Run fehlgeschlagen (Code $EXIT_CODE). Nächster Versuch nach 60s." | tee -a "$LOG_FILE"
    sleep 60
  else
    echo "✅ Durchlauf #$ITERATION sauber beendet. Nächster Start nach 20s." | tee -a "$LOG_FILE"
    sleep 20
  fi

  ITERATION=$((ITERATION + 1))
done
