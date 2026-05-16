# System 8 — Quality Management & Audit
spec_id: SYS-008 | version: 1.0 | date: 2026-05-15 | owner: senior-quality-auditor

## 1. ZWANGSREGEL
NOTHING goes to production without QA approval. No exceptions.

## 2. SEVEN QUALITY GATES
### GATE 1 — DOCUMENTATION
- [ ] Architecture spec exists + current
- [ ] API docs (endpoints, auth, errors)
- [ ] SOP reference
- [ ] Decision record (why?)

### GATE 2 — TESTING
- [ ] Unit: ≥80% P0, ≥60% P1, ≥40% P2
- [ ] Integration: cross-system verified
- [ ] Security scan: no CVEs
- [ ] Load: handles 2x expected

### GATE 3 — SECURITY
- [ ] Secrets in vault (none in code)
- [ ] No unnecessary open ports
- [ ] Auth on every endpoint
- [ ] Audit log active + immutable

### GATE 4 — ARCHITECTURE
- [ ] Fits 12-System model
- [ ] No duplication
- [ ] No contradictions
- [ ] Scaling plan documented

### GATE 5 — PERFORMANCE
- [ ] API <200ms p95
- [ ] Agent <5s response
- [ ] Container CPU <80%, memory <80%
- [ ] Brain query <500ms

### GATE 6 — WORKFLOW
- [ ] Order exists (SYS-007)
- [ ] Context enriched (Brain)
- [ ] Expert matched correctly
- [ ] Review scheduled

### GATE 7 — AGENT QUALITY
- [ ] Profile ≥4000 chars
- [ ] Brain-First enabled
- [ ] Escalation defined (4 levels)
- [ ] Heartbeat configured

## 3. AUDIT SCORING
PASS (1.0) / WARN (0.5) / FAIL (0.0)
- ≥0.85: APPROVED
- 0.70-0.84: CONDITIONAL
- 0.50-0.69: REJECTED
- <0.50: BLOCKED

## 4. CERTIFICATION
| Tier | Gates | Sustained | P0 Incidents |
|------|-------|-----------|--------------|
| BRONZE | ≥0.70 | 1 week | - |
| SILVER | ≥0.85 | 2 weeks | - |
| GOLD | ≥0.95 | 4 weeks | 0 |
| PLATINUM | GOLD + | 8 weeks auto | 0 |
