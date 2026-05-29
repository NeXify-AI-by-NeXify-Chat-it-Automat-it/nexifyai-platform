#!/usr/bin/env bash
# NeXifyAI — GitHub Label Sync Script
# Usage: bash scripts/github/sync-labels.sh
# Requires: gh auth login
# Updated: 2026-05-24

set -euo pipefail

REPO="NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform"

echo "Syncing labels to ${REPO}..."

create_label() {
  local name="$1" color="$2" desc="$3"
  gh label create "$name" --color "$color" --description "$desc" --repo "$REPO" --force 2>/dev/null && \
    echo "  ✅ $name" || echo "  ⚠️  $name (may already exist)"
}

echo "--- Governance ---"
create_label "governance"       "0075ca" "DOS/Governance policy changes"
create_label "dos"              "0075ca" "DOS standard document"
create_label "resource-first"   "0075ca" "Resource-first principle applied"
create_label "clean-reuse"      "0075ca" "Clean reuse pattern"
create_label "documentation"    "0075ca" "Documentation changes only"
create_label "adr"              "0075ca" "Architecture Decision Record"
create_label "learning"         "0075ca" "Learning/lessons-learned update"
create_label "prevention-rule"  "0075ca" "Prevention rule added or updated"

echo "--- Security ---"
create_label "security"         "d93f0b" "Security-relevant change"
create_label "security:critical" "b60205" "Critical security issue"
create_label "security:high"    "d93f0b" "High severity security issue"
create_label "security:medium"  "e4e669" "Medium severity security issue"
create_label "security:low"     "0e8a16" "Low severity security issue"
create_label "secret-leak"      "b60205" "Secret or token exposure"
create_label "codeql"           "d93f0b" "CodeQL alert related"
create_label "dependabot"       "0075ca" "Dependabot update"
create_label "vulnerability"    "d93f0b" "Known vulnerability"

echo "--- CI/CD ---"
create_label "ci"               "e4e669" "CI/CD pipeline change"
create_label "github-actions"   "e4e669" "GitHub Actions workflow"
create_label "deployment"       "e4e669" "Deployment configuration"
create_label "vercel"           "e4e669" "Vercel deployment related"
create_label "legacy-cline"     "cccccc" "Legacy Cline system (dead)"
create_label "docs-only"        "0075ca" "Documentation-only, no deploy"

echo "--- Work Type ---"
create_label "bug"              "d73a4a" "Bug fix"
create_label "enhancement"      "a2eeef" "New feature or improvement"
create_label "chore"            "e4e669" "Maintenance task"
create_label "refactor"         "a2eeef" "Code refactor"
create_label "cleanup"          "e4e669" "Code cleanup"
create_label "audit"            "d93f0b" "Security or compliance audit"
create_label "needs-triage"     "ededed" "Requires classification"
create_label "blocked"          "d73a4a" "Blocked by dependency"
create_label "ready-for-review" "0e8a16" "Ready for human review"

echo "--- Contributor ---"
create_label "good first issue" "7057ff" "Good for newcomers"
create_label "help wanted"      "008672" "Extra attention needed"

echo "--- Platform ---"
create_label "frontend"         "1d76db" "Frontend / React"
create_label "backend"          "1d76db" "Backend / FastAPI"
create_label "fullstack"        "1d76db" "Full-stack change"
create_label "supabase"         "1d76db" "Supabase related"
create_label "cloudflare"       "1d76db" "Cloudflare related"
create_label "docker"           "1d76db" "Docker/container"
create_label "brain"            "5319e7" "Enterprise Brain system"
# create_label "9router"          "5319e7" "9Router LLM gateway"  # REMOVED 2026-05-29
create_label "goose"            "5319e7" "Goose AI agent"

echo "--- Project Type ---"
create_label "customer-project" "b60205" "Customer project - handle carefully"
create_label "core-platform"    "0075ca" "Core NeXifyAI platform"
create_label "legacy"           "cccccc" "Legacy system"
create_label "shadow-system"    "cccccc" "Unapproved shadow system"

echo ""
echo "Label sync complete for ${REPO}"