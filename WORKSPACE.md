# NeXifyAI Platform — Workspace

## Quick Start

```bash
# Backend API
cd services/api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd apps/web
npm install && npm start

# Admin Panel
cd apps/admin-chat
npm install && npm run dev
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for Qdrant + Redis)
- Git LFS (optional, for large files)

## Environment

Copy `.env.example` to each service and configure:

```
OPENROUTER_API_KEY=<key>  # https://openrouter.ai/api/v1 | deepseek/deepseek-v4-flash
SUPABASE_URL=<url>
SUPABASE_SERVICE_KEY=<key>
REDIS_HOST=localhost
REDIS_PORT=6379
INTERNAL_AUTH=<key>
```

## Brain

Local Qdrant at http://localhost:6333
- Collection: `nexifyai_brain` (4096-dim vectors)
- Collection: `nexifyai_memories` (runtime observations)

## Deploy

Platform deploys via GitHub Actions + Vercel (frontend) + VDS (backend).
