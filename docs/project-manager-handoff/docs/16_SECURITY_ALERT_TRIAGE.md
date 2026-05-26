# 16 — Security Alert Triage

> **Stand: 2026-05-26T08:17 UTC**
> Vollständige Triage aller Security Alerts aus dem Repository
> `NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`
>
> **⚠️ Keine Alerts blind schließen — jeder Alert braucht Evidence + Issue/PR.**

---

## 1. Gesamtübersicht

| Typ | Total | Open | Critical | High | Medium |
|-----|-------|------|----------|------|--------|
| **Code Scanning** (CodeQL + Trivy) | 184 | 106 | 6 (2 open) | 97 (49 open) | 81 (55 open) |
| **Dependabot** | 7 | 0 | 0 | 0 | 0 |
| **Secret Scanning** | 2 | 0 | 0 | 0 | 0 |

**184 Alerts total, 106 offen, 78 fixed/resolved.**

---

## 2. Priorisierte Alert-Cluster (Fix-Reihenfolge)

### P0 — Fix sofort

| # | Severity | Type | File:Line | Issue |
|---|----------|------|-----------|-------|
| #28 | 🔴 Critical | Full SSRF | `crawl4ai_service.py:129` | #41 |

### P1 — Fix nächste Woche

| Cluster | Alerts | Files | Issue |
|---------|--------|-------|-------|
| **Clear-text storage** | #157–#150 | `services/runtime/security/vault/`, `audit/`, `rotation/` | #42 |
| **Clear-text logging** | #149–#143, #30 | `services/runtime/security/vault/`, `rotation/`, `audit/`, `model_router.py:121` | #43 |
| **Path traversal** | #86, #85, #84 | `skill_registry/registry.py:18-19`, `nutrient_service.py:34` | #44 |
| **Weak crypto** | #27 | `api_v1_routes.py:26` | #45 |
| **DOM XSS patterns** | #90, #88, #87 | `index.html:101`, `Admin.js:3708`, `chat.html:107` | (in #47) |

### P2 — Klassifizieren/Excluden

| Cluster | Alerts | Status |
|---------|--------|--------|
| **Insecure randomness** | #176, #175, #174, #126 | `_archive/` → exclude from CodeQL |
| **Test alerts** | #39, #38, #37 | Test fixtures → exclude or fix |
| **Frontend clear-text** | #95, #94, #93, #92, #91 | Review if real secrets |
| **Incomplete URL/escape** | #171–#166 | Mostly fixed duplicates |
| **Trivy CVEs** | ~26 medium | Container not prod → configured ignore |

### Fixed Alerts (78)

Alle Alerts auf `knowledge/emergent/`, `knowledge/emergent-bundle/`, `runtime/security/` (alte Pfade) sowie Secret-Scanning (#9–#5) und Dependabot sind bereits fixed.

---

## 3. Projekt-Governance

Alle offenen Security-Arbeiten sind als Issues erfasst und dem
**NeXify AI Master Delivery** Project (#2) zugeordnet.

| Issue | Titel | Priority | Status |
|-------|-------|----------|--------|
| #40 | Ruleset docs/** exclusion | P0 | Blocked (App permissions) |
| #41 | Fix SSRF (Alert #28) | P0 | Open |
| #42 | Clear-text storage (#157–#150) | P1 | Open |
| #43 | Clear-text logging (#149–#143, #30) | P1 | Open |
| #44 | Path traversal (#86/#85/#84) | P1 | Open |
| #45 | Weak crypto (#27) | P1 | Open |
| #46 | Secrets setup — all missing | P1 | Open |
| #47 | Test/archive CodeQL classification | P2 | Open |
| #49 | GitHub webhook endpoint | P1 | Blocked |
| #50 | Legacy Cline workflows | P2 | Open |

---

## 4. Monitoring-Regeln

| Regel | Beschreibung |
|-------|-------------|
| Neue P0 Alerts | Sofort Issue + Brain-Update |
| Neue Secret Scanning | Push Protection prüfen |
| Dependabot Critical/High | Automatischer PR (aktiv) |
| Kein Alert ohne Triage | Jeder braucht Evidence + Issue/PR |
| Archive/Test excluden | Nur mit dokumentierter Begründung |

---

## 5. Nächste konkrete Schritte

1. **Ruleset fixen**: GitHub App Permissions erweitern oder UI-Manual
2. **PR #39**: Fix SSRF in crawl4ai_service.py
3. **PR #40**: Fix clear-text storage in security modules
4. **PR #41**: Fix clear-text logging + redaction
5. **PR #42**: Fix path traversal
6. **PR #43**: Fix weak crypto
7. **Secrets setzen**: Owner identifizieren, Werte beschaffen
