# NeXifyAI Digital Operating System (DOS) v2.0

**Das integrierte, verbindliche Betriebssystem für alle NeXifyAI-Projekte**

Interne Produkte · Agenturprojekte · B2C · B2B · Enterprise · White-Label

**Version:** 2.0 | **Stand:** 2026-05-08
**Klassifikation:** INTERN – VERTRAULICH
**Vorgänger:** DOS v1.1 (2026-02-19)
**Verantwortlich:** NeXifyAI (Pascal Courbois, CEO)

---

## Systemmantra (unverändert aus v1.1)

Retrieval first. Marketplace first. Open Source first. Template first. CI driven. Security validated. Verify gated. Zero Information Loss. Systemische Konsistenz.

Jede Entscheidung oder Änderung ist: kontextualisiert · validiert · architektur-konform · CI-integriert · reproduzierbar · rollback-fähig · versioniert · auditiertbar · persistiert.

## Grundprinzip

Keine isolierte Lösung. Keine isolierte Installation. Keine isolierte Erweiterung. Keine isolierte Entscheidung.

**Kontext → Konsistenz → Validierung → Architekturprüfung → Umsetzung → Persistenz → CI → Governance**

---

# TEIL I: SYSTEMKERN (unverändert aus v1.1)

## 1. Einleitung & Systemüberblick

Das NeXifyAI Digital Operating System (DOS) ist das verbindliche, universelle Betriebssystem für alle Projekte unter der Marke NeXifyAI. Es ist kein Guideline-Dokument, das bei Bedarf konsultiert wird, sondern ein nicht-verhandelbarer Systemstandard.

### Anwendungsbereich

| Projekttyp | Beispiele |
|---|---|
| Interne Produktentwicklung | NeXify Chat it, Automate it, Plattform-Core |
| Agenturprojekte | Custom Builds, Kampagnenseiten, Repositories |
| B2C Kundenprojekte | Shops, Landingpages, Markenwebsites |
| B2B Kundenprojekte | SaaS, Portale, Enterprise-Software |
| White-Label / Partner | Lizenzierte Lösungen, Whitelabel-Produkte |

## 2. Systemkern & Unverhandelbare Guardrails

### 2.1 Die 7 Guardrail-Prinzipien

1. **Funnel-Zuordnung (Pflicht):** Jede Seite, jedes Feature, jede Automation muss einem Funnel-Schritt zugeordnet sein. Fehlt die Zuordnung → Raus aus dem Scope.
2. **Claims-Policy:** Jede Zahl, jedes Versprechen, jede Aussage braucht einen Scope (Segment, Zeitraum, Bedingung, Messmethode) oder wird explizit als "Beispielwert" markiert.
3. **No One-Off UI:** UI-Elemente entstehen ausschließlich über das zentrale Designsystem (`/packages/ui`).
4. **Tracking First:** Jede kritische Aktion ist Event-basiert messbar, bevor sie live geht.
5. **Loop-Automation:** KPI < Threshold → Trigger → Auto-Action → Messung → Entscheidung.
6. **Dokumentationspflicht:** Jede Implementierung dokumentiert mit Ziel, Funnel-Schritt, Trigger, KPI, Engpass und Ergebnis.
7. **Modularität:** Alle Komponenten sind austauschbar ohne Systembruch.

### 2.2 Pflicht-Reihenfolge bei Fehlerbehandlung

8. Stabilisieren (Root Cause isolieren)
9. Root Cause finden
10. Secondary Issues identifizieren (Blast Radius)
11. Vollständig beheben
12. Erst danach: Neuerungen

### 2.3 Memory-Architektur (Zero Information Loss)

| Ebene | Inhalt |
|---|---|
| STATE | Aktueller Systemzustand (Infrastruktur, Deployments, Konfigurationen) |
| KNOWLEDGE | Entscheidungen, Artefakte, Policies, Lessons Learned |
| TODO | Aufgaben, Risiken, Folgeaufgaben, Backlog |

Jeder Eintrag kategorisiert: Strategisch · Technisch · Infrastruktur · Policy · Workflow · Problem · Entscheidung · Lesson · Aufgabe.

---

# TEIL II: ROLLEN- & VERANTWORTUNGSARCHITEKTUR (NEU v2.0)

## 3. Rollenmodell & RACI-Matrix

### 3.1 Rollendefinitionen

| Rolle | Verantwortung | Entscheidungsrecht |
|---|---|---|
| **CEO (Pascal)** | Geschäftsstrategie, Budget, finale Design-Freigabe | Letztentscheidung |
| **NeXifyAI (KI-Lead)** | Architektur, Code-Qualität, Automatisierung, Brain-Governance | Technische Architektur, Tool-Wahl |
| **Technical Lead** | Code-Review, CI/CD, Security, Performance | Merge-Approval, Stack-Entscheidungen |
| **Security Officer** | Security-Audit, CVE-Monitoring, Incident-Response | Security-Blocks, Pen-Test-Freigabe |
| **Design Lead** | Designsystem, Brand-Konsistenz, UX | Design-Approval, Token-Änderungen |
| **Legal/Compliance** | DSGVO, AVV, Cookie-Governance, Lizenz-Scans | Compliance-Blocks |
| **Product Owner** | Roadmap, Priorisierung, Feature-Lifecycle | RICE-Scoring, Deprecation-Entscheidung |
| **DevOps** | Infrastruktur, Deployments, Monitoring, Backup | Infra-Änderungen, Release-Rollback |

### 3.2 RACI-Matrix

Siehe vollständige Matrix: `/docs/governance/raci.yaml`

**Kernbereiche:**
- **Designsystem:** Design Lead (A), NeXifyAI (R), CEO (C), Dev-Team (I)
- **Security:** Security Officer (A/R), DevOps (C), CEO (I)
- **Claims/Content:** Product Owner (A), Legal (R), CEO (C)
- **Infrastruktur:** DevOps (A/R), Security Officer (C)
- **KI-Governance:** NeXifyAI (A/R), Security Officer (C), CEO (I)

### 3.3 Eskalationspfade

```
Dev-Team → Technical Lead → NeXifyAI → CEO
                              ↓
                         Security Officer (bei Security-Fragen)
                              ↓
                         Legal (bei Compliance-Fragen)
```

---

# TEIL III: ADR-SYSTEM (NEU v2.0)

## 4. Architecture Decision Records

### 4.1 Template

Jeder ADR folgt diesem Template in `/docs/adrs/ADR-NNN-titel.md`:

```markdown
# ADR-NNN: Titel

**Status:** proposed | accepted | deprecated | superseded
**Datum:** YYYY-MM-DD
**Autor:** [Rolle]
**Stakeholder:** [Liste]

## Kontext
[Beschreibung des Problems/der Situation]

## Problem
[Konkrete Fragestellung]

## Optionen
1. Option A: [Beschreibung] — Pro/Contra
2. Option B: [Beschreibung] — Pro/Contra

## Entscheidung
[Gewählte Option mit Begründung]

## Konsequenzen
- Positiv: [Vorteile]
- Negativ: [Trade-offs, Risiken]
- Neutral: [Seiteneffekte]

## Rollback-Plan
[Wie machen wir das rückgängig?]

## Verweise
- [PR-Link]
- [Issue-Link]
```

### 4.2 Naming & Lifecycle

- Dateiname: `ADR-NNN-kurztitel.md` (NNN = fortlaufend, 001–999)
- Status-Flow: `proposed` → `accepted` → `deprecated` → `superseded`
- Bei Supersede: Verweis auf neuen ADR mit `superseded_by: ADR-XXX`
- Wiederverwendung von NNN: Nein (IDs sind unveränderlich)

### 4.3 Pflicht-ADRs (sofort zu erstellen)

- **ADR-001:** Einführung DOS v2.0 als verbindliches Betriebssystem
- **ADR-002:** Supabase als Primary Database (Ablösung MongoDB)
- **ADR-003:** OpenRouter als primärer LLM-Provider
- **ADR-004:** Monorepo-Struktur und Package-Grenzen

---

# TEIL IV: PROJEKTSYSTEM (aus v1.1)

## 5. Projektklassifikation

| Typ | Beschreibung | Funnel-Logik |
|---|---|---|
| A: SaaS / Plattform | Subscription, erklärungsbedürftig | Awareness → Education → Demo → Sales → Onboarding |
| B: B2C Shop | Transaktionsbasiert, Impuls/Preis | Traffic → Produkt → Vertrauen → Kauf → Upsell |
| C: B2B Shop | Qualitäts-/Beziehungsfokus | Research → Evaluation → Anfrage → Deal |
| D: Hybrid | Kombiniert mehrere Modelle | Segmentiert je Zielgruppe |
| E: Service / Consulting | Vertrauen & Expertise | Awareness → Trust → Kontakt → Angebot |
| F: Plattform / Marketplace | Netzwerkeffekte | Anbieter + Nachfrager parallel |

### Projekt-Start-Checkliste

1. Projekttyp klassifiziert (A–F)
2. Zielgruppen-Matrix erstellt (3 Ebenen)
3. Funnel-Architektur dokumentiert
4. Seitencluster definiert (8 Pflicht-Cluster)
5. Security-Stufe zugewiesen
6. KPI-Baseline definiert
7. CI-Pipeline konfiguriert
8. ADR-001 (Projekt-Baseline) erstellt

## 6. Zielgruppen-System

### Ebene 1 – Strukturell

| Segment | Rolle | Ziel | CTA |
|---|---|---|---|
| Privatkunde (B2C) | Endnutzer | Problem lösen | Kaufen / Jetzt starten |
| Geschäftskunde (B2B) | Entscheider | ROI erzielen | Demo / Angebot |
| Enterprise | CFO/CTO | Skalierung + Compliance | Gespräch / RFP |
| Partner / Reseller | Wachstumspartner | Provision + Wachstum | Partner werden |
| Investor | Kapitalgeber | Return + Skalierbarkeit | Kontakt aufnehmen |

### Ebene 2 – Psychologisch
Risikoscheu · Innovationsgetrieben · Preisfokus · Qualitätsfokus · Zeitmangel · Detailorientiert

### Ebene 3 – Intentions-basiert
Informationssuchend · Vergleichend · Kaufbereit · Wiederkehrend

---

# TEIL V: WEBSITE-ARCHITEKTUR (aus v1.1)

## 7. Website-Architektur Blueprint

### 7.1 Navigationsstruktur

| Navigationspunkt | Inhalt & Zweck |
|---|---|
| Lösungen (Solutions) | Use-Case-orientiert |
| Produkte (Products) | Modul-orientiert |
| Zielgruppen (Segments) | Segment-Landingpages |
| Preise (Pricing) | Transparent + FAQ + ROI |
| Ressourcen (Resources) | Blog, Guides, Glossar |
| Unternehmen (Company) | Über uns, Team, Partner |
| CTA (primär) | Demo / Jetzt starten |

### 7.2 Seitencluster-System (8 Pflicht-Cluster)

| Cluster | Funnel-Schritt | Conversion |
|---|---|---|
| Entry / Start | Awareness | Weiternavigation |
| Lösungen (Solutions) | Education | Demo |
| Produkte (Products) | Evaluation | Demo / Trial |
| Zielgruppen (Segments) | Personalisierung | Segment-Conversion |
| Preise (Pricing) | Evaluation | Plan-Auswahl |
| Ressourcen (Resources) | Education | Newsletter |
| Trust & Unternehmen | Trust | Referenz |
| Conversion | Conversion | Lead / Deal |

### 7.3 Interne Verlinkungsstrategie
- Produktseite → Use-Cases + Blog + Case Study
- Use-Case-Seite → Produkte + ROI + Demo
- Blog-Artikel → verwandte Artikel + Produkt + Newsletter-CTA

---

# TEIL VI: CONTENT & DESIGN (aus v1.1)

## 8. Content-System & Copy-Compiler

### 8.1 Der 8-Stufen Copy-Compiler

1. **Kontext:** Wer ist der Leser? In welcher Situation?
2. **Problem:** Konkreter Schmerz, Herausforderung
3. **Konsequenz:** Was passiert ohne Lösung?
4. **Lösung:** Wie löst unser Produkt das Problem?
5. **Mechanik:** Wie funktioniert die Lösung?
6. **Beweis:** Zahlen, Testimonials, Case Studies
7. **Nutzen:** Was gewinnt der Leser? (Outcome, nicht Feature)
8. **CTA:** Klare Handlungsaufforderung

### 8.2 Claims-Policy
Jede messbare Aussage enthält: Segment · Zeitraum · Bedingung · Messmethode
Fehlt die Methodik → "Beispielwert"-Markierung.

## 9. Design-System

### 9.1 Design Tokens

**Farben:**
- `--color-primary`: Deep Navy (#0f1923)
- `--color-accent`: NeXify Coral (#FE9B7B)
- `--color-accent-2`: Teal
- `--color-neutral-*`: Grau-Skala (100-900)
- `--color-success` / `--color-warning` / `--color-danger`

**Typografie:**
- `--font-heading`: Manrope
- `--font-body`: Inter / system-ui
- `--font-mono`: JetBrains Mono

**Spacing:** 4px Grid: 4/8/12/16/24/32/48/64/96/128
**Radius:** 6px / 10px / 16px / 50%
**Motion:** 150ms / 250ms / 400ms

### 9.2 Design-Qualitätsregeln
- Nur Komponenten aus `/packages/ui`
- Maximal 3 CTA-Typen (Primary/Secondary/Text)
- WCAG 2.1 AA Mindeststandard
- Mobile-First, Dark-Mode-kompatibel

---

# TEIL VII: TECH-STACK (aus v1.1, aktualisiert)

## 10. Tech-Stack

### 10.1 Aktueller Stack (NeXifyAI 2026)

| Kategorie | Tool | Status |
|---|---|---|
| Frontend | React 18 SPA (CRA) | ✅ Live |
| Backend | FastAPI (Python 3.11) | ✅ Live |
| Datenbank | Supabase PostgreSQL + MongoDB (Übergang) | 🔄 Migration |
| Auth | Supabase GoTrue + JWT Legacy | ✅ Dual-Mode |
| LLM | OpenRouter (deepseek/deepseek/deepseek-v4-flash) | ✅ |
| Hosting | Vercel (Frontend) + VPS (Backend) | ✅ |
| CI/CD | GitHub Actions + Vercel Auto-Deploy | 🔄 Minimal |
| Monitoring | Watchdog v2.0 + Health-Endpoint | ✅ |

### 10.2 Ziel-Stack (gemäß DOS)

| Kategorie | Ziel | Priorität |
|---|---|---|
| Frontend | Next.js (App Router) + TailwindCSS + shadcn/ui | Should |
| CMS | Directus/Strapi oder MDX | Should |
| Automation | Vercel Cron + FastAPI Routes + Supabase Edge Functions | Must |
| Analytics | PostHog oder Plausible + Microsoft Clarity | Must |
| CI/CD | Vollständige Quality Gates | Must |

---

# TEIL VIII: EVENT-TAXONOMY & AUTOMATION (aus v1.1)

## 11. Event-Taxonomy

### 11.1 Pflicht-Events

| Event | Beschreibung | Pflichtfelder |
|---|---|---|
| `page_view` | Seitenaufruf | url, referrer, timestamp |
| `cta_click` | CTA-Button geklickt | id, location, label |
| `scroll_depth` | Scroll-Tiefe | percent (25/50/75/90) |
| `pricing_view` | Pricing-Seite | url, segment |
| `plan_select` | Preisplan ausgewählt | plan_id, plan_name |
| `form_start` | Formular begonnen | form_id, form_type |
| `form_submit` | Formular abgeschickt | form_id, success |
| `form_error` | Formular-Fehler | form_id, field, error_type |
| `abandon_form` | Formular abgebrochen | form_id, last_field |

### 11.2 Event-Transport-Policy
- Events sind append-only
- Keine PII im Klartext
- Zod-Validierung
- Breaking Changes → neue Version (events/v2)

## 12. Trigger & Automations-System

### 12.1 Trigger-Kategorien
Verhaltens-Trigger · Intent-Trigger · Abbruch-Trigger · Timing-Trigger · KPI-Trigger · System-Trigger

### 12.2 Standard-Mappings

| Trigger | Auto-Action 1 | Auto-Action 2 |
|---|---|---|
| `pricing_view` + kein `plan_select` (24h) | E-Mail: Vergleich + Case Study | CRM: Interest-Flag |
| `form_start` + `abandon_form` (2h) | E-Mail: Reminder | Slack: Sales informieren |
| `returning_user` + `pricing_view` ≥ 2 | E-Mail: Fit-Check-Angebot | CRM: Hot-Lead |
| `demo_request` | CRM: Lead anlegen | Sales: Task + Reminder |

---

# TEIL IX: CI/CD (aus v1.1, erweitert)

## 13. CI/CD-Gesamtsystem

### 13.1 Branching-Strategie

| Branch | Verwendung |
|---|---|
| `main` | Production-ready. Kein Direct Push. |
| `develop` | Integration Branch (optional) |
| `feat/*` | Feature-Entwicklung |
| `fix/*` | Bugfixes |
| `chore/*` | Dependency Updates |
| `release/*` | Release-Vorbereitung |

### 13.2 PR-Pflicht-Inhalt
- Zielbeschreibung + Funnel-Zuordnung
- Risikoabschätzung (Low/Medium/High)
- Migrations-Hinweise
- UI-Screenshots (Before/After)
- Tracking-Änderungen
- Tests oder Begründung

### 13.3 Quality Gates (müssen grün sein für Merge)
- Lint: 0 Fehler
- Typecheck: 0 Fehler
- Unit Tests: grün (Coverage ≥ 80%)
- Build: erfolgreich
- Dependency Audit: 0 kritische CVEs
- Secret Scan: 0 Findings
- Performance: LCP < 2.5s, CLS < 0.1
- Bundle Size: im Budget

### 13.4 CI für inhaltliche Qualität
- H1-Struktur geprüft
- CTA-Vorhandensein
- Copy-Compiler-Vollständigkeit
- Claim-Scopes dokumentiert
- Glossar-Konsistenz
- Broken-Links-Prüfung

---

# TEIL X: SECURITY & PERFORMANCE (aus v1.1)

## 14. Security & Compliance

### 14.1 Basis-Sicherheitsstandard
- HTTPS überall, HSTS gesetzt
- CSP (Content Security Policy)
- RBAC (Role-Based Access Control)
- 2FA/MFA für Admin-Zugänge
- Secrets Management (nie in Git)
- Dependency Scanning (automatisch)
- Secret Scanning (Gitleaks/Trufflehog)

### 14.2 Erhöhter Standard (B2B/Enterprise)
- AVV vor Produktiv-Deployment
- DSGVO-Dokumentation (VVT)
- DSFA bei risikoreichen Verarbeitungen
- Incident Response Plan
- Backup-Konzept (RPO/RTO definiert)
- Penetration-Test (jährlich bei Enterprise)

## 15. Performance-Standards

| Metrik | Soll | Konsequenz |
|---|---|---|
| LCP | < 2.5s | Deployment-Warnung/Blocker |
| CLS | < 0.1 | Deployment-Warnung |
| TTFB | < 0.8s | Server-Optimierung |
| Page Size | < 2 MB | Bundle-Optimierung |
| Lighthouse | ≥ 85 | Deployment blockiert |

---

# TEIL XI: KPI & QUALITÄTS-LOOP (aus v1.1)

## 16. KPI-System

### 16.1 SaaS-KPIs
MRR · CAC · LTV · Churn Rate · Demo-to-Close · Trial-to-Paid · NPS

### 16.2 Shop-KPIs
Conversion Rate · AOV · ROAS · Cart Abandonment · Repeat Purchase · Refund Rate

### 16.3 B2B Lead-KPIs
CPL · Lead-to-Meeting · Meeting-to-Deal · Deal Size · Sales Cycle Length

### 16.4 Website-KPIs
Organic Traffic · CTA CTR · Scroll Depth · Bounce Rate · Pages/Session · Demo Conversion

## 17. Qualitäts-Loop (Closed Loop)

1. **Messen:** KPIs, Events, Heatmaps laufend erfassen
2. **Diagnose:** Engpass im Funnel identifizieren
3. **Hypothese:** Testbare These formulieren
4. **Experiment:** A/B-Test mit klarer Laufzeit
5. **Auswerten:** Statistisch signifikant?
6. **Rollout:** Gewinner für alle Nutzer
7. **Automatisieren:** Optimierung automatisch ausrollen
8. **Standardisieren:** Pattern ins Designsystem aufnehmen
9. **Dokumentieren:** Ergebnis, Learnings, KPI-Impact
10. **Wiederholen:** Nächsten Engpass identifizieren

---

# TEIL XII: ANWENDUNGSLEITFADEN (aus v1.1)

## 18. Leitfaden je Projekttyp

### Interne Produkte
- Maximale Automatisierung, alle CI-Checks, vollständiger Loop
- Designsystem-First, Tracking-First

### Agenturprojekte
- Standard-CI + Kunden-Freigabe-Gate
- Scope-Dokumentation + Handover

### B2C Kunden
- Conversion-Fokus, Performance-Priorität, Mobile-First
- Tracking-intensiv, Trust-Elemente

### B2B Kunden
- Trust-Seiten, ROI-Dokumentation, Lead-Qualität
- Erhöhter Review-Standard (2 Reviewer)

### Enterprise
- Audit-ready, vollständige Compliance-Dokumente
- Security-Review, Penetration-Test, E2E-Tests

### White-Label / Partner
- Theme-Fähigkeit, vollständige API-Dokumentation
- Onboarding-Dokumentation für Selbstständigkeit

## 19. Definition of Done

### Technisch
- Lint/Typecheck: 0 Fehler
- Unit Tests: grün (Coverage ≥ 80%)
- Build: erfolgreich
- Dependency Audit: 0 kritische CVEs
- Secret Scan: 0 Findings
- Performance: LCP < 2.5s, CLS < 0.1

### Inhaltlich
- 8-Stufen Copy-Compiler vollständig
- Claims mit Scope dokumentiert
- CTA vorhanden
- Interne Verlinkung systematisch

### Design
- Nur Komponenten aus `/packages/ui`
- Responsive geprüft
- WCAG 2.1 AA eingehalten

### Governance
- Dokumentiert: Ziel, Funnel, KPI, Risiko
- Review: min. 1 Approver
- Changelog + ADR (bei Architektur)
- Rollback dokumentiert

---

# TEIL XIII: ERWEITERUNGSREGELN (aus v1.1)

## 20. Governance & Erweiterung

### Erweiterungsregeln
- Nur mit Begründung, Dokumentation, Architekturprüfung
- Eigenentwicklung nur wenn kein Open-Source-Template existiert
- Framework-Updates versioniert (SemVer)

### Entscheidungsfindung
- Technische Architektur: NeXifyAI (KI-Lead) + Technical Lead
- Security/Compliance: Security Officer + Legal
- Design/Brand: Design Lead + CEO
- Strategie: CEO

---

# TEIL XIV: AI AGENT OPERATING LAYER (NEU v2.0 – Kapitel 21)

## 21. AI Agent Operating Layer

### 21.1 Geltungsbereich

Dieses Kapitel regelt den Betrieb aller KI-Agenten im NeXifyAI-Ökosystem:
- **NeXifyAI (Hermes Agent)** – Lead Agent, CLI + Admin Chat
- **9 Fach-Agenten** – intake, research, outreach, offer, planning, finance, support, design, qa
- **Subagenten** – von NeXifyAI gespawnte temporäre Agenten
- **Cron-Agenten** – autonom via Scheduler ausgeführte Tasks

### 21.2 Agent-Rollen & Hierarchie

```
CEO (Pascal) — Letztentscheidung
    │
NeXifyAI (Lead Agent) — Architektur, Orchestrierung, Governance
    │
    ├── Fach-Agenten (9) — Spezialisierte Aufgaben
    ├── Subagenten (spontan) — Isolierte Einmal-Tasks
    └── Cron-Agenten (scheduled) — Wiederkehrende Prüfungen
```

### 21.3 Tool-Permissions-Matrix

| Agent-Typ | Terminal | File R/W | Network | Browser | GitHub | SSH | Max Iterations |
|-----------|----------|----------|---------|---------|--------|-----|-----------------|
| Lead Agent | ✅ Full | ✅ Full | ✅ Full | ✅ | ✅ | ✅ | Unbegrenzt |
| Fach-Agenten | ✅ | ✅ R/O | ✅ API | ❌ | ❌ | ❌ | 25 |
| Subagenten | ✅ | ✅ R/W | ✅ | ✅ | ✅ | ⚠️ Restr. | 50 |
| Cron-Agenten | ✅ | ✅ R/W | ✅ | ❌ | ❌ | ❌ | 30 |

### 21.4 Prompt-Governance

- **System-Prompts** sind im Repo versioniert (`/packages/config/prompts/`)
- **Prefill.md** enthält den ZWANGSBEFEHL-Header (unveränderlich via `preserve_zwangsbefehl_header()`)
- **Kein Prompt-Injection:** User-Input wird vor Einbettung in Prompts escaped
- **Model-Pinning:** Lead Agent nutzt `deepseek/deepseek/deepseek-v4-flash`, Subagenten `deepseek/deepseek-v4-flash`
- **Fallback-Chain:** OpenRouter → DeepSeek Direct → Emergent LLM

### 21.5 Context-Injection & Retrieval-Regeln

| Ebene | Quelle | Priorität |
|---|---|---|
| 1. Brain DB | SQLite `/opt/data/brain/brain.db` | Hoch |
| 2. Qdrant | Vector Store (container-isoliert) | Mittel |
| 3. Open Notebook | API auf Port 32772 | Mittel |
| 4. Session-Search | Vergangene Konversationen | Niedrig |
| 5. Skills (153) | `/opt/data/skills/` | Bei Bedarf |

**Injection-Reihenfolge:** Brain → Skills → Notebook → Sessions

### 21.6 Model-Selection-Rules

| Aufgabe | Modell | Grund |
|---------|--------|-------|
| Architektur, DOS-Compliance | deepseek/deepseek/deepseek-v4-flash | Höchste Reasoning-Qualität |
| Code-Generierung | deepseek/deepseek/deepseek-v4-flash | Präzision |
| Einfache Queries, Health-Checks | deepseek/deepseek-v4-flash | Kosten ($0.14/M vs $1.40/M) |
| Subagenten (isoliert) | deepseek/deepseek-v4-flash | Kosteneffizienz |
| E-Mail-Autoreplies | deepseek/deepseek-v4-flash | Schnell, günstig |

### 21.7 Human-Override-Policy

- **CEO-Override:** Pascal kann jede Agent-Entscheidung überschreiben
- **Immediate Stop:** Befehl "STOP" oder "HALT" → alle Agent-Aktionen pausieren
- **Approval-Modus:** `approvals.mode=off` (Standard) — keine Rückfragen
- **Kritische Aktionen:** SSH zu Production, GitHub Force-Push, DB-Schema-Änderungen → Log-Pflicht

### 21.8 Hallucination-Policies

- **Claims erfordern Scope:** Keine unbelegten Behauptungen
- **Unsicherheit deklarieren:** "Nicht verifiziert" / "Basierend auf Brain-Daten vom [Datum]"
- **Source-Linking:** Jede Behauptung verlinkt auf Quelle (Brain, Notebook, externe URL)
- **Confidence-Scoring:**
  - HIGH: Durch 2+ Quellen bestätigt + im Repo verankert
  - MEDIUM: Eine Quelle + plausible aber unbestätigt
  - LOW: Inferenz, keine direkte Quelle

### 21.9 Memory-Write-Policies

- **brain_conclude()** bei: Korrekturen, Entscheidungen, Learnings, Pascal-Präferenzen
- **Kein Memory für:** Task-Progress, temporäre TODOs, triviale Fakten
- **Skill-Erstellung:** Nach jedem komplexen Task (5+ Tool-Calls) oder neuem Workflow
- **Skill-Patching:** Sofort wenn Skill veraltet/fehlerhaft — nicht warten

### 21.10 Agent-Selbstoptimierung

- **Wöchentlicher Self-Review:** Analyse der eigenen Effizienz (Tool-Calls/Task, Fehlerquote, Kontext-Nutzung)
- **Skill-Optimierung:** Ungenutzte Skills archivieren, fehlerhafte patchen
- **Prompt-Tuning:** Prefill.md monatlich auf Aktualität prüfen
- **Cron-Performance:** Job-Execution-Zeiten tracken, Timeouts anpassen

---

# TEIL XV: DATENARCHITEKTUR (NEU v2.0)

## 22. Datenarchitektur

### 22.1 Source of Truth pro Datenkategorie

| Kategorie | Primary Source | Secondary |
|---|---|---|
| Auth / Users | Supabase GoTrue | MongoDB (Legacy) |
| Business-Daten | Supabase PostgreSQL | MongoDB (Migration) |
| Vektordaten | Qdrant | SQLite Brain |
| Agent-Memory | Brain DB (SQLite) | Qdrant |
| Dokumente / Storage | Supabase Storage | Lokal |
| Config / Secrets | .env (Server) | GitHub Secrets |
| Logs | /var/log/nexifyai-*.log | — |

### 22.2 Schema-Governance (Supabase)
- Snake_case für Tabellen/Spalten
- Jede Tabelle hat `id` (UUID), `created_at`, `updated_at`
- Foreign Keys mit `ON DELETE`-Regel dokumentiert
- Migrations-Skripte in `/ops/infra/migrations/`
- Kein direktes `ALTER TABLE` ohne Migrations-Skript

### 22.3 Backup & Retention
- **Brain DB:** Täglich nach Supabase Storage + lokal
- **Qdrant:** Wöchentlicher Snapshot
- **PostgreSQL:** Supabase Point-in-Time Recovery (7 Tage)
- **Logs:** 30 Tage Retention, dann Archiv

---

# TEIL XVI: API-STANDARDS (NEU v2.0)

## 23. API-Standards

### 23.1 REST-Konventionen

**URL-Struktur:** `/api/v1/{resource}/{id}`
**Methoden:** GET (read), POST (create), PUT (update), DELETE (remove)
**Pagination:** `?page=1&limit=50` — Response enthält `total`, `page`, `pages`

### 23.2 Standard-Fehler-Schema

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Menschlich lesbare Beschreibung",
    "details": [
      {"field": "email", "reason": "Ungültiges Format"}
    ],
    "request_id": "req_abc123",
    "timestamp": "2026-05-08T12:00:00Z"
  }
}
```

**HTTP-Statuscodes:**
- 200: Erfolg
- 201: Created
- 400: Validation Error
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 429: Rate Limit
- 500: Internal Server Error

### 23.3 Auth-Header
- `Authorization: Bearer {jwt_token}` (User-Auth)
- `X-API-Key: nxa_live_{...}` (Programmatischer Zugriff)

### 23.4 OpenAPI-Pflicht
- Jeder Route-Handler hat `@router.get(..., response_model=...)` mit Pydantic-Modell
- FastAPI generiert automatisch `/docs` (Swagger) und `/redoc`
- OpenAPI-Spec wird bei CI validiert (kein Merge ohne valide Spec)

---

# TEIL XVII: INCIDENT-MANAGEMENT (NEU v2.0)

## 24. Incident-Management

### 24.1 Severity-Levels

| Level | Definition | Response-Zeit | Eskalation |
|---|---|---|---|
| SEV0 | Komplett-Ausfall (Backend down, Website down) | 15 Min | CEO + DevOps |
| SEV1 | Kritische Funktion gestört (Auth, Payment) | 30 Min | DevOps |
| SEV2 | Teilausfall (Ein Feature, Performance ↓) | 2 Std | DevOps |
| SEV3 | Minor (Cosmetic, Non-Critical) | 24 Std | Issue-Tracker |
| SEV4 | Observation (Monitoring-Warnung) | Nächster Workday | — |

### 24.2 On-Call-Prozess
1. Watchdog erkennt Ausfall → Log-Eintrag
2. NeXifyAI prüft Health-Endpoint
3. Bei SEV0/SEV1: E-Mail an Pascal
4. Root-Cause-Analyse (RCA)
5. Fix + Deploy + Verifikation
6. Postmortem-Dokument in `/docs/incidents/YYYY-MM-DD-sevX-title.md`

### 24.3 Postmortem-Template

```markdown
# Incident Postmortem: [Titel]

**Datum:** YYYY-MM-DD
**Severity:** SEV0-4
**Dauer:** [Start] – [Ende] (XX Min)
**Autor:** [Rolle]

## Zusammenfassung
[Ein-Satz-Beschreibung]

## Timeline
- HH:MM — Erste Erkennung
- HH:MM — Diagnose
- HH:MM — Fix deployed
- HH:MM — Verifikation

## Root Cause
[Technische Ursache]

## Impact
- Betroffene Nutzer: N
- Datenverlust: Ja/Nein
- Finanzieller Schaden: €X

## Resolution
[Was wurde getan]

## Prevention
- [ ] Maßnahme 1
- [ ] Maßnahme 2
```

---

# TEIL XVIII: FINOPS (NEU v2.0)

## 25. FinOps / Cost Governance

### 25.1 Budget-Thresholds (monatlich)

| Ressource | Budget | Warnung bei | Alarm bei |
|---|---|---|---|
| OpenRouter API | $500 | 80% ($400) | 100% ($500) |
| Vercel Pro | $20 | — | Überschreitung |
| Supabase | $25 | — | Überschreitung |
| Hostinger VPS | $15 | — | — |
| **Gesamt** | **$560** | **80%** | **100%** |

### 25.2 Kosten-Attribution
- **Pro Tenant:** API-Calls pro Kundenprojekt tracken
- **Pro Feature:** Chat-Messages, E-Mail-Versand getrennt messen
- **KI-Token-Verbrauch:** Pro Modell + Pro Agent loggen

### 25.3 Scaling-Policies
- Auto-Scaling: Nicht aktiv (Single-VPS)
- Warnung: Bei >80% Disk/RAM/CPU
- Vendor-Evaluation: Jährlicher Preisvergleich

---

# TEIL XIX: TESTING (NEU v2.0)

## 26. Testing-Architektur

### 26.1 Test-Pyramide

| Ebene | Tool | Umfang |
|---|---|---|
| Unit | pytest (Backend), Jest (Frontend) | ≥ 80% Coverage |
| Integration | pytest + TestClient | Alle API-Endpoints |
| E2E | Playwright | Kritische User-Flows |
| Contract | Pact | API-Verträge |
| Visual Regression | Percy/Chromatic | UI-Komponenten |
| Performance | k6/Locust | Unter Last |
| Security | OWASP ZAP | Monatlich |

### 26.2 Test-Pflichten
- **Jeder PR:** Unit + Integration Tests
- **Jeder Release:** E2E Smoke Tests
- **Monatlich:** Visual Regression + Security Scan
- **Quartalsweise:** Load Testing

---

# TEIL XX: MULTI-TENANT (NEU v2.0)

## 27. Multi-Tenant-Architektur

### 27.1 Tenant-Isolation
- **Daten:** Separate Supabase-Schemas oder Row-Level-Security
- **Config:** Tenant-Config in `/packages/config/tenants/{tenant_id}.yaml`
- **Feature-Flags:** Pro Tenant aktivierbar

### 27.2 RBAC-Differenzierung

| Rolle | Rechte |
|---|---|
| Tenant-Admin | Vollzugriff auf Tenant-Daten |
| Tenant-User | Lesen + eigene Daten schreiben |
| Tenant-Viewer | Nur Lesen |

---

# TEIL XXI: KNOWLEDGE-SYSTEM (NEU v2.0)

## 28. Knowledge-System Operationalisierung

### 28.1 Schema

- `/knowledge/` – Markdown-Dateien mit YAML-Frontmatter
- Tags: `[brain, dos, skill, architecture, security, devops, lesson]`
- Lifecycle: `draft → reviewed → published → archived`

### 28.2 Embedding-Strategie
- Primär: Qdrant (Vector Store)
- Fallback: SQLite Brain DB
- Sync: Alle 30 Min via brain-sync Cron

---

# TEIL XXII: LEGAL (NEU v2.0)

## 29. Legal Layer

### 29.1 Cookie-Governance
- Consent-Taxonomie: essential, functional, analytics, marketing
- Cookie-Banner mit Opt-in (DSGVO-konform)
- Consent-Log in Supabase

### 29.2 AI-Disclosure
- Transparenzhinweis auf KI-generierte Inhalte
- Keine automatisierte Einzelfallentscheidung ohne Human-Review

### 29.3 Lizenz-Compliance
- Open-Source-Scan via `license-checker` vor jedem Merge
- Liste genehmigter Lizenzen: MIT, Apache 2.0, BSD, ISC
- Blockierte Lizenzen: GPL (viral), AGPL, SSPL

---

# TEIL XXIII: PRODUKTMANAGEMENT (NEU v2.0)

## 30. Produktmanagement-System

### 30.1 RICE-Priorisierung

| Faktor | Beschreibung |
|---|---|
| Reach | Wie viele Nutzer betroffen? (1-10) |
| Impact | Wie groß ist der Effekt? (0.25/0.5/1/2/3) |
| Confidence | Wie sicher sind wir? (20%/50%/80%/100%) |
| Effort | Person-Tage (1-100) |

### 30.2 Feature-Lifecycle
`idea → spec → development → testing → release → live → deprecated → sunset`

---

# TEIL XXIV: SYSTEM HEALTH (NEU v2.0)

## 31. System Health Definition

### 31.1 Zusammengesetzter Health-Score

| Komponente | Gewicht | Messung |
|---|---|---|
| Uptime (30 Tage) | 25% | Watchdog / Better Uptime |
| Error Rate | 20% | Backend-Logs |
| Latenz (P95) | 15% | Health-Endpoint |
| Deploy Frequency | 10% | GitHub |
| MTTR | 10% | Incident-Log |
| Security Score | 10% | CVE-Scanner |
| Conversion Rate | 10% | Analytics |

**Berechnung:** Gewichteter Durchschnitt → Score 0-100
**Alarm:** Score < 70 → Auto-Ticket + Pascal-E-Mail

---

# TEIL XXV: MARKETPLACE (NEU v2.0)

## 32. Marketplace-/Template-System

### 32.1 Template-Registry
- `/templates/` – Wiederverwendbare Projekt-Blueprints
- Compatibility-Matrix: Welches Template für welchen Projekttyp
- Approved-Integrations-Liste in `/packages/config/integrations.json`

---

# TEIL XXVI: MIGRATION & DEPRECATION (NEU v2.0)

## 33. Migrations- & Deprecation-Policies

### 33.1 API-Deprecation
- **Ankündigung:** 90 Tage vor Sunset
- **Warning-Header:** `Deprecation: true` + `Sunset: [Datum]`
- **Migration-Window:** 90 Tage
- **Breaking Changes:** Nur mit MAJOR-Version

### 33.2 Version-Support-Matrix
- **Aktuelle Version:** Voll-Support
- **Vorherige MAJOR:** Security-Patches (6 Monate)
- **Älter:** Kein Support

---

# TEIL XXVII: ANHANG

## A. Quick-Reference: Pflicht-Tech-Stack

| Kategorie | Tool |
|---|---|
| Frontend | React 18 SPA → Next.js (Ziel) |
| Backend | FastAPI (Python 3.11) |
| Datenbank | Supabase PostgreSQL |
| Auth | Supabase GoTrue |
| LLM | OpenRouter (deepseek/deepseek/deepseek-v4-flash) |
| Hosting | Vercel (FE) + VPS (BE) |
| CI/CD | GitHub Actions |

## B. Funnel-Schritte

| Schritt | Beschreibung |
|---|---|
| Awareness | Nutzer kennt Problem, sucht Lösungen |
| Education | Nutzer versteht Lösung, evaluiert |
| Evaluation | Nutzer vergleicht Optionen |
| Conversion | Nutzer handelt (Kauf/Demo/Lead) |
| Onboarding | Erste Wert-Erfahrung |
| Retention | Loyalität, Upsell, Community |

## C. DOS-Versionen

| Version | Datum | Änderungen |
|---|---|---|
| v1.0 | 2026-01 | Initial |
| v1.1 | 2026-02-19 | Finales Gesamtkonzept |
| **v2.0** | **2026-05-08** | **+15 Kapitel: Rollen, ADR, AI-Governance, Daten, API, Incident, FinOps, Testing, Multi-Tenant, Knowledge, Legal, Product, Health, Marketplace, Migration** |

---

**System-Status: NeXifyAI DOS v2.0 — AKTIV UND VERBINDLICH**

Nächste geplante Revision: DOS v2.1 — nach vollständiger Implementierung aller 15 Lücken.
Letzte Änderung: 2026-05-08 durch NeXifyAI (Lead Agent).