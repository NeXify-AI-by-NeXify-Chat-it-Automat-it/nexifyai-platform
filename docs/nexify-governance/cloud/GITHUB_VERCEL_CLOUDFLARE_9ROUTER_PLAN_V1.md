# GitHub / Vercel / Cloudflare / 9Router Plan V1

**Status:** V1 — 2026-06-10
**Owner:** Team 09 — DevOps / Cloud / Live / GitHub / Deployment
**Geltungsbereich:** Externe Infrastruktur und Deployment-Ziele

## GitHub

| Aspekt | Ziel |
|--------|------|
| Repo | https://github.com/NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform.git |
| Master Registry | Alle Repos zentral registriert |
| Branch-Strategie | feature/ → main, PR-basiert |
| Issues | Autonome Erfassung aus Tasks |
| Actions | CI/CD für Tests, Lint, Deploy |
| Security | CodeQL, Dependabot, Secret Scanning |
| GitHub App | Für automatisierte Operationen |
| Push/Merge | Nur mit Pascal-Freigabe |

## Vercel

| Aspekt | Ziel |
|--------|------|
| Website | nexifyai.cloud und www.nexifyai.cloud |
| SSL | Automatisch via Vercel |
| Umgebungen | Preview/Production getrennt |
| Domain-Änderungen | Nur mit Pascal-Freigabe |

## Cloudflare

| Aspekt | Ziel |
|--------|------|
| Workstation | Über Tunnel (auth-geschützt) |
| Brain | Über Tunnel (auth-geschützt) |
| 9Router | Über Tunnel (auth-geschützt) |
| Website | Vercel (nicht Tunnel) |
| Mail-DNS | DNS-only prüfen |
| SPF/DKIM/DMARC | Erst nach Freigabe ändern |
| Tunnel-Änderungen | Nur mit Pascal-Freigabe |

## 9Router

| Aspekt | Ziel |
|--------|------|
| Zielroute | ai-router.nexifyai.cloud/v1 |
| Standardmodell | nexifyai-standard-llm (deepseek-v4-flash + deepseek-reasoner) |
| Pro/Max | Nur Ausnahme |
| DeepSeek-401 | Dokumentieren, Zielroute vorbereiten |
| Hermes-soll | Nicht direkt auf invaliden DeepSeek-Key laufen |
| Integration | 9Router als NeXify AI Router-Zentrale in Workstation |

## Aktuelle Blocker

- **Git Push/Merge** → WAITING_FOR_APPROVAL (gh CLI nicht installiert)
- **DNS/Cloudflare/Vercel Änderungen** → WAITING_FOR_APPROVAL
- **Secrets/Provider Keys** → WAITING_FOR_APPROVAL
- **SimpleX Outbound** → BLOCKED_APPROVAL
- **VDS/gh Livezugriff** → BLOCKED_ACCESS
