# Skill-/MCP-/Tool-Routing-Matrix V1

**Status:** V1 — 2026-06-10
**Owner:** Team 06 — Skills / MCP / Tooling
**Geltungsbereich:** Routing von Skills, MCPs und Tools zu Teams und Agenten

## Grundsatz

Skill-first. Prozess-Skills vor Implementation-Skills. Vor jeder Aktion Skills prüfen und laden.

## Team-Routing

| Team | Primäre Skills | MCPs | Tools/CLIs |
|------|---------------|------|------------|
| 01 CEO | nexify-ceo-orchestrator, nexify-research | — | Alle READ |
| 02 Context | nexify-ideation, nexify-complex-execution | Brain, Filesystem | search_files, read_file |
| 03 Auto/User-Chat | nexify-workflow-automation, nexify-core-operations | Filesystem WRITE_INTERNAL | terminal, cronjob |
| 04 Kanban | nexify-kanban | Filesystem WRITE_INTERNAL | todo, kanban |
| 05 Brain | nexify-data-preparation | Brain, Qdrant, agentmemory | memory, brain-api |
| 06 Skills/MCP | nexify-sop-creator | Skill/MCP Registry | skill_view, skill_manage |
| 07 UI/CI | nexify-project-development | Filesystem, Vercel READ | terminal, git |
| 08 9Router | nexify-core-operations | 9Router READ/PLAN | curl, api |
| 09 DevOps | nexify-github-operations | GitHub READ/PLAN, Vercel READ/PLAN, Cloudflare READ/PLAN | gh, git, vercel, wrangler |
| 10 Security | nexify-quality-assurance | Alle READ | policy-gate, secret-scan |
| 11 Customer | (CRM-Skills) | Resend DRAFT | — |
| 12 QR | nexify-quality-assurance | ALL_READ, Evidence WRITE | review, evidence |

## MCP-Rechte

| MCP | Standard-Recht | Gate bei |
|-----|----------------|----------|
| Filesystem | WRITE_INTERNAL | Destruktive Löschung |
| GitHub | READ/PLAN | Push/Merge/Release |
| Vercel | READ/PLAN | Environment/Domain/Deploy |
| Cloudflare | READ/PLAN | DNS/Tunnel/Proxy |
| Supabase | READ/PLAN | Produktive Daten/Schema |
| Brain | STORE_SUMMARY/PENDING | Sensitive Daten |
| agentmemory | WRITE_INTERNAL | Secrets |
| 9Router | READ/PLAN/TEST | Live-Provider/Secret |
| Resend | DRAFT | Send |
| SimpleX | INBOUND/LOCAL | Outbound/Public |

## Skill-Priorität

1. Prozess-Skills (Planung, Debugging, Review, Audit)
2. Implementation-Skills (Frontend, Backend, Deployment)
3. Domain-Skills (Karpathy, Research, Customer)
