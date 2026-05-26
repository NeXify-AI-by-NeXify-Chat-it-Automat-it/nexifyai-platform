# NeXifyAI — Autonomous GitHub Operations Policy
> Owner: NeXifyAI Platform Team | Standard: DOS v2.0 | Updated: 2026-05-24
> See also: `docs/agency/DOS_AUTONOMOUS_EXECUTION_POLICY.md`

## What Goose MAY Do Autonomously

### Repository Operations
- ✅ Create feature/chore/fix branches from main
- ✅ Commit changes with descriptive conventional commit messages
- ✅ Push branches to origin
- ✅ Create Pull Requests with full description and evidence
- ✅ Set labels on issues and PRs
- ✅ Post comments on PRs and issues (not exposing secrets)
- ✅ Create issues (redacted, no secret values)
- ✅ Update Brain with new knowledge
- ✅ Update DOS/Learning/Prevention documents

### Autonomous Merge Allowed When ALL conditions met:
1. PR is docs/governance/ci/dependabot-safe only
2. No secrets in diff
3. All required CI checks pass (green)
4. Diff reviewed and understood
5. No production code changed
6. Brain update performed (if rule change)
7. Labels set correctly
8. Merge method: squash or merge (no rebase that rewrites history)

### Dependabot PRs Auto-Mergeable
- GitHub Actions version bumps (minor/patch)
- Non-production dev dependency patches
- Condition: CI green + no breaking change indicators

## What Goose MUST NOT Do Autonomously

### Hard Limits — Never Without Human Approval
- ❌ Push directly to main branch
- ❌ Bypass branch protection rules
- ❌ Output secret values in any context
- ❌ Rotate secrets when external UI/API access is required
- ❌ Close CodeQL/Security alerts without rotation evidence
- ❌ Mark security incidents as resolved without confirmation
- ❌ Run database migrations in production
- ❌ Change Supabase RLS policies without review
- ❌ Modify billing/auth/payment code without review
- ❌ Delete files outside docs/agency without governance decision
- ❌ Copy customer project code without clean-reuse assessment
- ❌ Stop or restart production services on VDS

## Decision Tree — Merge or Not

```
PR ready to merge?
  │
  ├─ Contains secrets? → NO → STOP, human required
  ├─ Touches production code? → YES → STOP, human required
  ├─ CI checks green? → NO → WAIT or STOP
  ├─ Diff reviewed? → NO → Review first
  ├─ Labels set? → NO → Set labels first
  │
  └─ ALL CHECKS PASS → Merge autonomously ✅
       └─ Post merge → Brain update + DOS/Learning if rule changed
```

## When Uncertain
- Create PR with label `needs-triage`
- Post analysis comment
- DO NOT merge
- Flag for human review

## Audit Trail
Every autonomous merge must leave:
- Commit hash in Brain (category: autonomous-merge-log)
- PR URL in Brain
- Diff summary
- Evidence of CI pass
