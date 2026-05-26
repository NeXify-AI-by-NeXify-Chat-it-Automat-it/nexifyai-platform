# NeXifyAI — Required GitHub Labels
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24
> Sync via: `scripts/github/sync-labels.sh`

## Label Registry

### Governance
| Label | Color | Description |
|---|---|---|
| governance | #0075ca | DOS/Governance policy changes |
| dos | #0075ca | DOS standard document |
| resource-first | #0075ca | Resource-first principle applied |
| clean-reuse | #0075ca | Clean reuse pattern |
| documentation | #0075ca | Documentation changes only |
| adr | #0075ca | Architecture Decision Record |
| learning | #0075ca | Learning/lessons-learned update |
| prevention-rule | #0075ca | Prevention rule added or updated |

### Security
| Label | Color | Description |
|---|---|---|
| security | #d93f0b | Security-relevant change |
| security:critical | #b60205 | Critical security issue |
| security:high | #d93f0b | High severity security issue |
| security:medium | #e4e669 | Medium severity security issue |
| security:low | #0e8a16 | Low severity security issue |
| secret-leak | #b60205 | Secret or token exposure |
| codeql | #d93f0b | CodeQL alert related |
| dependabot | #0075ca | Dependabot update |
| vulnerability | #d93f0b | Known vulnerability |

### CI/CD
| Label | Color | Description |
|---|---|---|
| ci | #e4e669 | CI/CD pipeline change |
| github-actions | #e4e669 | GitHub Actions workflow |
| deployment | #e4e669 | Deployment configuration |
| vercel | #e4e669 | Vercel deployment related |
| legacy-cline | #cccccc | Legacy Cline system (dead) |
| docs-only | #0075ca | Documentation-only change, no deploy |

### Work Type
| Label | Color | Description |
|---|---|---|
| bug | #d73a4a | Bug fix |
| enhancement | #a2eeef | New feature or improvement |
| chore | #e4e669 | Maintenance task |
| refactor | #a2eeef | Code refactor |
| cleanup | #e4e669 | Code cleanup |
| audit | #d93f0b | Security or compliance audit |
| needs-triage | #ededed | Requires classification |
| blocked | #d73a4a | Blocked by dependency |
| ready-for-review | #0e8a16 | Ready for human review |

### Contributor
| Label | Color | Description |
|---|---|---|
| good first issue | #7057ff | Good for newcomers |
| help wanted | #008672 | Extra attention needed |

### Platform
| Label | Color | Description |
|---|---|---|
| frontend | #1d76db | Frontend / React |
| backend | #1d76db | Backend / FastAPI |
| fullstack | #1d76db | Full-stack change |
| supabase | #1d76db | Supabase related |
| vercel | #e4e669 | Vercel related |
| cloudflare | #1d76db | Cloudflare related |
| docker | #1d76db | Docker/container |
| brain | #5319e7 | Enterprise Brain system |
| 9router | #5319e7 | 9Router LLM gateway |
| goose | #5319e7 | Goose AI agent |

### Project Type
| Label | Color | Description |
|---|---|---|
| customer-project | #b60205 | Customer project — handle carefully |
| core-platform | #0075ca | Core NeXifyAI platform |
| legacy | #cccccc | Legacy system |
| shadow-system | #cccccc | Unapproved shadow system |

## Sync Instructions
```bash
# Requires: gh auth login
bash scripts/github/sync-labels.sh
```
