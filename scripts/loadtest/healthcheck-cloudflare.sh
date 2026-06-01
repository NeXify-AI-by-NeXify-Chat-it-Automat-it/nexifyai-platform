#!/bin/bash
# NeXifyAI Cloudflare Hostname Healthcheck v1
# Usage: ./healthcheck-cloudflare.sh [--json] [--uptime-kuma]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

TS=$(date +%Y%m%d_%H%M)
LOG="/var/log/nexifyai/healthcheck-${TS}.log"
mkdir -p /var/log/nexifyai

MODE="${1:-normal}"

declare -A HOSTS=(
  ["nexifyai.cloud"]="Hauptdomain|200|active|critical"
  ["www.nexifyai.cloud"]="WWW-Redirect|307|active|high"
  ["admin.nexifyai.cloud"]="Admin Portal|200|active|high"
  ["ai-team.nexifyai.cloud"]="AI Team Chat|200|offline-known|low"
  ["analytics.nexifyai.cloud"]="Analytics|200|offline-known|low"
  ["auth.nexifyai.cloud"]="Auth Service|200|offline-known|low"
  ["brain.nexifyai.cloud"]="Brain API|200|active|critical"
  ["chat.nexifyai.cloud"]="Chat UI|200|offline-known|low"
  ["chatboard.nexifyai.cloud"]="Chat Board|200|offline-known|low"
  ["goose.nexifyai.cloud"]="Goose Agent|200|offline-known|low"
  ["grafana.nexifyai.cloud"]="Grafana Dashboard|200|needs-fix|medium"
  ["hermes.nexifyai.cloud"]="Hermes WebUI|200|needs-fix|medium"
  ["mdb.nexifyai.cloud"]="MindsDB|200|offline-known|low"
  ["mindsdb.nexifyai.cloud"]="MindsDB Alt|200|offline-known|low"
  ["monitoring.nexifyai.cloud"]="Monitoring|200|offline-known|low"
  ["status.nexifyai.cloud"]="Uptime Kuma|200|needs-fix|high"
  ["temporal.nexifyai.cloud"]="Temporal UI|200|offline-known|low"
  ["traefik.nexifyai.cloud"]="Traefik Dashboard|401|active|medium"
  ["webhook.nexifyai.cloud"]="Webhook|200|offline-known|low"
  ["nexify-automate.com"]="Agentur-Seite|200|active|critical"
  ["www.nexify-automate.com"]="Agentur-WWW|200|active|high"
)

PASS=0
WARN=0
FAIL=0
CRITICAL=0
SKIP=0

echo "=========================================================="
echo "  NeXifyAI Cloudflare Healthcheck — $(date)"
echo "=========================================================="
printf "  %-35s %-6s %-8s %s\n" "HOSTNAME" "STATUS" "CODE" "SERVICE"
echo "----------------------------------------------------------"

for host in "${!HOSTS[@]}"; do
  IFS='|' read -r desc expected issues priority <<< "${HOSTS[$host]}"

  # Check for known-offline / needs-fix markers
  is_known_offline=false
  is_needs_fix=false
  [[ "$issues" == *"offline-known"* ]] && is_known_offline=true
  [[ "$issues" == *"needs-fix"* ]] && is_needs_fix=true

  code=$(curl -sI -o /dev/null -w "%{http_code}" "https://$host" --connect-timeout 5 2>/dev/null || echo "FAIL")
  
  if $is_known_offline; then
    echo -e "⏸️  ${CYAN}%-33s SKIP  %-8s %s${NC}" "$host" "$code" "$desc (bekannt offline)"
    SKIP=$((SKIP + 1))
  elif $is_needs_fix; then
    echo -e "🔧  ${YELLOW}%-33s FIX   HTTP %-4s %s${NC}" "$host" "$code" "$desc"
    WARN=$((WARN + 1))
  elif [ "$code" = "FAIL" ] || [ "$code" = "000" ]; then
    echo -e "❌  ${RED}%-33s FAIL  %-8s %s${NC}" "$host" "CURL" "$desc"
    FAIL=$((FAIL + 1))
    [ "$priority" = "critical" ] && CRITICAL=$((CRITICAL + 1))
  elif [ "$code" = "$expected" ]; then
    echo -e "✅  ${GREEN}%-33s OK    HTTP %-4s %s${NC}" "$host" "$code" "$desc"
    PASS=$((PASS + 1))
  elif [ "$code" -ge 200 ] && [ "$code" -lt 400 ]; then
    echo -e "✅  ${GREEN}%-33s OK    HTTP %-4s %s${NC}" "$host" "$code" "$desc"
    PASS=$((PASS + 1))
  elif [ "$code" -ge 400 ] && [ "$code" -lt 500 ]; then
    echo -e "⚠️  ${YELLOW}%-33s WARN  HTTP %-4s %s${NC}" "$host" "$code" "$desc"
    WARN=$((WARN + 1))
  else
    echo -e "❌  ${RED}%-33s FAIL  HTTP %-4s %s${NC}" "$host" "$code" "$desc"
    FAIL=$((FAIL + 1))
    [ "$priority" = "critical" ] && CRITICAL=$((CRITICAL + 1))
  fi
done

echo "----------------------------------------------------------"
echo -e "${GREEN}✅ PASS: $PASS${NC} | ${YELLOW}⚠️  WARN: $WARN${NC} | ${RED}❌ FAIL: $FAIL${NC} | ${RED}🔥 CRITICAL: $CRITICAL${NC} | ${CYAN}⏸️  SKIP: ${SKIP}${NC}"
echo "=========================================================="

# Log
{
  echo "=== NeXifyAI Cloudflare Healthcheck — $(date) ==="
  echo "PASS=$PASS WARN=$WARN FAIL=$FAIL CRITICAL=$CRITICAL SKIP=$SKIP"
} > "$LOG"

# Exit codes for monitoring
[ $CRITICAL -gt 0 ] && exit 2
[ $FAIL -gt 0 ] && exit 1
exit 0
