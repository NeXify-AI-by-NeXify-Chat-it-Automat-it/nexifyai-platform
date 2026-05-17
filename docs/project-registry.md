# NeXifyAI — Kundenprojekt-Registry

> Stand: 2026-05-17 | Autopilot Phase 0-5
> Brain API v2 on :8420 | Cogn. Runtime on :8000 | Hermes on :8642

---

## Übersicht

| Projekt | Typ | Port | Status | Git | Stack |
|---------|-----|------|--------|-----|-------|
| NexifyAI Platform | Eigen | :8420, :8000, :8642 | ✅ | github.com/nexifyai-dev/nexifyai-platform | FastAPI + Python + Qdrant + Temporal |
| Studienkolleg Aachen | Kunde | :8010 | ✅ | github.com/nexifyai-dev/studienkolleg-aachen | Express + React |
| Affilinet Portal | Kunde | :8020 | ✅ | github.com/nexifyai-dev/affilinet-portal | Express + Prisma/Neon |
| OpenCarBox | Kunde | :8030 | ✅ | GitLab (s. u.) | Express + React |

---

## 1. 🎓 Studienkolleg Aachen

**Git**: `nexifyai-dev/studienkolleg-aachen`
**Deployment**: `/opt/nexifyai/studienkolleg/server.js`
**Source**: `/opt/nexifyai-backend/studienkolleg-aachen/`
**PM2**: id 3 (nach CWD-Fix), port 8010
**Health**: `GET /api/health` → ok
**Uptime**: neugestartet nach CWD-Fix, zuvor 4 Tage stabil

### Stack
- **Server**: Express (Node.js 22)
- **Frontend**: React SPA (Vite + Tailwind) in `frontend/`
- **Backend**: Express + Routen in `backend/routers/`
- **Doku**: 20+ MD-Dokumente (Architektur, Tech-Stack, QA, Rollen...)

### Features
- AI-gestütztes Studierendenscreening
- eVidence-Handling
- Admin/Staff-Shell
- i18n (DE/EN)
- QR-Codes + Formular-Engine

### History
- 2026-04-25: Erstes PM2-Deployment (falscher CWD)
- 2026-05-13: Letzter Git-Commit `a19cd72`
- 2026-05-17: CWD gefixt von opencarbox → studienkolleg

---

## 2. 🔗 Affilinet Portal

**Git**: `nexifyai-dev/affilinet-portal`
**Deployment**: `/opt/nexifyai/affilinet/server.js`
**Source**: `/opt/affilinet-portal/`
**PM2**: id 4, port 8020
**Health**: `GET /api/health` → ok

### Stack
- **Server**: Express (Node.js 22)
- **ORM**: Prisma (PostgreSQL via Neon Serverless)
- **Frontend**: React
- **Infra**: Docker + Vercel + Neon konfiguriert

### History
- 2026-04-25: PM2-Deployment
- 2026-05-17: CWD gefixt
- Drift: Source hat Prisma/Full-Stack, Deployment nur Express-Static

---

## 3. 🚗 OpenCarBox

**Git**: GitLab (`.gitlab-ci.yml` vorhanden, kein GitHub Mirror)
**Deployment**: `/opt/nexifyai/opencarbox/server.js`
**Source**: `/opt/nexifyai/opencarbox/`
**PM2**: id 5, port 8030
**Health**: `GET /api/health` → ok

### Stack
- Express + backend/ + frontend/ + tests/
- CI/CD via GitLab

---

## 4. 🧠 NeXifyAI Platform (Eigen)

**Git**: `nexifyai-dev/nexifyai-platform`
**Deployment**: Systemd (26 Services), Docker (16 Container), PM2 (1)
**Source**: `/opt/nexifyai-platform/` + `/runtime/` + `/systemmaster/`

### Kernkomponenten
- Cognitive Runtime: 32 Module (MCP, Events, Planner, Reasoning)
- Brain: 14 Collections, 12.997 Points
- Brain API v2: Port 8420 (neu)
- Temporal Workers: 5 Worker
- Event Bus: 2 Prozesse
- Bots: Admin, Support, WhatsApp, Email, GitHub

### Git-Struktur (nach Autopilot Sync)
```
nexifyai-platform/
├── apps/              # React SPA + Next.js Admin
├── services/          # FastAPI + Temporal
├── runtime/           # 32 Module (Phase 0 Sync) ← NEU
├── systemmaster/      # 14 Dienste (Phase 0 Sync) ← NEU
├── governance/        # Bootstrap + CB + DLQ
├── infrastructure/    # Docker + Supabase + Vercel
├── knowledge/         # Brain-Schemas + Emergent
├── docs/              # Architektur + Legal + Registry
└── brain/             # Operations Memory
```

---

## Port-Übersicht

| Port | Service | Projekt |
|------|---------|---------|
| 80 | Traefik HTTP | Plattform |
| 443 | Traefik HTTPS | Plattform |
| 3001 | Uptime-Kuma | Monitoring |
| 47334 | MindsDB | Data/ML |
| 6333 | Qdrant Brain | Plattform |
| 6379 | Redis | Plattform |
| 7233 | Temporal | Plattform |
| 8000 | Mem0 API | Plattform |
| **8010** | **Studienkolleg** | **🎓 Kunde** |
| **8020** | **Affilinet** | **🔗 Kunde** |
| **8030** | **OpenCarBox** | **🚗 Kunde** |
| 8080 | Traefik Dashboard | Plattform |
| **8420** | **Brain API v2** | **Neu** |
| 8642 | Hermes Gateway | Plattform |
| 9001 | WhatsApp | Plattform |

---

## Brain-Zustand

| Collection | Points |
|------------|--------|
| nexifyai_brain | 12.997 |
| nexifyai_memories | 5.852 |
| company_brain | 13 |
| 11 weitere | 0 |

### Wichtige Kategorien
```
live_monitoring  435   governance     18   system_state    10
infrastructure     6   architecture    5   knowledge_base   4
quality            3   runtime         2   agent_profile    2
mission_statement  1   legal           1   market_intel     1
```

---

## Nächste Schritte

1. **OpenCarBox**: GitLab → GitHub oder GitLab-PAT hinterlegen
2. **Affilinet**: Prisma/Neon-Backend deployen (nicht nur Static)
3. **Studienkolleg**: Frontend-Build automatisieren
4. **Legal**: Impressum/DSGVO auf nexifyai.cloud deployen
5. **Portal**: apps/web über Vercel deployen
6. **Temporal**: Worker-Pfad migrieren (alt → neu)
7. **Monitoring**: Kunden-Ports via Traefik routen
