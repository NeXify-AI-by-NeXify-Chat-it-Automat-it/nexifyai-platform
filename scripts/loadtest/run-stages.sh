#!/bin/bash
# NeXifyAI Enterprise — k6 Load Test Runner
# Usage: ./run-stages.sh [stage] [vus] [duration]
# Stages: stage1 (brain-9router-gateway)
set -euo pipefail

STAGE="${1:-stage1}"
VUS="${2:-10}"
DURATION="${3:-30s}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${RESULTS_DIR}"

case "${STAGE}" in
  stage1)
    SCRIPT="${SCRIPT_DIR}/stage1-brain-9router-gateway.js"
    ;;
  *)
    echo "Unknown stage: ${STAGE}"
    echo "Available: stage1"
    exit 1
    ;;
esac

echo "=========================================="
echo "NeXifyAI Load Test — ${STAGE}"
echo "  VUs:       ${VUS}"
echo "  Duration:  ${DURATION}"
echo "  Script:    ${SCRIPT}"
echo "  Results:   ${RESULTS_DIR}/${STAGE}-${TIMESTAMP}.json"
echo "=========================================="

k6 run \
  --vus "${VUS}" \
  --duration "${DURATION}" \
  --summary-export "${RESULTS_DIR}/${STAGE}-${TIMESTAMP}.json" \
  --summary-trend-stats "avg,p(50),p(90),p(95),p(99),min,max" \
  "${SCRIPT}" 2>&1 | tee "${RESULTS_DIR}/${STAGE}-${TIMESTAMP}.log"

echo ""
echo "Done. Results saved to:"
echo "  JSON: ${RESULTS_DIR}/${STAGE}-${TIMESTAMP}.json"
echo "  LOG:  ${RESULTS_DIR}/${STAGE}-${TIMESTAMP}.log"
