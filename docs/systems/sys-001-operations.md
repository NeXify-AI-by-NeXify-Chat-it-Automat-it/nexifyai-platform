# System 1 — Unternehmensbetrieb & Operations
spec_id: SYS-001 | version: 1.0 | date: 2026-05-15 | owner: project-manager

## 1. SCOPE
Enterprise operations: process management, roles, escalation, audit, SLAs, emergency response.

## 2. ESCALATION CHAIN (4 Levels)
| Level | Trigger | Responder | Timeout | Action |
|-------|---------|-----------|---------|--------|
| L1 | Agent timeout/failure | Domain Expert | 5 min | Retry |
| L2 | Expert unavailable/3 fails | Senior QA | 15 min | Reassign |
| L3 | System degradation | CEO | 30 min | Orchestrator hold |
| L4 | Data loss/security breach | ALL STAKEHOLDERS | Immediate | Full stop |

## 3. ROLE MATRIX
| Role | Responsibility | Deputy | Audit Freq |
|------|---------------|--------|------------|
| CEO | Strategic decisions | project-manager | Weekly |
| Domain Expert | System ownership | peer expert | Per execution |
| Senior QA | Quality gates | review-agent | Per deploy |
| Project Manager | Operations oversight | business-analyst | Daily |
| AI-engineer | AI runtime health | monitoring-specialist | Hourly |

## 4. SLA DEFINITIONS
| System | Availability | Response P0 | Response P1 | Response P2 |
|--------|-------------|-------------|-------------|-------------|
| Brain | 99.5% | 5 min | 30 min | 2h |
| Backend API | 99.9% | 5 min | 15 min | 1h |
| Hermes Gateway | 99.5% | 5 min | 30 min | 2h |
| Agent Runtime | 99.0% | 15 min | 1h | 4h |
| Infrastructure | 99.9% | 5 min | 15 min | 1h |

## 5. EMERGENCY RESPONSE
### P0 Declaration Criteria
- Data loss or corruption
- Security breach (unauthorized access)
- >30% system degradation sustained 5+ min
- Brain unavailable >2 min
- Multiple agent failures (3+ simultaneous)

### P0 Response Protocol
1. CEO declares P0 → all agents notified
2. Orchestrator halts all non-P0 tasks
3. security-engineer isolates affected system
4. network-specialist assesses blast radius
5. Root cause identified → fix → verify → document
6. Postmortem within 1 hour (SYS-008 template)

## 6. CONSTRAINT
- NEVER: P0 without postmortem
- NEVER: Role without deputy
- NEVER: Decision without documentation
- ALWAYS: Audit trail for all P0/P1 events
