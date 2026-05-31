#!/bin/bash
# k6 Load Test Runner — NeXifyAI
# Usage: ./run-all.sh [duration]

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
TS=$(date +%Y%m%d_%H%M)
REPORT_DIR="${DIR}/reports/${TS}"
mkdir -p "$REPORT_DIR"

export BASE_URL="${BASE_URL:-http://127.0.0.1:8420}"
export ROUTER_URL="${ROUTER_URL:-http://localhost:20128/v1}"

echo "=== NeXifyAI Load Tests — $(date) ==="
echo "Brain API: $BASE_URL"
echo "9Router:   $ROUTER_URL"
echo "Reports:   $REPORT_DIR"
echo ""

# 1. Brain API
echo "--- Test: Brain API ---"
k6 run --out json="${REPORT_DIR}/brain.json" "${DIR}/k6-brain.js" 2>&1 | tee "${REPORT_DIR}/brain.log" || true

sleep 2

# 2. 9Router (nur wenn nicht --skip-llm)
if [ "${SKIP_LLM:-}" != "1" ]; then
  echo ""
  echo "--- Test: 9Router LLM (vorsichtig) ---"
  k6 run --vus 2 --duration 30s --out json="${REPORT_DIR}/9router.json" "${DIR}/k6-9router.js" 2>&1 | tee "${REPORT_DIR}/9router.log" || true
else
  echo "--- SKIP 9Router (SKIP_LLM=1) ---"
fi

echo ""
echo "=== Reports: ${REPORT_DIR} ==="
ls -la "$REPORT_DIR"
