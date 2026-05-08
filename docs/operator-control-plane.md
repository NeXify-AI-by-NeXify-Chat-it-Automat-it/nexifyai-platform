# NeXifyAI — Operator Control Plane (E2.5)
**Status:** EVALUATION (Design) | **Datum:** 2026-05-08

## Zweck

Definiert die direkten Kommunikationskanäle zwischen Hermes Runtime und Operatoren.  
Nicht: Mensch → ChatGPT → Hermes.  
Sondern: Runtime Event → Hermes → Operator Channel → Recovery.

---

## 1. KANAL-EVALUATION

| Kanal | Protokoll | Latenz | Security | Aufwand | Empfehlung |
|-------|-----------|--------|----------|---------|------------|
| **Slack** | Webhook/Events API | <1s | OAuth 2.0, signing secrets | Mittel | ✅ Phase 1 |
| **Discord** | Webhook | <1s | Webhook-URL als Secret | Niedrig | ✅ Phase 1 (besteht) |
| **Matrix** | Federation | <1s | E2E encryption | Hoch | ⏸ Phase 3 |
| **ntfy** | HTTP | <1s | Token-auth | Niedrig | ✅ Phase 2 |
| **GitHub Issues** | REST API | <5s | PAT/OAuth | Niedrig | ✅ Bestehend |
| **Email (Resend)** | SMTP | <30s | API-Key | Niedrig | ✅ Bestehend |
| **Telegram** | Bot API | <1s | Bot-Token | Niedrig | ✅ Phase 1 |
| **Signal** | signal-cli | <5s | E2E | Hoch | ⏸ Phase 3 |

---

## 2. SECURITY-MODELL

### 2.1 Secrets
- Alle Channel-Credentials in `/opt/CREDENTIALS.md` (nicht im Repo)
- Webhook-URLs, Bot-Tokens, API-Keys niemals im Code
- Environment Variables via `.env` (gitignored)

### 2.2 Anti-Spam / Rate-Limiting
- Max 1 Recovery-Nachricht pro Service pro 5 Minuten
- Deduplizierung via Event-ID (incident_id + timestamp hash)
- Severity-Filter: nur HIGH/CRITICAL → Operator-Channel

### 2.3 Replay Protection
- Jede Runtime-Nachricht trägt `X-Message-ID` (UUID)
- Operator-Channel speichert last 100 Message-IDs
- Duplikate werden silently verworfen

---

## 3. ESCALATION-FLOWS

```
Runtime Event (z.B. qdrant unreachable)
  │
  ├─ Severity LOW/MEDIUM → Brain persist + Log
  │
  ├─ Severity HIGH → Brain + Discord Webhook
  │
  └─ Severity CRITICAL → Brain + Discord + Email + Slack
       │
       └─ Kein ACK in 5 Min → Escalation: ntfy Push
```

---

## 4. RECOVERY-KOMMANDOS (Gateway)

Hermes darf Recovery-Kommandos vorschlagen, aber Operatoren müssen bestätigen:

```
Hermes: "Qdrant unreachable from container. Recovery: docker restart nexifyai-qdrant"
Operator: "!recover qdrant-primary"
Hermes: "Executing: docker restart nexifyai-qdrant... ✅ Service recovered (2.3s)"
```

### 4.1 Erlaubte Kommandos (Whitelist)
- `systemctl restart nexifyai-backend`
- `docker restart <service>`
- `systemctl status <unit>`
- `docker ps --filter name=<name>`

### 4.2 Verbotene Kommandos (Blacklist)
- `rm -rf`
- `DROP TABLE`
- `docker rm`
- `iptables`
- `shutdown / reboot`

---

## 5. AUDITIERBARKEIT

Jede Operator-Interaktion wird geloggt:
```json
{
  "event": "operator_action",
  "channel": "discord",
  "operator": "pascal",
  "command": "recover qdrant-primary",
  "result": "success",
  "duration_ms": 2300,
  "timestamp": "2026-05-08T18:00:00Z"
}
```

Logs in `brain.db` → `operator_actions` Tabelle (geplant in Migration 006).

---

## 6. IMPLEMENTIERUNGS-PLAN

### Phase 1 (JETZT)
- Discord Webhook (besteht bereits via Hermes Gateway)
- GitHub Issue Automation (besteht via `mcp_github`)

### Phase 2 (NACH INFRA-STABILISIERUNG)
- Slack SDK Integration
- ntfy Push für Critical Alerts
- Telegram Bot

### Phase 3 (SPÄTER)
- Matrix E2E-encrypted Channel
- Signal Gateway
- Bidirektionale Recovery-Bestätigung

---

## 7. STATUS

| Kanal | Status |
|-------|--------|
| Discord | ✅ Aktiv (Hermes Gateway Native) |
| Telegram | ✅ Aktiv (Hermes Gateway Native) |
| GitHub Issues | ✅ Aktiv (MCP) |
| Email (Resend) | ✅ Konfiguriert (nicht aktiv für Runtime) |
| Slack | 🔜 Phase 1 |
| ntfy | 🔜 Phase 2 |
| Matrix | ⏸ Phase 3 |
| Signal | ⏸ Phase 3 |
