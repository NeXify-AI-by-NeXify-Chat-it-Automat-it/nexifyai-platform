# GitHub Custom Properties and Autolinks

## Custom Properties (Target)

| Property | Value | Description |
|----------|-------|-------------|
| `platform_area` | `core-platform` | Role within the platform ecosystem |
| `data_sensitivity` | `internal` | Data classification level |
| `runtime_class` | `production-adjacent` | Runtime environment type |
| `customer_scope` | `core` | Customer impact scope |
| `lifecycle_state` | `active` | Current lifecycle phase |
| `owner` | `nexify-ai` | Team or service owner |
| `compliance_profile` | `standard-plus` | Compliance requirements |
| `ai_agent_access` | `controlled` | Whether AI agents operate here |
| `secret_profile` | `managed-required` | Secret management level |
| `deployment_target` | `vercel-vds-cloudflare` | Deployment destinations |
| `brain_required` | `true` | Whether Brain context is mandatory |
| `project_manager_required` | `true` | Whether PM API integration is mandatory |

**Status**: NOT configurable via API. Requires GitHub Settings → Custom properties (org-level).

## Autolinks (Target)

| Prefix | URL Template | Purpose | Status |
|--------|-------------|---------|--------|
| `NX-` | `https://nexifyai.cloud/tasks/{reference}` | PM Tasks | ❌ URL not yet stable |
| `INC-` | `https://github.com/orgs/NeXify-AI-by-NeXify-Chat-it-Automat-it/issues?q=is:issue+label:incident+{reference}` | Incidents | ❌ Needs policy |
| `VERCEL-` | `https://vercel.com/nexifyai/deployments/{reference}` | Deployments | ❌ URL not yet stable |

**Decision**: Do NOT create Autolinks until URL patterns are stable. Document as future work.
