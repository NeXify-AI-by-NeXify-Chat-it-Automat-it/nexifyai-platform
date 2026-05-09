# NeXifyAI — License Compliance Policy

**Document:** docs/policies/license-policy.md
**Version:** 1.0.0
**Last Updated:** 2026-05-09
**Authority:** DOS v2.1 Kap. 14 — OSS-Konformität

## Policy Statement

NeXifyAI is a proprietary software company. All NeXifyAI core code is proprietary.
Third-party open-source dependencies must comply with this policy.

## Prohibited Licenses

The following licenses are **STRICTLY PROHIBITED** for any dependency:

| License | Reason |
|---------|--------|
| GPL (all versions) | Copyleft — forces derivative works to be open-source |
| AGPL (all versions) | Network copyleft — applies to SaaS usage |
| SSPL | Server Side Public License — requires release of all service code |
| EUPL | European Union Public License — strong copyleft |
| CC-BY-SA | ShareAlike — copyleft for documentation |
| OSL | Open Software License — patent retaliation |

## Allowed Licenses

The following licenses are **PERMITTED**:

### Permissive (Preferred)
- MIT
- Apache 2.0
- BSD (2-Clause, 3-Clause)
- ISC
- Unlicense / CC0

### Weak Copyleft (Conditional Approval)
- LGPL (runtime linking only, no static linking)
- MPL 2.0 (file-level copyleft acceptable)
- CDDL (only if no alternative exists)

### Commercial
- Proprietary licenses with valid commercial agreement
- NeXifyAI internal code (all rights reserved)

## Audit Process

### Pre-Commit Check

Every dependency addition MUST pass:
1. `license-check` in CI (security-dependencies.yml)
2. Manual review for prohibited licenses
3. Documentation in LICENSE-3RD-PARTY.md

### CI Enforcement

```yaml
# Security dependencies workflow checks:
- NPM license audit
- Python license check (pip-licenses)
- Blocked: GPL, AGPL, SSPL (exit code 1)
```

### Remediation

If a prohibited dependency is found:
1. **Immediately:** Open P1 Issue
2. **Within 24h:** Find alternative with permissible license
3. **Within 72h:** Replace dependency
4. **Blocking:** No merge until resolved

## Current Approved Dependencies

### Frontend (npm)
- React (MIT)
- Next.js (MIT)
- Tailwind CSS (MIT)
- Supabase JS Client (MIT)
- All dependencies audited via `npm audit`

### Backend (pip)
- FastAPI (MIT)
- SQLAlchemy (MIT)
- httpx (BSD)
- Pydantic (MIT)
- All dependencies audited via `safety check`

## Exceptions

Exceptions require:
1. Written justification (business case)
2. Legal review
3. CEO approval (Pascal Courbois)
4. Documented in ADR

No exceptions granted to date.

## Reporting

- **License violations:** security@nexifyai.de
- **Questions:** Refer to [SECURITY.md](../SECURITY.md)

## References

- [DOS v2.1 Kap. 14 — Security](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/blob/main/docs/DOS-v2.0.md)
- [SECURITY.md](../SECURITY.md)
- [public/security.txt](../public/security.txt)
