# docs/agency — NeXifyAI Governance & Operating System

> **Verbindlicher Hauptstandard: [docs/DOS-v2.0.md](../DOS-v2.0.md)**

## Hierarchie der DOS-Wahrheit

| Dokument | Status | Rolle |
|---|---|---|
| `docs/DOS-v2.0.md` | **Hauptstandard** | Aktueller, verbindlicher DOS. Gilt immer. |
| `docs/agency/DOS_v1.1_SOURCE.md` | Historisch | Ursprüngliche Quelle. Nur als Referenz/Kontext. |
| `docs/agency/DOS_v1.2_EXTENDED.md` | Delta/Erweiterung | Ergänzungen zu v1.1. Kein eigenständiger Standard. |

## Inhalt von docs/agency

```
docs/agency/
├── README.md                          ← Diese Datei (Orientierung & Verknüpfung)
├── DOS_UPDATE_POLICY.md               ← Regeln für DOS-Updates und Konflikte
├── DOS_LEARNING_POLICY.md             ← Lernpolitik: was/wie gespeichert wird
├── DOS_RESOURCE_FIRST.md              ← Resource-First-Prinzip
├── DOS_PLATFORM_OPERATING_MODEL.md    ← Plattform-Betriebsmodell
├── DOS_CUSTOMER_PROJECT_GOLDEN_PATH.md← Goldener Pfad für Kundenprojekte
├── DOS_CLEAN_REUSE_CATALOG.md         ← Clean-Reuse-Katalog
├── DOS_REUSE_GOVERNANCE.md            ← Reuse-Governance-Regeln
├── DOS_AUTOMATED_DOCUMENTATION.md     ← Regeln für automatisierte Dokumentation
├── DOS_AGENT_GOVERNANCE.md            ← Agenten-Governance
├── DOS_AI_GOVERNANCE.md               ← KI-Governance
├── DOS_CHANGELOG.md                   ← Änderungshistorie
├── DOS_COMPLIANCE_MATRIX.md           ← Compliance-Matrix
├── DOS_DEFINITION_OF_DONE.md          ← Definition of Done
├── DOS_GATES.md                       ← Quality Gates
├── DOS_REQUIREMENTS_MATRIX.md         ← Anforderungsmatrix
├── DOS_SERVICE_CATALOG.md             ← Service-Katalog
├── DOS_SKILL_COMPOSITION.md           ← Skill-Kompositions-Regeln
├── DOS_v1.1_SOURCE.md                 ← Historische Quelle (v1.1)
├── DOS_v1.2_EXTENDED.md               ← Delta/Erweiterung (v1.2)
├── learning/                          ← Lern- & Prevention-Registries
│   ├── ai-systems-learning-policy.md
│   ├── decision-memory.json
│   ├── failed-patterns.json
│   ├── lessons-learned.json
│   ├── prevention-rules.json
│   ├── resource-catalog.json
│   └── reusable-capabilities.json
├── machine-readable/                  ← Maschinenlesbare Policy-Dateien
│   ├── agency-dos-file-index.json     ← Datei-Index (maschinenlesbar)
│   ├── customer-project-reuse-map.json
│   ├── documentation-automation-rules.json
│   ├── dos-compliance-map.json
│   ├── dos-customer-project-golden-path.json
│   ├── dos-definition-of-done.json
│   ├── dos-gates.json
│   ├── dos-learning-policy.json
│   ├── dos-platform-operating-model.json
│   ├── dos-requirements.json
│   ├── dos-service-catalog.json
│   ├── dos-skill-map.json
│   ├── dos-v1.1-extracted.json
│   ├── dos-v1.2-extended.json
│   ├── reusable-artifacts.json
│   └── reuse-catalog.json
└── understanding/                     ← Verständnis-Maps & Capability-Modelle
    ├── (38 weitere JSON/MD-Dateien)
```

## Kern-Regeln

1. **docs/DOS-v2.0.md ist der einzig verbindliche Hauptstandard.**
2. Neue Erkenntnisse müssen in DOS / Learning / Prevention / Resource und Brain abgeglichen werden.
3. **GitHub ist Source of Truth.** Lokale Goose-/Brain-Ablagen sind nur Runtime-/Working-Copies.
4. Kundenprojekt-Code darf nicht ungeprüft kopiert werden.
5. Keine Secrets, Kundendaten oder Markenlogik übernehmen.
6. Vor jeder Implementierung: Resource-First-Prüfung (vgl. `DOS_RESOURCE_FIRST.md`).

## Konflikt-Auflösung zwischen DOS-Versionen

Bei Widersprüchen gilt folgende Priorität:
1. `docs/DOS-v2.0.md` — Hauptstandard
2. Neuere ADRs/Changelogs, falls explizit beschlossen
3. `docs/agency machine-readable` Policies als ausführbare Ergänzung
4. Historische Quellen (v1.1, v1.2) nur als Kontext

## Source of Truth

| Ablage | Rolle |
|---|---|
| GitHub (dieses Repo) | **Source of Truth** |
| Lokaler goose-skill-bridge | Working Copy (nicht final) |
| Brain/Qdrant | Runtime-Kontext (nicht final) |

---
*Erstellt: 2026-05-24 | Owner: NeXifyAI | Standard: docs/DOS-v2.0.md*
