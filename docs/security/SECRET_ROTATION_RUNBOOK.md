# NeXifyAI — Secret Rotation Runbook
> Owner: NeXifyAI Platform Team | Priority: P0 | Updated: 2026-05-24

## ⚠️ CRITICAL RULES
- NEVER output secret values in any log, PR, issue, comment, or terminal
- NEVER store secrets in the repository
- ALWAYS use least-privilege when generating replacement tokens
- ALWAYS close GitHub Secret Alert ONLY AFTER rotation is confirmed

## Step-by-Step Rotation Process

### Step 1: Identify Compromised Token
```bash
# View alert details (redacted) via GitHub UI or:
gh secret-scanning list-alerts --repo NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform
# Note: Only view alert metadata, NEVER copy/paste the actual value
```

### Step 2: Revoke at Provider
| Provider | Revocation URL |
|---|---|
| GitHub PAT | https://github.com/settings/tokens |
| OpenRouter | https://openrouter.ai/keys |
| Supabase | https://supabase.com/dashboard/project/*/settings/api |
| nScale | https://console.nscale.com |
| Revolut | Revolut Business Dashboard → API Keys |

### Step 3: Assess Exposure Window
```bash
# Check when the secret was first committed (partial pattern only, never full value)
git log --all --full-history -S "first_4_chars_only" -- 2>/dev/null | head -5
# Check GitHub Actions logs (do NOT print values)
# Check systemd journal (do NOT print values)
journalctl -u nexify-brain --since="7 days ago" | grep -i "token|key|secret" | wc -l
```

### Step 4: Generate Replacement
- Minimum scope / least privilege
- Set expiration (90 days max recommended)
- Store ONLY in:
  - GitHub Secrets (for CI/CD)
  - Systemd EnvironmentFile (for VDS services)
  - Vault/secret manager (if available)

### Step 5: Update Secret Store
```bash
# For GitHub Actions (via gh CLI):
gh secret set TOKEN_NAME --body "new_value" --repo NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform
# For VDS systemd services:
# Edit /etc/systemd/system/<service>.secrets (NOT inside repo — use systemd EnvironmentFile=)
# systemctl daemon-reload && systemctl restart <service>
```

### Step 6: Verify Services
- Verify Brain API: `curl http://localhost:PORT/health`
- Verify 9Router: `curl http://localhost:PORT/v1/models`
- Run CI pipeline to confirm secrets work

### Step 7: Close Alert
- Go to GitHub → Security → Secret Scanning
- Close alert with resolution: "Revoked and rotated"
- Add comment: "Token revoked at [provider] on [date], replacement issued"
- Do NOT include the old or new token value

### Step 8: Document Incident
- Create `docs/security/incidents/INCIDENT_<date>_<type>.md`
- Redacted form only
- Add to `lessons-learned.json`

## Token Registry (Metadata Only — No Values)
| Token Name | Provider | Used In | Rotation Interval | Last Rotated |
|---|---|---|---|---|
| OPENROUTER_API_KEY | OpenRouter | CI (cline-legacy), possibly Brain | 90 days | UNKNOWN — rotate now |
| GITHUB_TOKEN | GitHub | CI (auto) | Auto-rotated by GitHub | N/A |
| SUPABASE_* | Supabase | Backend, possibly CI | 90 days | UNKNOWN — check |
| NSCALE_* | nScale | Brain API | 90 days | UNKNOWN — check |
