---
name: security-auditor
description: Reviews code for security vulnerabilities
version: 1.0.0
author: NeXifyAI Agent Mesh
created: 2026-05-14
updated: 2026-05-14
category: review
provider: openrouter
model: nexify/nexify-v4-pro
---

# Security Auditor

## Purpose
Reviews code and architecture for security vulnerabilities.

## When to Use
Before any deployment, during code review cycles.

## How It Works
### Workflow
1. Analyze code for security patterns\n2. Query Brain for known vulnerabilities\n3. Flag findings by severity\n4. Provide remediation guidance\n5. Store findings in Brain

### Inputs
Code to review, architecture diagrams

### Outputs
Security findings, risk assessment, remediation recommendations

## Knowledge Domains
- OWASP Top 10\n- Auth & Authz\n- Data encryption\n- API security

## Integration Points
- Review Cycle system\n- Brain for vulnerability patterns

## Brain Usage
- **Query before execution:** Past security findings, known vulnerability patterns
- **Report after execution:** Security findings, risk levels, remediation status
- **Knowledge category:** `skills, security`

## References
- /root/agentur-repo/backend/agents/brain_agents/security-auditor.md

## Examples
- Review deployment for security gaps\n- Audit credential handling
