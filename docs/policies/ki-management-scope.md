# KI-Management-Scope (ISO 42001:2023)

**Stand:** 2026-05-30
**Version:** 1.0
**Scope-ID:** AIMS-SCOPE-001
**Verantwortlich:** NeXifyAI
**Norm:** ISO/IEC 42001:2023 — Künstliche-Intelligenz-Managementsystem (AIMS)

---

## 1. Scope-Definition

### 1.1 Organisation
| Feld | Wert |
|------|------|
| Unternehmen | NeXifyAI — neXify (Chat it. Automate it.) |
| Standort | Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande |
| Scope-ID | AIMS-SCOPE-001 |
| Version | 1.0 |
| Datum | 2026-05-30 |

### 1.2 Scope-Erklärung
Das AIMS umfasst die Entwicklung, den Betrieb und die Governance aller KI-gestützten Systeme der NeXifyAI Enterprise Brain v3 Plattform. Dies schließt die 14 KI-Agenten, den Oracle-Orchestrator, die Brain API mit Qdrant-Vektorsuche, die Embedding-Pipeline (Nscale Qwen3-8B, 4096d) sowie sämtliche KI-gestützten Kommunikations- und Automationsfunktionen ein.

---

## 2. KI-Systeme im Scope

### 2.1 KI-Systeme (Übersicht)

| ID | System | Typ | Zweck | Risikoklasse (EU AI Act) |
|----|--------|-----|-------|------------------------|
| **AIMS-SYS-001** | Agent-Orchestrator (14 Agenten) | Multi-Agent-System | Task-Orchestrierung, Entscheidungsfindung | Minimal |
| **AIMS-SYS-002** | Oracle Engine | Enterprise AI OS | System-Orchestrierung, Loop-Management | Minimal |
| **AIMS-SYS-003** | Brain API + Qdrant | Wissensmanagement | Semantische Suche, Memory, Embedding | Minimal |
| **AIMS-SYS-004** | Outbound Lead Machine | KI-Outreach | Lead-Generierung, Website-Analyse, Outreach | Minimal |
| **AIMS-SYS-005** | Customer Communication | KI-Chat | Chat, E-Mail, Portal-Kommunikation | Minimal |
| **AIMS-SYS-006** | Legal Guardian | Compliance-Gate | Outreach-Prüfung, DSGVO-Compliance | Minimal |
| **AIMS-SYS-007** | Embedding Pipeline | Vektorisierung | Qwen3-8B Embedding (4096d) | Minimal |
| **AIMS-SYS-008** | Health-Score System | Metrik-Erfassung | System-Zustandsbewertung | Minimal |

### 2.2 KI-Systeme (nicht im Scope)

| System | Begründung |
|--------|------------|
| CI/CD Pipeline (GitHub Actions) | Keine KI-Entscheidungen — regelbasiert |
| Supabase Auth | Keine KI — kryptografische Authentifizierung |
| Kubernetes/Docker-Orchestrierung | Keine KI — container-basiert |
| Monitoring (Prometheus/Grafana) | Keine KI — regelbasierte Metrik-Erfassung |

---

## 3. KI-Risikobewertung

### 3.1 Risikoklassifikation (EU AI Act)

| Kriterium | Bewertung | Nachweis |
|-----------|-----------|----------|
| Verbotene Praktiken (Art. 5) | ❌ Nicht relevant | Kein Social-Scoring, keine Manipulation, keine Biometrie |
| Hochrisiko (Annex III) | ❌ Nicht relevant | Keine kritische Infrastruktur, keine Bildungs-Zugänge |
| Transparenzpflicht (Art. 50) | ✅ Erfüllt | AI-Signatur, Chat-Kennzeichnung, DSE-Info |
| Minimales Risiko | ✅ Zutreffend | Chat-Support, Lead-Qualifizierung, Angebotserstellung |

Siehe [EU AI Act Assessment](../legal/eu-ai-act-assessment.md)

### 3.2 KI-Risikomatrix

| Risiko | Eintrittsw'keit | Schwere | Risikowert | Maßnahme | Verantwortlich |
|--------|----------------|---------|------------|----------|----------------|
| Halluzination (falsche Fakten) | Mittel | Niedrig | **Niedrig** | Legal Gate, Human-in-the-Loop, 3-Query-Validierung | AI-QA |
| Bias/Voreingenommenheit | Niedrig | Mittel | **Niedrig** | Strukturierte Outputs, fit-scoring, diverse Modelle | AI-Ethics |
| Data Leak (über LLM-Provider) | Niedrig | Hoch | **Mittel** | DPA mit OpenRouter, keine Rohdaten-Speicherung | AI-Security |
| Fehlentscheidung (Outreach) | Mittel | Mittel | **Mittel** | Admin-Eskalation, Legal Gate, Review-Prozess | AI-Compliance |
| Prompt Injection | Niedrig | Hoch | **Mittel** | Input-Validierung, Escape-Funktion, Zwangsbefehl-Header | AI-Security |
| Modell-Drift | Niedrig | Mittel | **Niedrig** | Loop 3: wöchentliche Qualitätsprüfung | AI-QA |
| Embedding-Fehler | Mittel | Niedrig | **Niedrig** | 3-Stufen-Fallback (OpenRouter→Ollama→Zero-Vector) | AI-Runtime |

### 3.3 Risiko-Behandlungsplan

| Risiko | Behandlung | Restrisiko | Überwachung |
|--------|-----------|------------|-------------|
| Halluzination | Human-in-the-Loop + Legal Gate | Akzeptabel | Loop 3 (ständlich) |
| Data Leak | DPA + keine Speicherung | Akzeptabel | Security-Review (wöchentlich) |
| Fehlentscheidung | Admin-Eskalation | Akzeptabel | Review-Prozess (pro Execution) |
| Prompt Injection | Input-Validierung + Zwangsbefehl | Akzeptabel | CI/CD-Scan (pro Commit) |

---

## 4. KI-Governance-Struktur

### 4.1 Rollen und Verantwortlichkeiten

| Rolle | Verantwortung | Agent |
|------|---------------|-------|
| **KI-Verantwortlicher** | Gesamtverantwortung AIMS | Pascal Courbois (CEO) |
| **KI-Sicherheitsbeauftragter** | Security der KI-Systeme | AI-Security |
| **KI-Compliance-Beauftragter** | Regulatorische Compliance | AI-Compliance |
| **KI-Qualitätsbeauftragter** | Qualitätssicherung | AI-QA |
| **KI-Ethik-Beauftragter** | Bias-Prüfung, Fairness | AI-Ethics |
| **KI-Architekt** | System-Design, ADR | AI-Architect |

### 4.2 KI-Governance-Pyramide

```
Menschliche Aufsicht (Pascal Courbois)
│
├── AI-CEO (Orchestrierung, Entscheidungen)
│   ├── AI-Governor (Policy-Enforcement)
│   │   ├── AI-Compliance (Regularien)
│   │   └── AI-Ethics (Bias, Fairness)
│   ├── AI-Security (Sicherheit)
│   ├── AI-Architect (Design)
│   ├── AI-QA (Qualität)
│   └── AI-Memory (Wissen)
```

### 4.3 Entscheidungsbefugnisse

| Entscheidungstyp | Autonom | Bedingt | Niemals |
|-----------------|---------|---------|---------|
| Brain lesen/schreiben | ✅ Immer | — | — |
| Code ändern | ✅ T1 | ✅ T2 | — |
| PR mergen | — | ✅ Mit CI-Grün | — |
| Deployment main | — | — | ❌ Pascal |
| Secret-Rotation | — | — | ❌ Pascal |
| DB-Migration | — | — | ❌ Pascal |

Quelle: [Operational Constitution Art. 7](../../operational-constitution.md)

---

## 5. KI-Lebenszyklus

### 5.1 Entwicklungsphase
```
Idee → ADR → Architektur-Review → Implementierung → Tests → CI/CD → Brain-Store
```

| Schritt | Gate | Verantwortlich |
|---------|------|---------------|
| Idee | — | AI-CEO |
| ADR | GATE-06 (DOS) | AI-Architect |
| Architektur-Review | AI-Architect | AI-Architect |
| Implementierung | GATE-13 (CI/CD) | AI-Runtime |
| Tests | GATE-16 (DoD) | AI-QA |
| Deployment | GATE-17 (Evidence) | AI-Runtime |

### 5.2 Betriebsphase
```
Health-Check → Loop-Überwachung → Incident-Response → Lessons Learned
```

| Schritt | Frequenz | Automatisiert |
|---------|----------|---------------|
| Health-Score | Alle 30 Min | ✅ |
| Loop 3 (AI Quality) | Stündlich | ✅ |
| Embedding-Health | Pro Query | ✅ |
| Security-Review | Wöchentlich | ⚠️ Teilweise |
| Compliance-Review | Wöchentlich | ℹ️ Manuell |

### 5.3 Ausserbetriebnahme
```
Deaktivierung → Datenarchivierung → Brain-Cleanup → Abschlussbericht
```

---

## 6. KI-Dokumentation (ISO 42001 Cap. 7.5)

| Dokument | Inhalt | Ort |
|----------|--------|-----|
| KI-Management-System | AIMS-Beschreibung (ISO 42001) | [ki-management-system.md](./ki-management-system.md) |
| KI-Management-Scope | Scope, Systeme, Risiken (dieses Dokument) | [ki-management-scope.md](./ki-management-scope.md) |
| AI Governance Policy | 5 Kernprinzipien | [DOS_AI_GOVERNANCE.md](../agency/DOS_AI_GOVERNANCE.md) |
| Agent Governance Policy | 14 Agenten-Verträge | [DOS_AGENT_GOVERNANCE.md](../agency/DOS_AGENT_GOVERNANCE.md) |
| Agenten-Verträge | Rollen, Capabilities, Restrictions | [agents.yaml](../../contracts/agents.yaml) |
| EU AI Act Assessment | Risikoklassifikation, Transparenz | [eu-ai-act-assessment.md](../legal/eu-ai-act-assessment.md) |
| Operational Constitution | 9 Artikel Governance | [operational-constitution.md](../../operational-constitution.md) |

---

## 7. KI-Leistungsindikatoren (KI-KPIs)

| KPI | Metrik | Grenzwert | Aktuell |
|-----|--------|-----------|---------|
| Systemverfügbarkeit | Health-Score | >= 90% | **95%** 🟢 |
| Brain-Qualität | Points-Wachstum | Steigend | **112.425** 🟢 |
| Embedding-Verfügbarkeit | Embedding-Status | Verftigbar | **fallback_active** 🟡 |
| Halluzinationsrate | Loop 3 Query-Ergebnis | >= 80% Pass | **100%** 🟢 |
| Agent-Effizienz | Task-Completion-Rate | >= 80% | **87.5%** 🟢 |
| Compliance | Offene Findings | < 5 | **0** 🟢 |

---

## 8. KI-Audit-Programm

| Audit-Typ | Rhythmus | Prüfer | Umfang |
|-----------|----------|--------|--------|
| **KI Qualitäts-Audit** | Stündlich (Loop 3) | AI-QA | Memory, Embedding, Halluzination |
| **KI Security-Audit** | Wöchentlich | AI-Security | Prompt-Injection, Data Leaks |
| **KI Compliance-Audit** | Wöchentlich | AI-Compliance | DSGVO, EU AI Act, ISO 42001 |
| **KI Ethik-Audit** | Monatlich | AI-Ethics | Bias, Fairness, Transparenz |
| **AIMS-Managementbewertung** | Quartalsweise | Pascal + AI-CEO | Gesamtes AIMS |

---

## 9. Verweise

| Dokument | Ort |
|----------|-----|
| KI-Management-System (ISO 42001) | [ki-management-system.md](./ki-management-system.md) |
| AI Governance Policy | [DOS_AI_GOVERNANCE.md](../agency/DOS_AI_GOVERNANCE.md) |
| Agent Governance Policy | [DOS_AGENT_GOVERNANCE.md](../agency/DOS_AGENT_GOVERNANCE.md) |
| EU AI Act Assessment | [eu-ai-act-assessment.md](../legal/eu-ai-act-assessment.md) |
| Operational Constitution | [operational-constitution.md](../../operational-constitution.md) |
| Agenten-Verträge | [agents.yaml](../../contracts/agents.yaml) |
| ISMS-Scope | [isms-scope.md](./isms-scope.md) |
| QM-Handbuch | [qm-handbuch.md](./qm-handbuch.md)