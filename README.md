# NeXifyAI Website — nexify-automate.com

Offizielle Website von [NeXifyAI by NeXify](https://nexify-automate.com) — Chat it. Automate it.

**Stack:** React 18 SPA (Frontend) + FastAPI (Backend) + Vercel (Hosting) + OpenRouter (LLM)

**Production:** [nexify-automate.com](https://nexify-automate.com)  
**Preview:** Vercel Preview Deploys via `npx vercel`  
**Backend:** [contract-os.preview.emergentagent.com](https://contract-os.preview.emergentagent.com)

## 📊 NeXifyAI System Health

| Workflow | Status |
|---|---|
| Security Scan | [![Security Scan](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/security-scan.yml/badge.svg?branch=main&event=push)](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/security-scan.yml) |
| CI Quality Gates | [![CI](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/ci.yml) |
| Tests | [![Tests](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/test.yml) |
| Vercel Deploy | [![Vercel](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/deploy.yml/badge.svg?branch=main&event=push)](https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/deploy.yml) |

**Entwicklung:**
```bash
cd frontend && npm install && npm start     # Frontend (localhost:3000)
cd backend && uvicorn server:app --reload   # Backend (localhost:8000)
```
