# AI Fabrik — Governance

## Governance Pipeline

Every operation flows through:

```
Capability Check → Risk Assessment → Blast Radius → Policy → Approval
```

## Access Levels (Brain)

| Level | Read | Write |
|-------|------|-------|
| PUBLIC | Anyone | ATTRIBUTED (source required) |
| AGENT | Authenticated agents | ATTRIBUTED |
| GOVERNED | Capability token required | GOVERNED (capability-gated) |
| RESTRICTED | Explicit approval | CORROBORATED (multi-source) |
| CEO_ONLY | Pascal only | GOVERNED |

## Risk Classification

| Risk | Examples | Auto-Approval |
|------|----------|--------------|
| LOW | CREATE INDEX, ADD COLUMN nullable | Yes |
| MEDIUM | ALTER TABLE, CREATE POLICY | Yes |
| HIGH | DROP COLUMN, ALTER TYPE | No (human) |
| CRITICAL | DROP TABLE, TRUNCATE | No (human) |

## Mandatory Policies

1. **No Stripe** — Revolut only
2. **No GPL/AGPL/SSPL** — License compliance
3. **RLS Required** — All Supabase writes must have RLS
4. **Blast Radius Cap** — Maximum 3 downstream systems
5. **Source Attribution** — Every brain write must declare source
6. **No Unvalidated Embeddings** — Min confidence 0.3

## Capability Tokens

| Token | Scope |
|-------|-------|
| github.read | * |
| github.write | repo:nexifyai-dev/* |
| vercel.read | project:frontend |
| vercel.write | project:frontend |
| supabase.read | database:* |
| supabase.write | database:* |
| brain.read | * |
| brain.write | category-gated |
| brain.ceo | * (full access) |

## Audit

Every brain operation is logged (brain_audit.db):
- Who accessed what, when
- Approval/denial with reason
- Capability used
- Full traceability
