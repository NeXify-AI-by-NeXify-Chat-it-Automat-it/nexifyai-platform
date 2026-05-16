# System 9 — Security Operations
spec_id: SYS-009 | version: 1.0 | date: 2026-05-15 | owner: security-engineer

## 1. SECURITY ARCHITECTURE
```
Internet → Cloudflare WAF → Nginx (SSL) → Backend (:8001)
                                              │
                    ┌─────────────────────────┤
                    │ Auth Layer               │
                    │ ├── JWT (Supabase)       │
                    │ ├── X-Internal-Auth      │
                    │ └── API Keys (MCP)       │
                    ├── RBAC                    │
                    │   ├── admin              │
                    │   ├── manager            │
                    │   ├── agent              │
                    │   └── viewer             │
                    └── Audit Log (Brain)      │
```

## 2. SECRET MANAGEMENT
- All 16 credential sets in Data Vault
- Never in code, never in logs, never in chat
- Rotated: manual for now, auto-rotation target Q3
- Access: only via DS_<SLUG>__<FIELD> env vars

## 3. ZERO TRUST PRINCIPLES
- No internal network assumed safe
- Every endpoint authenticated
- Least privilege enforced
- All access logged

## 4. THREAT DETECTION (Planned)
- SIEM: Wazuh or Graylog (target Q2)
- IDS: OSSEC file integrity monitoring
- Alerting: Prometheus → Uptime Kuma webhook
- Response: Playbook per threat type

## 5. INCIDENT RESPONSE
| Threat | Detection | Containment | Recovery | Postmortem |
|--------|-----------|-------------|----------|------------|
| Unauthorized access | Auth failure spike | Block IP, rotate keys | Audit trail | Within 1h |
| Data breach | Unexpected data access | Isolate system | Restore from backup | Within 1h |
| DDoS | Traffic spike | Cloudflare rate limit | Scale up | Within 4h |
| Malware | File integrity alert | Quarantine container | Rebuild | Within 4h |

## 6. CURRENT GAPS
- No SIEM deployed (target: Q2 2026)
- No automated secret rotation
- No penetration testing program
- No bug bounty program

## 7. CONSTRAINT
- NEVER: Secret in code, config, or log
- NEVER: Open port without auth
- NEVER: Unaudited access to Brain
- ALWAYS: Escalate P0 security events immediately
