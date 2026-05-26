# GitHub Advanced Security Policy

## Push Protection
- **Status**: Target ENABLED
- Blocks commits containing secrets before they reach GitHub.
- Bypass only with documented Business Justification.

## Direct Alert Dismissal Prevention
- **Status**: Target ENABLED  
- Alerts cannot be dismissed without reason comment.
- Manual dismissals audited.

## Secret Scanning
- **Standard patterns**: ON (GitHub-managed)
- **Custom patterns**: To be defined
  - `nexify_*` tokens
  - `NXFY_*` tokens
  - AI router admin keys
  - Internal webhook tokens
  - Cloudflare tunnel token patterns
- **Validity checks**: ON (where provider-supported)
- **Push protection**: ON
- **Generic passwords**: ON (non-provider patterns)

## CodeQL
- **Default Setup**: Active (repository level)
- **Analysis languages**: JavaScript/TypeScript, Python, Actions
- **Schedule**: Push to main, PR to main, weekly
- **Configuration**: `.github/codeql-config.yml` with paths-ignore for tests/archive
- **Threshold**: Code scanning required with at least `errors` and `warnings` at high/critical

## Dependabot
- **Dependabot alerts**: ON
- **Security updates**: Target ON (auto-PR for fixable vulns)
- **Version updates**: via `dependabot.yml` (configured in repo)
- **Malware alerts**: ON
- **Rules**: grouped security updates enabled

## Private Vulnerability Reporting
- **Status**: Target ENABLED
- Allows private disclosure before CVE.

## Dependency Graph
- **Status**: Target ENABLED
- Automatic submission to GitHub.
