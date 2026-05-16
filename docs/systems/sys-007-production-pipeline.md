# System 7 — Order & Production Pipeline
spec_id: SYS-007 | version: 1.0 | date: 2026-05-15 | owner: order-workflow-specialist

## 1. PIPELINE FLOW
```
Problem → Order → Prioritize → Context → Expert → Execute → Review → Rework → Approve → Document → Monitor
  ↑                                                                                              │
  └──────────────────────────────── FEEDBACK LOOP ──────────────────────────────────────────────┘
```

## 2. ORDER LIFECYCLE
```
CREATED → PRIORITIZED → ASSIGNED → IN_PROGRESS → REVIEW → APPROVED → ARCHIVED
                                    ↓              ↓          ↓
                                 BLOCKED        REJECTED → REWORK → IN_PROGRESS
```

### State Transitions (logged + immutable)
| From | To | Trigger | Actor |
|------|----|---------|-------|
| CREATED | PRIORITIZED | Priority assessed | CEO / auto |
| PRIORITIZED | ASSIGNED | Expert matched | order-workflow |
| ASSIGNED | IN_PROGRESS | Agent accepts | Agent |
| IN_PROGRESS | REVIEW | Agent completes | Agent |
| REVIEW | APPROVED | QA passes | senior-quality-auditor |
| REVIEW | REJECTED | QA fails | senior-quality-auditor |
| REJECTED | REWORK | Feedback provided | Agent |
| IN_PROGRESS | BLOCKED | Dependency unavailable | Agent |

## 3. PRIORITY MATRIX
| Priority | Execute | Review | Timeout | Escalate |
|----------|---------|--------|---------|----------|
| P0 | CEO+Expert | CEO | 15min | Immediate all-hands |
| P1 | Expert | Senior QA | 60min | CEO after 3 fails |
| P2 | Expert (auto) | Review Agent | 4h | Project Manager |
| P3 | Scheduled | Review Agent | 24h | Never |

## 4. CONTEXT ENRICHMENT
Before assignment, every order gets:
- Brain semantic search (Qdrant: nexifyai_brain)
- Agent capability match + current load
- Related orders + past solutions
- System health status

## 5. QUALITY GATE INTEGRATION (7 Gates)
See SYS-008 for full gate specs. Every order passes through all 7.
BLOCK if: missing doc, missing tests, security gaps, architecture conflicts,
         performance degradation, workflow gaps, agent quality issues.

## 6. VERBOTEN (Automatic Blockers)
- NO direct execution without order
- NO completion without quality gate
- NO deployment without full documentation
- NO task forgotten (every order tracked to closure)
