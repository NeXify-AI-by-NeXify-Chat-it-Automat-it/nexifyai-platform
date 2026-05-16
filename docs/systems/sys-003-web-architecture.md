# System 3 — Web & Platform Architecture
spec_id: SYS-003 | version: 1.0 | date: 2026-05-15 | owner: nextjs-architecture-expert

## 1. PLATFORM STACK
- Frontend: Next.js (Vercel deployment, token: DS_VERCEL_F2F9EC1F__TOKEN)
- Backend: FastAPI (localhost:8001)
- Database: Supabase + MongoDB (DS_SUPABASE_1E93118D + DS_MONGODB_80FC6526)
- Auth: Supabase Auth (JWT) + X-Internal-Auth (internal)
- Email: Resend
- DNS: Cloudflare (DS_CLOUDFLARE_57D167E2)

## 2. PAGE ARCHITECTURE
| Route | Purpose | Auth | Status |
|-------|---------|------|--------|
| / | Landing page | Public | Planned |
| /services | Service overview | Public | Planned |
| /portal | Customer portal | JWT | Planned |
| /admin | Admin dashboard | JWT+Admin | Planned |
| /api/* | API docs | Public | Planned |

## 3. SEO STRUCTURE
- i18n: German primary, English secondary
- Meta: per-page OG tags, structured data
- Performance: <2s LCP, <100ms FID, <0.1 CLS
- Sitemap: auto-generated from routes

## 4. ADMIN SYSTEM
- Role-based: admin, manager, agent, viewer
- Dashboard: system health, agent status, orders, revenue
- Agent management: deploy, configure, score
- Audit: all admin actions logged

## 5. CONSTRAINT
- NEVER: Public admin endpoint without auth
- NEVER: Missing role check on mutation
- NEVER: Direct production database access from frontend
- ALWAYS: CSP headers, HTTPS only, rate limiting
