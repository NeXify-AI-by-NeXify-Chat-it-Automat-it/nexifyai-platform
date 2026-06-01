# System 6 — Infrastructure & Network Architecture
spec_id: SYS-006 | version: 1.1 | date: 2026-05-23 | owner: network-specialist
RACI: see docs/governance/raci.yaml#infrastruktur (R/A: devops)

## 1. INFRASTRUCTURE MAP
```
INTERNET → Cloudflare (DNS, SSL) → VPS (mail.nexifyai.cloud)
                                          │
    ┌─────────────────────────────────────┤
    │  Docker Host                         │
    │  ├── nexifyai-qdrant (0.0.0.0:6333)   ← Brain Primary (⚠️ fixed from 127.0.0.1)
    │  ├── Qdrant-vjfp (qdrant-vjfp-qdrant-1:6333) ← Container-Fallback
    │  ├── Traefik (disabled, replaced by Nginx)
    │  ├── Nginx (80/443 → Backend)        ← SSL Termination
    │  ├── Hermes Gateway (:8642, systemd)
    │  └── 10 containers total (all healthy)
    │
    ├── Backend (systemd, :8001)
    │   ├── FastAPI + Uvicorn
    │   ├── OpenRouter (NeXify v4 Pro)
    │   ├── MongoDB (connected)
    │   └── MCP Router (/mcp/rpc)
    │
    ├── Agents (systemd timers)
    │   ├── CEO Timer (5min)
    │   ├── Orchestrator Timer (5min)
    │   ├── Monitor Timer (1min)
    │   └── Gardener Timer (30min)
    │
    └── External
        ├── Vercel (Frontend deployment)
        ├── Supabase (Database)
        ├── GitHub (Code, CI/CD)
        ├── Cloudflare (DNS, SSL)
        └── Resend (Email)
```

## 2. DNS ZONES
| Domain | Target | SSL |
|--------|--------|-----|
| nexifyai.cloud | VPS IP | Let's Encrypt (89d) |
| hermes.nexifyai.cloud | VPS IP | Let's Encrypt (89d) |
| qdrant.nexifyai.cloud | VPS IP | Let's Encrypt (89d) |
| api.nexifyai.cloud | VPS IP | Let's Encrypt (89d) |
| *.nexifyai.cloud | VPS IP | Let's Encrypt (89d) |
| 8/8 certificates >88d validity | | |

## 3. SSL MONITORING
- Let's Encrypt via Nginx (certbot)
- Renewal: auto-renew at 30d remaining
- Check: daily cron, alert if <14d
- All certs currently 89d remaining ✅

## 4. CONTAINER HEALTH
| Container | Status | Uptime |
|-----------|--------|--------|
| nexifyai-qdrant | ✅ | 37h |
| mindsdb-pfoz-mindsdb-1 | ✅ | 37h |
| 8 others | ✅ | 37h |
| 10/10 healthy | | |

## 5. SECURITY POSTURE
- Ports open: 22 (SSH), 80, 443, 8642 (Gateway)
- Legacy Qdrant port 32769: CLOSED (decommissioned)
- Firewall: iptables (Docker managed)
- SSH: key-only, no password
- Pending: SIEM/IDS (System 9)

## 6. REDUNDANCY
- Single VPS (mail.nexifyai.cloud) — no failover yet
- Brain: single Qdrant instance — no replication
- Recommendation: Cloud Qdrant (qdrant.nexifyai.cloud) as mirror
