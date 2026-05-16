# System 2 — Agenturstruktur & CRM
spec_id: SYS-002 | version: 1.0 | date: 2026-05-15 | owner: crm-automation-specialist

## 1. CRM ARCHITECTURE
- Backend: Supabase (connected: DS_SUPABASE_1E93118D)
- Auth: JWT via Supabase Auth
- Portal: Next.js frontend (System 3)
- Integration: Hermes Gateway for AI-automated actions

## 2. CUSTOMER PORTAL
| Feature | Status | Priority |
|---------|--------|----------|
| Dashboard (project overview) | Planned | P1 |
| Ticket system | Planned | P1 |
| Communication history | Planned | P2 |
| Invoicing | Planned | P2 |
| SLA tracking | Planned | P1 |

## 3. TICKETING SYSTEM
```
TICKET_CREATED → TRIAGE → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
                      ↓                     ↓
                   REJECTED             ESCALATED → CEO
```
Priority: P0-P3 mapped to System 7 routing matrix.

## 4. COMMUNICATION PIPELINE
- Email: Resend API (DS_RESEND_443B8456, sender: DS_RESEND_443B8456__SENDER_EMAIL)
- Internal: Hermes Gateway agent dispatch
- Client-facing: Portal messaging
- Emergency: Direct CEO notification

## 5. SLA SYSTEM
| Tier | Response | Resolution | Support Hours |
|------|----------|------------|---------------|
| Enterprise | 15 min | 4h | 24/7 |
| Business | 1h | 8h | Business hours |
| Starter | 4h | 24h | Business hours |

## 6. CONSTRAINT
- NEVER: Client data in plain text logs
- NEVER: Ticket without priority assessment
- NEVER: Communication without audit trail
