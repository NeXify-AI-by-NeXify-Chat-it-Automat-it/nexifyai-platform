# KI-Management-System (ISO 42001)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI
**Norm:** ISO/IEC 42001:2023 — Künstliche-Intelligenz-Managementsystem

---

## 1. Geltungsbereich

Das KI-Management-System umfasst alle KI-gestützten Komponenten der NeXifyAI-Plattform:
- Agent-Orchestrator (14 Agenten-Verträge)
- Oracle Engine (Enterprise AI Operating System)
- Brain API + Qdrant (Wissensmanagement)
- Legal Guardian (Compliance-Gate)
- Outbound Lead Machine (KI-Outreach)
- Customer Communication (Chat, E-Mail, Portal)
- Embedding Pipeline (Qwen3-Embedding-8B, 4096d)

## 2. KI-Governance-Prinzipien

| Prinzip | Beschreibung | Nachweis |
|---------|-------------|----------|
| **Brain-First** | Ohne Brain keine Arbeit | Brain API Health 200 |
| **Human Oversight** | Admin-Kontrolle über Agent-Aktionen | Admin Chat Gateway |
| **Transparenz** | KI-generierte Inhalte gekennzeichnet | Chat-UI, E-Mail-Signatur |
| **Fairness** | Legal Gate vor Outreach | legal_guardian.py |
| **Robustheit** | Retry, Fallback, Circuit Breaker | 3-Stufen-Embedding |
| **Datenschutz** | DSGVO-konform | Löschkonzept, VVT, AVV |
| **Rückverfolgbarkeit** | Audit-Log für alle Aktionen | Timeline, Events |

## 3. KI-Systemklassifikation (EU AI Act)

| Kriterium | Bewertung |
|-----------|-----------|
| Risikoklasse | **Minimales Risiko** |
| Transparenzpflicht | ✅ Erfüllt (Art. 50) |
| Human Oversight | ✅ Implementiert (Art. 14) |
| Technical Doc | ✅ Vorhanden (Art. 11) |

Siehe [EU AI Act Assessment](../legal/eu-ai-act-assessment.md)

## 4. Agenten-Governance (14 Verträge)

| Rolle | Funktion | Restriktionen |
|-------|----------|--------------|
| AI-CEO | Orchestrierung & Strategie | kein DB-Write, kein Deploy |
| AI-Governor | Policy-Enforcement | kein Code-Write |
| AI-Retrieval | Wissensabruf | kein Write, kein Execute |
| AI-Security | Threat Detection | kein Deploy |
| AI-Compliance | Regulatory | kein System-Change |
| AI-Architect | Architektur | kein Write/Deploy/Execute |
| AI-Auditor | Integritätsprüfung | kein Modify |
| AI-Reviewer | Qualitätssicherung | kein Production-Write |

## 5. KI-Risikomanagement

| Risiko | Eintrittsw'keit | Schwere | Maßnahme |
|--------|----------------|---------|----------|
| Halluzination | Mittel | Niedrig | Legal Gate, Human-in-the-Loop |
| Bias | Niedrig | Mittel | Strukturierte Outputs, fit-scoring |
| Data Leak | Niedrig | Hoch | DPA mit OpenRouter, Audit-Log |
| Fehlentscheidung | Mittel | Niedrig | Admin-Eskalation, Review-Prozess |
| Prompt Injection | Niedrig | Hoch | Input-Validierung, Escape-Funktion |

## 6. KI-Qualitätssicherung

| Maßnahme | Frequenz | Automatisiert |
|----------|----------|---------------|
| Loop 3: AI Quality (Memory, Embedding, Halluzination) | Stündlich | ✅ |
| Health-Score | Alle 30 Min | ✅ |
| Embedding-Health | Pro Query | ✅ |
| Agent-Contract-Validierung | Pro Execution | ✅ |
| Brain-Konsistenz | Pro Store | ✅ |

## 7. Verweise

- [AI Governance Policy](../agency/DOS_AI_GOVERNANCE.md)
- [Agent Governance Policy](../agency/DOS_AGENT_GOVERNANCE.md)
- [Agenten-Verträge](../../contracts/agents.yaml)
- [EU AI Act Assessment](../legal/eu-ai-act-assessment.md)
- [Operational Constitution](../../operational-constitution.md)
- [Legal Guardian](../../services/api/services/legal_guardian.py)