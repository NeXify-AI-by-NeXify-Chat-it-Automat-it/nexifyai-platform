# 15 — GitHub Secrets and Environments

> **Stand: 2026-05-26**
> Diese Policy dokumentiert alle Secrets, Environments und sicheren Konfigurationswerte
> für das Repo `NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`.
>
> **⚠️ Keine Secret-Werte in diesem Dokument — nur Namen, Zweck, Status und Quelle.**

---

## 1. Secret-Typen

| Typ | Beschreibung | Speicherort |
| --- | --- | --- |
| Repository Secret | Pro Repo, für alle Workflows | `gh secret list --repo ...` |
| Environment Secret | Nur in bestimmten Environments | `gh secret list --env ... --repo ...` |
| Dependabot Secret | Für Dependabot-Workflows | `gh secret list --app dependabot --repo ...` |
| Actions Secret | Für Self-Hosted Runner | `gh secret list --app actions --repo ...` |
| Codespace Secret | Für Codespace-Nutzung | GitHub Settings → Codespaces |
| VDS Local | Nur auf VDS, nie in GitHub | `/opt/nexify/secrets/` |
| Brain Secret | Im Enterprise Brain gespeichert | Via `brainStore` mit `tags: secret` |

---

## 2. Secret-Matrix

### Repository Secrets (GitHub)

| Secret Name | Zweck | Gesetzt | Quelle | Workflow |
| --- | --- | --- | --- | --- |
| *(keine)* | — | ❌ 0 Secrets gesetzt | — | — |

**Aktuell: 0 Repository Secrets konfiguriert.**
Erwartet werden Secrets für: DeepSeek/LLM, nscale, Supabase, Vercel, Cloudflare, Deployment, Monitoring, Security Scanner, Webhooks.

### Environment Secrets

| Environment | Secrets | Status |
| --- | --- | --- |
| `cline-actions` | 0 | ❌ Leer |
| `production` | 0 | ❌ Leer |
| `Production – frontend` | 0 | ❌ Leer |
| `Production – nexifyai-platform` | 0 | ❌ Leer |
| `Production – web` | 0 | ❌ Leer |

**5 Environments vorhanden, keine Secrets gesetzt.**

### VDS Local Secrets

| Pfad | Inhalt | Status |
| --- | --- | --- |
| `/opt/nexify/secrets/github-app/private-key.pem` | GitHub App Private Key | ✅ chmod 600 |
| `/opt/nexify/secrets/github-app/app-id` | GitHub App ID: 3865469 | ✅ |
| `/opt/nexify/secrets/github-app/installation-id` | Org Installation ID: 135674562 | ✅ |

---

## 3. Erwartete Secrets (Namen und Zweck)

Folgende Secrets müssen gesetzt werden (ohne Werte):

| Kategorie | Secret Name | Scope | Zweck | Priorität |
| --- | --- | --- | --- | --- |
| **LLM** | `DEEPSEEK_API_KEY` | Repo | DeepSeek-API für KI-Funktionen | P0 |
| **LLM** | `OPENAI_API_KEY` | Repo | OpenAI-API-Fallback | P1 |
| **Deployment** | `VERCEL_TOKEN` | Repo | Vercel-Deployment | P0 |
| **Deployment** | `VERCEL_ORG_ID` | Repo | Vercel-Organisations-ID | P1 |
| **Deployment** | `VERCEL_PROJECT_ID` | Repo | Vercel-Projekt-ID | P1 |
| **Deployment** | `CLOUDFLARE_API_TOKEN` | Repo | Cloudflare-API | P1 |
| **Deployment** | `CLOUDFLARE_ZONE_ID` | Repo | Cloudflare-Zone | P1 |
| **Database** | `SUPABASE_URL` | Repo/Env | Supabase-Projekt-URL | P0 |
| **Database** | `SUPABASE_SERVICE_KEY` | Repo/Env | Supabase-Service-Role-Key | P0 |
| **Database** | `SUPABASE_ANON_KEY` | Repo/Env | Supabase-Anon-Key | P1 |
| **Auth** | `NEXTAUTH_SECRET` | Production Env | NextAuth-Verschlüsselung | P0 |
| **Auth** | `JWT_SECRET` | Production Env | JWT-Signatur | P0 |
| **GitHub** | `GH_TOKEN` | Dependabot | Dependabot-PAT (nur nötig für private deps) | P2 |
| **GitHub** | `GITHUB_APP_WEBHOOK_SECRET` | Repo | Webhook-Validierung | P1 |
| **Brain** | `BRAIN_API_KEY` | Repo | Enterprise Brain API | P0 |
| **Brain** | `QDRANT_API_KEY` | Repo | Qdrant-Vektor-DB | P1 |
| **9Router** | `NINEROUTER_API_KEY` | Repo | 9Router-API | P1 |
| **Monitoring** | `SENTRY_DSN` | Production Env | Sentry-Error-Tracking | P1 |
| **Webhook** | `WEBHOOK_SECRET` | Repo | NeXify-Webhook-Signatur | P1 |

---

## 4. Secret-Quellen auf dem VDS

| Quelle | Beschreibung | Zugriff |
| --- | --- | --- |
| `/opt/nexify/secrets/` | Sichere Secret-Ablage | root-only (chmod 600) |
| `.env`-Dateien in Repos | **Nicht erlaubt** — nur als Template (.env.example) | Ausgeschlossen |
| `~/.config/gh/hosts.yml` | GitHub-Credentials — enthält PAT ohne PR-Write | Nur GitHub Auth |
| Environment-Variablen | `GH_TOKEN` war gesetzt, **entfernt** | Nicht mehr aktiv |

---

## 5. Secret-Setzungs-Regeln

### Erlaubt

```bash
# Aus Datei (sicher)
printf '%s' "$(cat /pfad/zum/secret)" | gh secret set SECRET_NAME \
  --repo NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform \
  --body-file -

# Aus Environment-Variable (wenn nicht im Chat)
printf '%s' "$VALUE" | gh secret set SECRET_NAME --body-file -

# Interaktiv (auf VDS)
gh secret set SECRET_NAME --repo ... --body-file -
```

### Nicht erlaubt

```bash
❌ gh secret set SECRET_NAME --body "Klartext..."
❌ echo "secret..." | gh secret set ...
❌ Secret-Werte in Chat, Logs oder Repo
```

---

## 6. Secret-Rotation

| Regel | Intervall |
| --- | --- |
| GitHub App Private Key | Nur bei Kompromittierung |
| API Keys (DeepSeek, Supabase, etc.) | Alle 90 Tage |
| Webhook Secrets | Alle 180 Tage |
| PATs | Nur Notfall — durch GitHub App ersetzen |
| JWT Secrets | Alle 90 Tage |

---

## 7. Offene Secret-Lücken

| Lücke | Risiko | Aktion |
| --- | --- | --- |
| 0 Repository Secrets gesetzt | 🚨 Alle Workflows ohne echte Secrets | Alle P0-Secrets setzen |
| 5 Environments ohne Secrets | 🚨 Production-Deployment blockiert | P0-Secrets in Production-Envs setzen |
| Keine Dependabot Secrets | ⚠️ Private Dependencies nicht installierbar | Nur bei Bedarf |

---

## 8. Nächste Schritte

```text
P0:
1. DEEPSEEK_API_KEY setzen (Repro Secret)
2. SUPABASE_URL + SUPABASE_SERVICE_KEY setzen (Production Env)
3. VERCEL_TOKEN setzen (Repo Secret)
4. BRAIN_API_KEY setzen (Repo Secret)
5. NEXTAUTH_SECRET setzen (Production Env)

P1:
6. CLOUDFLARE_API_TOKEN setzen
7. SENTRY_DSN setzen (Production Env)
8. WEBHOOK_SECRET setzen
9. 9Router, OpenAI, Qdrant Secrets setzen

P2:
10. Dependabot Secrets prüfen
11. Nicht mehr benötigte Secrets identifizieren und löschen
```
