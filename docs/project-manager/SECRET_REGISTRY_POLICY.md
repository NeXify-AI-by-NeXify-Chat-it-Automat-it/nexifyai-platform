# Secret Registry Policy

## Prinzipien

1. **Zentral** — Alle Secrets in Supabase Registry / `.env.complete` / systemd override
2. **Eindeutig** — Jeder Secret-Name nur einmal, eindeutig zugeordnet
3. **Autonom findbar** — Worker/Agent kann Secret-Metadaten abfragen ohne Werte zu sehen
4. **Kein Leak** — Keine Secrets in Logs, GitHub, Brain, Issues, PRs, Shell-Output

## Secret Registry Format (Supabase)

| Secret Name | Scope | Storage | Owner | Rotation | Consumer |
|:------------|:------|:--------|:------|:---------|:---------|
| `GITHUB_WEBHOOK_SECRET` | Repo | systemd override | pascal | jährlich | PM API |
| `GITHUB_APP_PRIVATE_KEY` | Org | systemd | pascal | 2 Jahre | GH App |
| `PROJECT_MANAGER_API_TOKEN` | Local | systemd | pascal | jährlich | PM API |
| `BRAIN_API_TOKEN` | Local | systemd | pascal | jährlich | PM API |
| `COPILOT_MCP_GITHUB_PAT` | Agents | GitHub UI | pascal | jährlich | GitHub Agent |
| `CLOUDFLARE_API_TOKEN` | Account | env file | pascal | jährlich | Cloudflare API |
| `DEEPSEEK_API_KEY` | Local | goose-cli.env | pascal | jährlich | 9Router/Goose |

## Verbote

- Keine Secrets in `ExecStart=` Commandlines
- Keine Secrets in Logs/Output
- Keine Secrets in GitHub Code, Issues, Actions
- Keine Secrets im Brain (Qdrant)
- Keine Secrets in dieser Dokumentation

## Erlaubte Secret-Referenzen in Codebase

Ja, wenn:
- Nur **Name** des Secrets
- Kein Wert
- Consumer (`services/project-manager-api/app/config.py`)
- Storage-Referenz (`systemd override`, `env file`, `GitHub UI`)
- Owner

## Wenn Secret fehlt

1. Secret-Name im Issue dokumentieren
2. Blocker setzen
3. Owner kontaktieren
4. Nicht "Key nicht gefunden" als akzeptierten Block stehen lassen

## Migration auf Vault (TODO)

Ziel: HashiCorp Vault / Infisical für alle Secrets
- Einheitliches API
- Rotation automatisieren
- Audit-Logs
- Worker authentisiert via Workload Identity
