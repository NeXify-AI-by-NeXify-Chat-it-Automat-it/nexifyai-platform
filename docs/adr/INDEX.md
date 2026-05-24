# Architecture Decision Records — Index
# =============================================================================
# Stand: 2026-05-22 16:42 UTC
# =============================================================================

## Status-Legende
| Symbol | Status | Beschreibung |
|--------|--------|-------------|
| ✅ | accepted | Genehmigt und verbindlich |
| 📝 | proposed | Vorgeschlagen, nicht genehmigt |
| ⚠️ | deprecated | Nicht mehr gültig |
| 🔄 | superseded | Durch neueren ADR ersetzt |

---

## ADR Registry

| Nr | Titel | Status | Datum |
|----|-------|--------|-------|
| ADR-001 | Einführung DOS v2.0 als verbindliches Betriebssystem | ✅ accepted | 2026-05-08 |
| ADR-002 | Supabase als Primary Database | 📝 proposed | 2026-05-08 |
| ADR-003 | OpenRouter als primärer LLM-Provider | 📝 proposed | 2026-05-08 |
| ADR-004 | Monorepo-Struktur und Package-Grenzen | 📝 proposed | 2026-05-08 |
| ADR-005 | API-Standardisierung & Automation Layer | 📝 proposed | 2026-05-08 |
| ADR-006 | Queue-System mit BullMQ | 📝 proposed | 2026-05-08 |
| ADR-007 | Health-System v3 — Topologie-Aware | 📝 proposed | 2026-05-08 |
| ADR-008 | AI Agent Operating Layer | 📝 proposed | 2026-05-08 |
| ADR-009 | Event-Taxonomie & Automation | 📝 proposed | 2026-05-08 |
| ADR-010 | CI/CD Pipeline | 📝 proposed | 2026-05-08 |
| ADR-011 | Security Scanning | 📝 proposed | 2026-05-08 |
| ADR-012 | Incident Management | 📝 proposed | 2026-05-08 |
| ADR-013 | Multi-Tenant Architektur | 📝 proposed | 2026-05-08 |
| ADR-014 | Knowledge System (Brain) | 📝 proposed | 2026-05-08 |
| ADR-015 | Health Monitoring | 📝 proposed | 2026-05-08 |
| ADR-016 | FinOps-Strategie | 📝 proposed | 2026-05-08 |
| ADR-017 | Testing-Strategie | 📝 proposed | 2026-05-08 |
| ADR-019 | LangChain/LangGraph Agenten-Optimierung | 📝 proposed | 2026-05-21 |

> **Hinweis:** ADR-018 wurde übersprungen. Nächste freie Nummer: ADR-020.

---

## Kategorien

| Kategorie | ADRs |
|-----------|------|
| **Architektur** | 001, 002, 004, 008, 013, 014 |
| **Plattform/Infra** | 003, 005, 006, 007, 010 |
| **Security/Compliance** | 011, 012, 015 |
| **Operations/FinOps** | 016, 017, 019 |
| **AI/Agent** | 008, 014, 019 |
| **Daten/Events** | 009 |

---

## Lifecycle
```
proposed → accepted → deprecated → superseded (by newer ADR)
```

## Neuen ADR erstellen
1. Kopiere `template.md` → `ADR-NNN-kurztitel.md`
2. Fülle alle Abschnitte aus
3. Status auf `proposed`
4. PR mit ADR-Request-Label
5. Nach Approval: Status → `accepted`, INDEX.md aktualisieren

## Naming-Konvention
- Dateiname: `ADR-NNN-kurztitel-mit-bindestrichen.md`
- NNN: Fortlaufend (001-999), führende Nullen
- Nummern werden NICHT wiederverwendet
