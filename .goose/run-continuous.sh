#!/usr/bin/env bash
set -u

REPO_DIR="/opt/nexify/repos/nexifyai-platform"
RECIPE="$REPO_DIR/.goose/nexify-continuous.yaml"
LOG_DIR="$REPO_DIR/logs/goose"
LOCK_FILE="$REPO_DIR/.goose/continuous.lock"

mkdir -p "$LOG_DIR"

cd "$REPO_DIR" || exit 1

if [ -f "$LOCK_FILE" ]; then
  echo "Loop läuft vermutlich bereits. Lockfile vorhanden: $LOCK_FILE"
  echo "Falls sicher kein Prozess läuft: rm $LOCK_FILE"
  exit 1
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

  echo "============================================================" | tee -a "$LOG_FILE"
  echo "NeXify Goose Continuous Run #$ITERATION - $TS" | tee -a "$LOG_FILE"
  echo "============================================================" | tee -a "$LOG_FILE"

  goose run \
    --recipe "$RECIPE" \
    --with-builtin developer,github \
    --max-turns 1000 \
    --max-tool-repetitions 12 \
    --output-format text \
    2>&1 | tee -a "$LOG_FILE"

  EXIT_CODE=${PIPESTATUS[0]}

  echo "" | tee -a "$LOG_FILE"
  echo "Goose Exit Code: $EXIT_CODE" | tee -a "$LOG_FILE"

  if [ "$EXIT_CODE" -ne 0 ]; then
    echo "Goose-Run fehlgeschlagen. Nächster Versuch nach 60 Sekunden." | tee -a "$LOG_FILE"
    sleep 60
  else
    echo "Durchlauf abgeschlossen. Nächster Durchlauf nach 20 Sekunden." | tee -a "$LOG_FILE"
    sleep 20
  fi

  ITERATION=$((ITERATION + 1))
done
