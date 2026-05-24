# NeXifyAI Digital Operating System (DOS) v1.1

Version: 1.1  
Stand: 2026-02-19  
Klassifikation: INTERN - VERTRAULICH  
Erstellt für: Pascal / NeXifyAI  
Zweck: Universelle, verbindliche Projektgrundlage für alle NeXifyAI-Projekte: interne Produkte, Agenturprojekte, B2C, B2B, Enterprise, White-Label.

## Systemmantra

Das Mantra gilt für jede Interaktion, jedes Projekt, jede Entscheidung.

- Retrieval first.
- Marketplace first.
- Open Source first.
- Template first.
- CI driven.
- Security validated.
- Verify gated.
- Zero Information Loss.
- Systemische Konsistenz.

Jede Entscheidung oder Änderung ist:
- kontextualisiert
- validiert
- architektur-konform
- CI-integriert
- reproduzierbar
- rollback-fähig
- versioniert
- auditierbar
- persistiert

Grundprinzip:
Keine isolierte Lösung.
Keine isolierte Installation.
Keine isolierte Erweiterung.
Keine isolierte Entscheidung.

Jede Interaktion folgt dem Pfad:
Kontext -> Konsistenz -> Validierung -> Architekturprüfung -> Umsetzung -> Persistenz -> CI -> Governance

## 1. Einleitung und Systemüberblick

Das NeXifyAI Digital Operating System ist das verbindliche, universelle Betriebssystem für alle Projekte unter der Marke NeXifyAI. Es gilt von internen Produkten über Agenturaufträge bis zu Enterprise-Kundenprojekten. Es ist kein loses Guideline-Dokument, sondern ein nicht verhandelbarer Systemstandard.

Anwendungsbereiche:
- Interne Produktentwicklung: NeXify Chat it, Automate it, Plattform-Core
- Agenturprojekte: Custom Builds, Kampagnenseiten, Repositorys
- B2C Kundenprojekte: Shops, Landingpages, Markenwebsites
- B2B Kundenprojekte: SaaS, Portale, Enterprise-Software
- White-Label / Partner: lizenzierte Lösungen, Whitelabel-Produkte

## 2. Systemkern und unverhandelbare Guardrails

### 2.1 Die 7 Guardrail-Prinzipien
1. Funnel-Zuordnung: Jede Seite, jedes Feature und jede Automation muss einem Funnel-Schritt zugeordnet sein.
2. Claims-Policy: Jede Zahl braucht Scope: Segment, Zeitraum, Bedingung, Messmethode. Sonst Beispielwert.
3. No One-Off UI: UI-Elemente nur über /packages/ui.
4. Tracking First: Jede kritische Aktion ist Event-basiert messbar vor Go-Live.
5. Loop-Automation: KPI unter Threshold -> Trigger -> Auto-Action -> Messung -> Entscheidung.
6. Dokumentationspflicht: Jede Implementierung mit Ziel, Funnel-Schritt, Trigger, KPI, Engpass, Ergebnis.
7. Modularität: Alle Komponenten austauschbar ohne Systembruch.

### 2.2 Fehlerbehandlungs-Reihenfolge
1. Stabilisieren (Root Cause isolieren, Schadensminimierung)
2. Root Cause finden
3. Secondary Issues identifizieren (Blast Radius)
4. Vollständig beheben
5. Erst danach: Neuerungen

### 2.3 Memory-Architektur: Zero Information Loss
Drei Ebenen: STATE (Systemzustand), KNOWLEDGE (Entscheidungen, Policies, Lessons), TODO (Aufgaben, Risiken).
Jeder Eintrag kategorisiert und verknüpft mit Server-IP, Policy-Version, Agent-Rolle, CI-Referenz.

## 3. Projektklassifikation
Typen: A SaaS/Plattform, B B2C Shop, C B2B Shop, D Hybrid, E Service/Consulting, F Plattform/Marketplace.

## 4. Zielgruppen-System: Universal Matrix
Drei Ebenen: strukturell (B2C/B2B/Enterprise/Partner/Investor), psychologisch, intentions-basiert.
Jede Zielgruppe erhält Segment-Einstiegsseite, Vertrauensseite, Entscheidungsseite, Conversion-Seite.

## 5. Website-Architektur: Universal Blueprint
8 Pflicht-Cluster: Entry/Start, Lösungen, Produkte, Zielgruppen, Preise, Ressourcen, Trust/Unternehmen, Conversion.
Interne Verlinkungsstrategie: Produktseite -> Use-Cases + Blog + Case Study.

## 6. Content-System und Copy-Compiler
8-Stufen: Kontext, Problem, Konsequenz, Lösung, Mechanik, Beweis, Nutzen, CTA.

## 7. Design-System
/packages/ui als versioniertes Paket. Design Tokens für Farben, Typografie, Spacing, Radius, Motion.
Pflicht-Komponenten: Header, Hero, Feature Grid, Benefits, Proof, Comparison Table, FAQ, Pricing Cards, Form, Footer.

## 8. Tech-Stack
Next.js App Router, TailwindCSS, shadcn/ui, Supabase, n8n, GitHub Actions, Vercel, PostHog/Plausible, Sentry.

## 9. Event-Taxonomy
Zentral in /packages/events. Baseline-Events: page_view, cta_click, form_start/submit/error, pricing_view, demo_request, signup, login, checkout, payment.

## 10. Trigger- und Automations-System
Trigger-Kategorien: Conversion, Usage, Billing, Support, Security, Performance, KPI, Onboarding, Retention, Recovery.
n8n Workflow-Standards: versioniert, Owner, Zweck, Trigger, Input, Output, Fehlerpfad.

## 11. CI/CD-Gesamtsystem
main geschützt. Feature Branches. PR mit Ziel, Scope, Tests, Security, Tracking, Rollback, Doku.
Quality Gates: Lint, Typecheck, Tests, Build, Security Scan, Secrets, Doku, Events.

## 12. Security und Compliance
Keine Secrets im Repo. Sichere Env-Verwaltung. Supabase RLS. Auth/Rollen dokumentiert. Input Validation. Rate Limiting.

## 13. Performance-Standards
Core Web Vitals: LCP gut, CLS gut, INP gut. Performance-Checkliste: Bilder, Fonts, Lazy Loading, SSR/ISR, Caching.

## 14. KPI-System
SaaS: MRR, ARR, Churn, Activation, Trial-to-Paid, CAC, LTV, Usage, Retention.
Shop: Conversion Rate, AOV, Cart Abandonment, Revenue.
B2B: Lead Conversion, Demo Requests, Qualified Leads, Close Rate.

## 15. Release-Management
SemVer. Release-Prozess: Scope -> Tests -> Security -> Build -> Deployment -> Rollback -> Monitoring -> Doku -> Nachmessung.

## 16. Qualitäts-Loop
Messen -> Engpass -> Hypothese -> Änderung -> Testen -> Messen -> behalten/verwerfen/iterieren -> dokumentieren.

## 17. Anwendungsleitfaden je Projekttyp
Siehe Abschnitt 17 im vollständigen Dokument.

## 18. Definition of Done
Technisch: Code, Typecheck, Lint, Tests, Build, Secrets, Security, Performance, Rollback, CI.
Inhaltlich: Copy-Compiler, Zielgruppe, Funnel, Claims, CTA, Verlinkung.
Design: Designsystem, No One-Off, Responsive, WCAG 2.1 AA, Brand, Dark Mode.
Tracking: Events, Payload, Trigger, n8n.
Governance: Doku, ADR, Release Notes, Inventar, Owner, Risiken, Lessons Learned.

## 19. Erweiterungsregeln und Governance
Neu nur bei klarem Zweck, Funnel, KPI, Ressourcen-Prüfung, Architekturverträglichkeit.
Eigenentwicklung nur nach Marketplace-, Open-Source-, Template-, Ressourcen-Prüfung.
DOS wird versioniert. Changelog bei Änderungen.

## 20. Anhang
Projekt-Start-Checkliste. Quick-Reference Funnel. Quick-Reference Tech-Stack. Monetarisierungs-Hebel.
