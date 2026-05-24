# Vault Solution Evaluation - Recommendation

## Result: Infisical (score 9/10)

### Scoring
| Solution | Score | Self-Hosted | API-First | Worker-Ready | License |
|---|---|---|---|---|---|
| Infisical | 9 | Yes | Yes | Yes | EE + MIT SDK |
| HashiCorp Vault | 7 | Yes | Yes | Yes | BSL (restricted) |
| Doppler | 5 | No (SaaS) | Yes | Yes | Proprietary |
| Supabase Vault | 3 | Yes | No | No | Postgres |
| 1Password | 4 | No | Yes | No | Enterprise |

### Why Infisical
- Self-host via Docker (~100MB)
- Python SDK (python-infisical) for vault_compat integration
- Ephemeral leases match our lease_manager design
- Auto-rotation support
- Secrets as CI/CD-native objects

### Migration Path
1. Deploy Infisical container
2. Point injection_bridge.py to Infisical API
3. Migrate DS_ env vars to Infisical secrets
4. vault_compat becomes the local cache layer
5. Enable auto-rotation through Infisical

### Fallback
HashiCorp Vault if enterprise compliance specifically requires it.
