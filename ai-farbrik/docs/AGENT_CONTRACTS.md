# AI Fabrik — Agent Contracts

## Mandatory Agents

| Agent | Role | Capabilities | Risk Limit |
|-------|------|-------------|-----------|
| AI-CEO | Strategy + Prioritization | brain.ceo | 0.0 |
| AI-Brain-Governor | Brain protection | brain.governance | 0.0 |
| AI-Governance | Policies + Approvals | governance.* | 0.0 |
| AI-Reconciliation | Conflict resolution | brain.reconcile | 0.05 |
| AI-Auditor | Truth verification | brain.audit | 0.0 |
| AI-Architect | System architecture | dos, adr | 0.05 |
| AI-Delivery | Deployments | vercel.write, github.write | 0.10 |
| AI-QA | Quality validation | browser, pytest, jest | 0.05 |
| AI-Knowledge | Knowledge structuring | brain.write, embeddings | 0.05 |
| AI-Identity | Cross-channel identity | identity.* | 0.0 |

## Agent Contract Schema

Every agent MUST declare:

```yaml
agent_id: ai-ceo
domain: executive
version: 1.0.0

capabilities:
  - brain.ceo
  - governance.*

risk:
  max_blast_radius: 0
  requires_human_approval: false

tools:
  - brain_search
  - governance_kernel

contract:
  - No direct brain writes
  - All decisions audited
  - Strategy changes versioned

compensation:
  - Strategy rollback via ADR
```

## Prohibited

- Agents with full access (brain.ceo only for AI-CEO)
- Autonomous self-modification
- Ungoverned tool access
- Direct production deployments (preview first)
- Unaudited runtime decisions
- Parallel conflicting agents
