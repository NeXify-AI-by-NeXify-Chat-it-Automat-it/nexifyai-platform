# NeXifyAI — Connection Inventory
# Stand: 2026-05-08 | Letzter Audit: 2026-05-08 03:00 CEST

## Prinzip
Jede Verbindung muss dauerhaft und ohne manuelles Zutun funktionieren.
Token-Ablauf → 30-Tage-Warnung → automatische Erneuerung oder Eskalation.

---

## 1. GitHub

| Feld | Wert |
|------|------|
| **Typ** | SSH-Key + HTTPS-Token |
| **User** | nexifyai-dev |
| **Auth-Methode** | SSH Key (ed25519, `~/.ssh/id_ed25519_nexifyai`) |
| **Token** | GH_TOKEN (repo-scoped) |
| **Ablauf** | Nie (SSH-Key), Token: unbekannt |
| **Erneuerung** | SSH-Key persistent auf VPS + Container |
| **Health-Check** | `ssh -T git@github.com` → "Hi nexifyai-dev!" |
| **Status** | ✅ Aktiv |

## 2. Vercel

| Feld | Wert |
|------|------|
| **Typ** | API-Token + Git-Integration |
| **Team** | agentur |
| **Project** | frontend (prj_abAYg51SsmuIzdVKdITCLwGtQCF7) |
| **Auth-Methode** | VERCEL_TOKEN (env) |
| **Ablauf** | Unbekannt |
| **Erneuerung** | Token in CI-Secrets + VPS-Env |
| **Health-Check** | `curl -H "Authorization: Bearer $VERCEL_TOKEN" https://api.vercel.com/v9/projects` |
| **Status** | ✅ Aktiv (Deploy 1366c57 live) |

## 3. Supabase (Self-Hosted)

| Feld | Wert |
|------|------|
| **Typ** | PostgreSQL (direkt) |
| **Host** | localhost:5432 |
| **User** | postgres |
| **Auth-Methode** | Password (postgres) |
| **Ablauf** | Nie (kein Token) |
| **Erneuerung** | N/A (lokale Verbindung) |
| **Health-Check** | `psql -h localhost -U postgres -c "SELECT 1"` |
| **Status** | ✅ Aktiv |

## 4. DeepSeek / OpenRouter

| Feld | Wert |
|------|------|
| **Typ** | API-Key |
| **Endpoint** | https://openrouter.ai/api/v1 |
| **Auth-Methode** | Bearer Token (OPENROUTER_API_KEY) |
| **Ablauf** | Unbekannt |
| **Erneuerung** | Key in .env + VPS-Env |
| **Health-Check** | `curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models` |
| **Status** | ✅ Aktiv |

## 5. Plausible CE

| Feld | Wert |
|------|------|
| **Typ** | Self-Hosted Docker |
| **Host** | analytics.nexifyai.cloud → 127.0.0.1:8088 |
| **Auth-Methode** | Kein Token (intern) |
| **Ablauf** | Nie (self-hosted) |
| **Erneuerung** | N/A |
| **Health-Check** | `curl -o /dev/null -w "%{http_code}" https://analytics.nexifyai.cloud` |
| **Status** | ✅ Aktiv |

## 6. Resend (E-Mail)

| Feld | Wert |
|------|------|
| **Typ** | API-Key |
| **Auth-Methode** | Bearer Token (RESEND_API_KEY) |
| **Ablauf** | Unbekannt |
| **Erneuerung** | Key in .env |
| **Health-Check** | `curl -H "Authorization: Bearer $RESEND_API_KEY" https://api.resend.com/emails` |
| **Status** | ✅ Aktiv |

## 7. Hostinger VPS

| Feld | Wert |
|------|------|
| **Typ** | SSH-Key |
| **Host** | 72.62.152.47 |
| **User** | root |
| **Auth-Methode** | SSH Key (hermes_vps_key) |
| **Ablauf** | Nie (SSH-Key) |
| **Erneuerung** | Key in /opt/data/ssh_keys/ |
| **Health-Check** | `ssh -i hermes_vps_key root@72.62.152.47 hostname` |
| **Status** | ✅ Aktiv |

## 8. Traefik

| Feld | Wert |
|------|------|
| **Typ** | Reverse Proxy (intern) |
| **Auth-Methode** | Kein Token (intern) |
| **Ablauf** | Let's Encrypt: alle 90 Tage (auto-renew) |
| **Erneuerung** | Traefik ACME |
| **Health-Check** | `curl -k https://mail.nexifyai.cloud` |
| **Status** | ✅ Aktiv |

## 9. GitHub Container Registry (Hermes Agent Image)

| Feld | Wert |
|------|------|
| **Typ** | ghcr.io |
| **Auth-Methode** | GH_TOKEN |
| **Ablauf** | Wie GH_TOKEN |
| **Health-Check** | `docker pull ghcr.io/hostinger/hvps-hermes-agent:latest --dry-run` |
| **Status** | ✅ Aktiv |

---

## Health-Check-Ergebnisse

| Datum | GitHub | Vercel | Supabase | DeepSeek | Plausible | Resend | VPS | Traefik | Score |
|-------|--------|--------|----------|----------|-----------|--------|-----|---------|-------|
| 2026-05-08 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |

---

## Token-Ablauf-Warnungen

| Verbindung | Token | Ablauf | Warnung | Aktion |
|-----------|-------|--------|---------|--------|
| GH_TOKEN | PAT | Unbekannt | Prüfen | Token-Scope dokumentieren |
| VERCEL_TOKEN | API | Unbekannt | Prüfen | Team-Token vs Persönlich? |
| OPENROUTER_API_KEY | API | Unbekannt | Prüfen | Ablaufdatum prüfen |
| RESEND_API_KEY | API | Unbekannt | Prüfen | Ablaufdatum prüfen |
