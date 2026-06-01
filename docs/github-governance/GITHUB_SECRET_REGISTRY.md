# GitHub Secrets Registry

## Service Account Credentials (GitHub CLI)

| Secret Name | Category | Owner | Storage | Scope | Rotation | Status |
|-------------|----------|-------|---------|-------|----------|--------|
| `NEXIFYAI_GITHUB_USER` | GitHub Auth | pascal | `.env.complete` | GitHub CLI (sudo/gh auth) | — | ✅ Dokumentiert |
| `NEXIFYAI_GITHUB_PASSWORD` | GitHub Auth | pascal | `.env.complete` + systemd override | GitHub CLI (sudo/gh auth) | Nach Incident | ✅ Dokumentiert |

## Personal Access Tokens (PATs)

| Secret Name | Category | Owner | User | Scope | Status |
|-------------|----------|-------|------|-------|--------|
| `GITHUB_PAT_NEXIFYDEV` | GitHub PAT | pascal | `nexifyai-dev` | — | 🔴 EXPIRED/INVALID (HTTP 401 am 2026-05-27) — **Muss neu erstellt werden** |
| `GITHUB_PAT_ORG` | GitHub PAT | pascal | `nexifyai-dev` | Orgs, Repos | ✅ Valide (2026-05-27 verifiziert) |

## GitHub App

| Secret Name | Category | Owner | Storage | Scope | Status |
|-------------|----------|-------|---------|-------|--------|
| `GITHUB_APP_ID` | GitHub App | pascal | GitHub Secrets | 3865469 | ❌ Fehlt in GitHub UI |
| `GITHUB_APP_INSTALLATION_ID` | GitHub App | pascal | GitHub Secrets | Org=135674562, User=135674457 | ❌ Fehlt in GitHub UI |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App | pascal | systemd override + `/workspace/secrets/` | RSA 2048 | ✅ Systemd + Workspace |
| `GITHUB_APP_CLIENT_ID` | GitHub App | pascal | — | `Iv23li7oxPfvxfc9eXyu` | ✅ Dokumentiert |

### App Installationen (2026-05-27 verifiziert)

| Target | Installation ID | Type | Repository Selection | Permissions |
|--------|----------------|------|---------------------|-------------|
| `NeXify-AI-by-NeXify-Chat-it-Automat-it` | 135674562 | Organization | all | Full write (pages, checks, issues, actions, members, secrets, contents, packages, workflows, codespaces, deployments, discussions, pull_requests, administration, security_events, webhooks, projects, dependabot, attestations, environments, merge_queues, custom_properties, etc.) |
| `nexifyai-dev` | 135674457 | User | all | Full write (same scopes minus org-level permissions) |

## Webhook

| Secret Name | Purpose | Status |
|-------------|---------|--------|
| `GITHUB_WEBHOOK_SECRET` | HMAC-SHA256 | ✅ systemd override |
| `GITHUB_WEBHOOK_SECRET` (GitHub UI) | HMAC-SHA256 | ✅ Webhook #631147476 |

## AI / Router

| Secret Name | Category | Status |
|-------------|----------|--------|
| `DEEPSEEK_API_KEY` | LLM Provider | ✅ goose-cli.env |
| `NSCALE_API_KEY` | Embedding | ✅ `.env.complete` |
| `AI_ROUTER_ADMIN_KEY` | 9Router Auth | 🔴 Blocked (not found) |
| `BRAIN_API_KEY` | Brain Auth | ✅ `.env.complete` + systemd |

## Cloudflare

| Secret Name | Status |
|-------------|--------|
| `CLOUDFLARE_API_TOKEN` | ✅ `.env.complete` + CLI |
| Cloudflare Tunnel Token | ✅ systemd override |

## Supabase

| Secret Name | Status |
|-------------|--------|
| `SUPABASE_SERVICE_ROLE_KEY` | ❌ Fehlt (Pascal: Supabase Dashboard) |
| `SUPABASE_ANON_KEY` | ❌ Fehlt (Pascal: Supabase Dashboard) |
| `SUPABASE_JWT_SECRET` | ❌ Fehlt (Pascal: Supabase Dashboard) |
| `SUPABASE_ACCESS_TOKEN` | ❌ Fehlt (Pascal: Supabase Dashboard) |
| Supabase DB Password | ✅ `.env.complete` |

## Vercel

| Secret Name | Status |
|-------------|--------|
| `VERCEL_TOKEN` | ✅ `.env.complete` |
| Vercel ByPass | ✅ `.env.complete` |

## Revolut

| Secret Name | Status |
|-------------|--------|
| `REVOLUT_SECRET_KEY` | ✅ `.env.complete` |
| `REVOLUT_PUBLIC_KEY` | ✅ `.env.complete` |

## MCP / Agents

| Secret Name | Status |
|-------------|--------|
| `COPILOT_MCP_GITHUB_PAT` | ❌ Fehlt (keine Copilot Lizenz) |

## Missing Secrets Summary

| Secret Name | Required By | Blocker |
|-------------|-------------|---------|
| `SUPABASE_SERVICE_ROLE_KEY` | PM API, Backend | Supabase Dashboard (Pascal) |
| `SUPABASE_ANON_KEY` | Frontend | Supabase Dashboard (Pascal) |
| `SUPABASE_JWT_SECRET` | Auth | Supabase Dashboard (Pascal) |
| `SUPABASE_ACCESS_TOKEN` | API | Supabase Account (Pascal) |
| `GITHUB_APP_ID` | PM API GitHub Client | GitHub UI Settings |
| `GITHUB_APP_INSTALLATION_ID` | PM API GitHub Client | GitHub UI Settings |
| `COPILOT_MCP_GITHUB_PAT` | GitHub Cloud Agent | Copilot Lizenz |
| `AI_ROUTER_ADMIN_KEY` | 9Router Auth | Unknown/not found |

## Registry Location

Central `.env.complete` path: `/opt/nexifyai/creds/.env.complete`
Also mirrored in: systemd override files, goose-cli.env, GitHub Secrets UI (pending)
