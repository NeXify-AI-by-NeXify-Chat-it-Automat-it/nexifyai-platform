#!/usr/bin/env bash
# ============================================================
# NeXify Goose — PM API Task-Driven Worker
# ============================================================
# Holt einen Task aus der Project Manager API, führt ihn aus,
# schreibt Ergebnis zurück, lädt Evidence ins Brain.
#
# Flow:
#   GET /tasks/next → Task holen
#   POST /tasks/{id}/claim → Task claimen (optional)
#   Brain-Kontext laden → Goose run mit Task-Prompt
#   POST /worker/callback → Ergebnis zurück
#   Brain-Update → Evidence speichern
#
# Exit Codes:
#   0  = Erfolg oder keine Tasks (graceful)
#   1  = Fehler
# ============================================================

set -Eeuo pipefail

ENV_FILE="/opt/nexify/goose-runtime/env/goose-cli.env"
REPO_DIR="/opt/nexify/repos/nexifyai-platform"
LOG_DIR="/var/log/nexify-goose"
GOOSE_BIN="/root/.local/bin/goose"
PM_API_URL="${PM_API_URL:-http://127.0.0.1:8421}"
PM_API_TOKEN="${PM_API_TOKEN:-pm_local_dev_token}"
BRAIN_API_URL="${BRAIN_API_URL:-http://127.0.0.1:8420}"
WORKER_TIMEOUT="${WORKER_TIMEOUT:-2700}"  # 45 minutes

# Source the CLI-mirrored environment
set -a
source "$ENV_FILE"
set +a

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

TS="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/worker_${TS}.log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
die() { log "FATAL: $*"; exit 1; }

log "=== NeXify Goose Worker — $TS ==="
log "PM_API_URL=$PM_API_URL"
log "GOOSE_BIN=$GOOSE_BIN"
log "GOOSE_VERSION=$("$GOOSE_BIN" --version 2>&1 || true)"
log "==================================="

# --------------------------------------------------
# Step 1: Next task from PM API
# --------------------------------------------------
log "Polling PM API for next task..."
NEXT=$(curl -sS -f "$PM_API_URL/tasks/next" 2>/dev/null || echo '{"queue_empty":true}')

QUEUE_EMPTY=$(echo "$NEXT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('queue_empty',True))" 2>/dev/null || true)

if [ "$QUEUE_EMPTY" = "True" ]; then
    log "No tasks in queue. Sleeping."
    exit 0
fi

TASK_ID=$(echo "$NEXT" | python3 -c "import sys,json; print(json.load(sys.stdin)['task']['task_id'])" 2>/dev/null || true)
GOAL=$(echo "$NEXT" | python3 -c "import sys,json; print(json.load(sys.stdin)['task']['goal'][:200])" 2>/dev/null || true)
MODE=$(echo "$NEXT" | python3 -c "import sys,json; print(json.load(sys.stdin)['task']['mode'])" 2>/dev/null || "implement")
ABORT_CONDITIONS=$(echo "$NEXT" | python3 -c "
import sys,json
t=json.load(sys.stdin)['task']
conds=t.get('abort_conditions',[]) or []
print('; '.join(conds) if conds else 'none specified')
" 2>/dev/null || "none specified")

if [ -z "$TASK_ID" ]; then
    log "Failed to parse task from response"
    exit 1
fi

log "Got task: $TASK_ID | mode=$MODE | goal=${GOAL:-unknown}"

# --------------------------------------------------
# Step 2: Claim task (update status to running)
# --------------------------------------------------
log "Claiming task $TASK_ID..."
CLAIM_RESP=$(curl -sS -X POST "$PM_API_URL/tasks/$TASK_ID/run" \
  -H "Authorization: Bearer $PM_API_TOKEN" \
  -H "Content-Type: application/json" 2>/dev/null || echo '{"error":"claim failed"}')
log "Claim response: $CLAIM_RESP"

# --------------------------------------------------
# Step 3: Load Brain context
# --------------------------------------------------
log "Loading Brain context..."
BRAIN_QUERY=$(curl -sS "$BRAIN_API_URL/query?q=${GOAL:-state}&limit=3" 2>/dev/null || echo '{}')
log "Brain context loaded ($(echo "$BRAIN_QUERY" | wc -c) bytes)"

# --------------------------------------------------
# Step 4: Build task prompt
# --------------------------------------------------
PROMPT=$(cat <<EOF
AUFGABE:
$GOAL

TASK-ID: $TASK_ID
MODUS: $MODE
QUELLE: Project Manager API

KONTEXT AUS BRAIN:
$(echo "$BRAIN_QUERY" | python3 -m json.tool 2>/dev/null | head -100)

REGELN:
- Dies ist ein PM-API-gesteuerter Task.
- Evidence-Pflicht.
- Keine Secrets ausgeben.
- Kein direkter Push auf main.
- Issue/Project/Brain nach Abschluss aktualisieren.
- Abbruch bei: $ABORT_CONDITIONS
EOF
)

log "Prompt built ($(echo "$PROMPT" | wc -c) bytes)"

# --------------------------------------------------
# Step 5: Execute Goose
# --------------------------------------------------
log "Starting Goose execution (timeout=${WORKER_TIMEOUT}s)..."
EXIT_CODE=0
OUTPUT=""

# Write prompt to temp file for isolation
TMP_PROMPT=$(mktemp /tmp/goose-task-prompts/XXXXXXXX.md)
mkdir -p /tmp/goose-task-prompts
echo "$PROMPT" > "$TMP_PROMPT"

set +e
OUTPUT=$(timeout "$WORKER_TIMEOUT" "$GOOSE_BIN" run \
  --instructions "$TMP_PROMPT" \
  --no-session \
  --max-turns 300 \
  --max-tool-repetitions 8 \
  --output-format text \
  < /dev/null 2>&1)
EXIT_CODE=$?
set -e

rm -f "$TMP_PROMPT"
log "Goose exit code: $EXIT_CODE"
log "Output lines: $(echo "$OUTPUT" | wc -l)"

# Save evidence locally
EVIDENCE_FILE="$LOG_DIR/evidence_${TASK_ID}_${TS}.txt"
echo "$OUTPUT" > "$EVIDENCE_FILE"
log "Evidence saved to $EVIDENCE_FILE"

# --------------------------------------------------
# Step 6: Callback to PM API
# --------------------------------------------------
if [ "$EXIT_CODE" -eq 0 ]; then
    STATUS="completed"
else
    STATUS="failed"
fi

SUMMARY=$(echo "$OUTPUT" | tail -50 | head -20 | tr '\n' ' ' | head -c 500)

CALLBACK_PAYLOAD=$(cat <<EOF
{
  "task_id": "$TASK_ID",
  "status": "$STATUS",
  "summary": $(echo "$SUMMARY" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "actions_taken": ["goose_worker_execution"],
  "evidence": ["$EVIDENCE_FILE"]
}
EOF
)

log "Sending callback (status=$STATUS)..."
CALLBACK_RESP=$(curl -sS -X POST "$PM_API_URL/worker/callback" \
  -H "Authorization: Bearer $PM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CALLBACK_PAYLOAD" 2>/dev/null || echo '{"error":"callback failed"}')
log "Callback response: $CALLBACK_RESP"

# --------------------------------------------------
# Step 7: Brain Update
# --------------------------------------------------
log "Updating Brain..."
BRAIN_PAYLOAD=$(cat <<EOF
{
  "category": "governance",
  "title": "Task $TASK_ID completed ($STATUS)",
  "content": "Task $TASK_ID mode=$MODE status=$STATUS goal=$GOAL",
  "source": "goose-worker",
  "tags": "worker,task,pipeline,$TASK_ID,$STATUS"
}
EOF
)

BRAIN_RESP=$(curl -sS -X POST "$BRAIN_API_URL/store" \
  -H "Content-Type: application/json" \
  -d "$BRAIN_PAYLOAD" 2>/dev/null || echo '{"error":"brain update failed"}')
log "Brain update: $BRAIN_RESP"

log "=== Worker finished for task $TASK_ID (status=$STATUS) ==="
exit 0
