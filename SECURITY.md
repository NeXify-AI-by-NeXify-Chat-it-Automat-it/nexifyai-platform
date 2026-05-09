# NeXifyAI — Security Policy

**NeXifyAI by NeXify — Chat it. Automate it.**

## Vulnerability Disclosure Policy

NeXifyAI takes the security of our systems seriously. We appreciate responsible disclosure of security vulnerabilities.

### Reporting a Vulnerability

**DO NOT create a public GitHub issue.** Instead, send an encrypted report to:

- **Email:** security@nexifyai.de
- **PGP Key:** [Download PGP Key](https://www.nexify-automate.com/.well-known/security.txt)
- **Fingerprint:** (to be published)

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected component/version
- Potential impact
- Any suggested fixes

### Response Timeline

| Phase | Timeline |
|-------|----------|
| Acknowledgment | Within 24 hours |
| Initial Assessment | Within 72 hours |
| Fix Development | Within 7 days (critical), 30 days (high) |
| Public Disclosure | 90 days after fix, or coordinated |

### Safe Harbor

NeXifyAI will not pursue legal action against researchers who:
- Act in good faith
- Follow responsible disclosure practices
- Avoid data destruction or service disruption
- Do not access or modify user data without permission

## Supported Versions

| Version | Supported |
|---------|-----------|
| main branch | ✅ Active development |
| Latest release | ✅ Full support |
| Older releases | ❌ Upgrade required |

## Security Architecture

- **Zero Trust:** All access requires explicit authorization
- **Defense in Depth:** Multiple governance layers (Brain, Runtime, CI)
- **Least Privilege:** Minimum capabilities per agent
- **Audit Everything:** Every operation logged

## Security Tools

- **Gitleaks:** Secret scanning on every push
- **Trivy:** Container vulnerability scanning (HIGH/CRITICAL blocking)
- **CodeQL:** Code analysis (planned)
- **NPM Audit:** Dependency vulnerability checks (HIGH blocking)
- **Safety:** Python dependency checks
- **Dependabot:** Automated dependency updates

## Prohibited

- GPL/AGPL/SSPL licensed dependencies
- Secrets in source code
- Direct brain writes (bypassing BrainGovernor)
- Unvalidated embeddings
- Unaudited CI/CD flows

## Contact

- **Security Team:** security@nexifyai.de
- **CEO:** Pascal Courbois — p.courbois@icloud.com
- **Legal:** NeXify Automate, KvK NL

Last updated: 2026-05-09
