# Qualitätsmanagement-Handbuch (ISO 9001)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI Product Owner / Pascal Courbois
**Norm:** ISO 9001:2015 — Qualitätsmanagementsystem

---

## 1. QM-Politik

Die NeXifyAI-Plattform wird nach folgenden Qualitätsprinzipien entwickelt:

1. **Kundenorientierung** — Jede Funktion löst ein echtes Kundenproblem
2. **Prozessorientierung** — Wiederholbare Workflows statt Ad-Hoc-Lösungen
3. **Kontinuierliche Verbesserung** — Lessons Learned + Prevention Rules = Pflicht
4. **Faktenbasierte Entscheidungen** — Health-Score, Metriken, Runtime Evidence
5. **Mitarbeiterbeteiligung** — Agenten-Governance mit klaren Rollen (14 Contracts)

## 2. Qualitätsziele

| Ziel | Metrik | Grenzwert | Aktuell |
|------|--------|-----------|---------|
| Systemverfügbarkeit | Health-Score | ≥ 90% | **95%** 🟢 |
| Testabdeckung | CI/CD Pipeline | Tests ≤ 5% Fail | **0% Fail** 🟢 |
| Incident-Response | SEV1 Reaktionszeit | < 15 Min | ✅ Definiert |
| Dokumentation | ADR-Vollständigkeit | 100% | **33 ADRs** 🟢 |
| Kundenzufriedenheit | Support-Tickets | — | Implementiert |

## 3. Qualitätsprozesse

### 3.1 Entwicklungsprozess (Definition of Done)
Jeder Task durchläuft 5 Qualitätsstufen:

```
1. Technisch: Code, Typecheck, Lint, Tests, Build, Security, CI
2. Inhaltlich: Copy-Compiler, Zielgruppe, Funnel
3. Design: Designsystem, Responsive, WCAG, Brand
4. Tracking: Events, Payload, Automation
5. Governance: Doku, ADR, Lessons, Brain
```

Nachweis: DoD-Checkliste in [DOS Definition of Done](../agency/DOS_DEFINITION_OF_DONE.md)

### 3.2 Review-Prozess
| Review-Typ | Wann | Wer |
|------------|------|-----|
| Code-Review | Vor jedem Merge | Tech Lead / AI-Architect |
| Security-Review | Bei System-Änderungen | AI-Security |
| Compliance-Review | Bei Legal-Änderungen | AI-Compliance |
| Design-Review | Bei UI-Änderungen | AI-Architect |
| Architektur-Review | Bei Architektur-Entscheidungen | AI-Architect + ADR |

### 3.3 Qualitäts-Gates (17 Gates)
Siehe [DOS Gates](../agency/DOS_GATES.md). Jeder Task durchläuft GATE-01 bis GATE-17.

## 4. Dokumentenlenkung

| Dokumenttyp | Verwaltung | Versionierung |
|-------------|-----------|---------------|
| ADRs | docs/adrs/ | SemVer | 
| Policies | docs/policies/ | Datum |
| Legal | docs/legal/ | Datum |
| System-Docs | docs/systems/ | SemVer |
| DOS-Standards | docs/agency/ | v1.x, v2.0 |
| Machine-Readable | docs/agency/machine-readable/ | JSON-Schema |

## 5. Messung, Analyse, Verbesserung

| Maßnahme | Output | Intervall |
|----------|--------|-----------|
| Health-Score | Score-Bericht | Alle 30 Min |
| CI-Status | Pipeline-Output | Bei jedem Push |
| Audit (Enterprise) | Audit-Bericht | Täglich/Wöchentlich |
| Incident-Postmortem | Lessons Learned | Nach SEV1/SEV2 |
| Qualitäts-Review | Review-Bericht | Wöchentlich |

## 6. Verweise

- [Definition of Done](../agency/DOS_DEFINITION_OF_DONE.md)
- [Quality Gates](../agency/DOS_GATES.md)
- [ADR-Verzeichnis](../adrs/README.md)
- [Test-Suite](../../services/api/tests/)