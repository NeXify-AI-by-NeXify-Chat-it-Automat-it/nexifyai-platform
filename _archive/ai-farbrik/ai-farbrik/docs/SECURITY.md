# AI Fabrik — Security

## Principles

- Zero Trust: No implicit access
- Defense in Depth: Multiple governance layers
- Least Privilege: Minimum capabilities per agent
- Audit Everything: Every operation logged
- Immutable Logs: Append-only, signed

## Secrets Management

- All secrets in environment variables (never in code)
- Vault integration planned
- Short-lived credentials preferred
- Rotation required for long-lived tokens

## Supply Chain

- SBOM generation (CycloneDX)
- Trivy container scanning
- Gitleaks secret detection
- Dependabot dependency updates
- No GPL/AGPL/SSPL dependencies

## Storage

- Encryption at rest (brain.db via filesystem)
- Encryption in transit (HTTPS for all APIs)
- Signed artifacts (future: Sigstore)
- Immutable snapshots (future: append-only ledger)

## Identity

- Workload identity per agent
- Service identity per connector
- Short-lived capability tokens

## Prohibited

- Direct brain writes (bypassing BrainGovernor)
- Unvalidated embeddings
- Unstructured memories
- Full-access agents
- Parallel truths (conflicting memories)
- Unaudited CI/CD flows
- Non-versioned prompt changes
