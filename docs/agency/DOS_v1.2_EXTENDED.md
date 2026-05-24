# NeXifyAI DOS v1.2 Extended

Version: 1.2  
Stand: 2026-05-24  
Klassifikation: INTERN - VERTRAULICH  
Quelle: Agenturvorgaben + System-Migration-Erkenntnisse  
Erweiterung zu: DOS v1.1 (2026-02-19)

DOS v1.2 erweitert DOS v1.1 vollständig. Nichts aus DOS v1.1 wird entfernt. Alle v1.2-Erweiterungen sind verbindlich.

## v1.2 A — AI-Governance

- Brain-first. Ohne Brain keine Arbeit.
- Ein zentrales Brain statt XX-Brains.
- Semantisches Gedächtnis für Fakten, Architektur, Regeln.
- Episodisches Gedächtnis für Ereignisse, Incidents, Entscheidungen.
- Prozedurales Gedächtnis für Workflows, Recovery, Vorgehensweisen.
- Lessons Learned sind Pflicht.
- Prevention Rules sind Pflicht.
- Fehler dürfen nicht zweimal passieren.
- Resource-first vor jeder neuen Lösung.
- Runtime Evidence ist Pflicht.
- Sourcecode ist nicht Runtime.
- Keine Fertigmeldung ohne Nachweis.
- Keine lokale Erledigtmeldung akzeptieren.
- Jede AI-Lösung muss validierte Erkenntnisse zurück ins Brain schreiben.

## v1.2 B — Goose-/Agenten-Governance

- Goose ist Primärintelligenz.
- Cline ist Dead Legacy.
- Anton ist Legacy/entfernt.
- Hermes ist Legacy/entfernt.
- Oracle/Autopilot-Reste sind Legacy.
- Diese Systeme nur noch readonly für History, Lessons Learned, Wissenstransfer.
- Keine neue Cline-Integration.
- Keine neue Anton-/Hermes-/Oracle-Integration.
- Keine lokalen Fake-Skills.
- claude-code-templates ist Master-Skill-System.
- Skills müssen kombiniert werden.
- Subagenten-/Reviewer-Pflicht bei systemweiten Aufgaben.
- Intent Reconstruction ist Pflicht.
- Human Expectations Model ist Pflicht.
- Completion Definition mit Evidence ist Pflicht.
- Keine Fertigmeldung ohne Brain-, Repo-, Runtime- und Test-/Security-Nachweis.

## v1.2 C — Skill-/Agent-/MCP-Governance

- Master-Skill-Registry ist Pflicht.
- Skill-Kompositions-Pipeline ist Pflicht: Prozess -> Architektur -> Domain/Implementierung -> QA/Security/Infra.
- Hooks und MCPs nur kontrolliert.
- MCP/Tool-Security prüfen.
- Tool-/Prompt-Injection-Risiken nicht ignorieren.
- Wenn Skill nicht im Master existiert: keine lokale Erfindung.
- Stattdessen nearest-master-match suchen, Abweichung melden, Bridge nutzen.
- claude-code-templates vollständig ausschöpfen: Skills, Agents, Commands, Hooks, MCPs, Settings, Templates, Installer, Workflows, Beispiele, Patterns, Konventionen, Automatisierungen.

## v1.2 D — Plattform-Governance

- nexifyai-platform ist zentrales Repo.
- GitHub ist Source of Truth.
- Vercel Deployment Evidence ist Pflicht.
- Supabase Governance ist Pflicht.
- Cloudflare/DNS/Tunnel Governance ist Pflicht.
- 9Router ist kritische Core-Infrastruktur.
- Brain/Qdrant/9Router/Traefik/Cloudflare niemals gefährden.
- Keine Shadow-Systeme.
- Keine lokalen Sonderlösungen.
- Keine manuell zusammengeklickten Deployments als Wahrheit.
- Infrastruktur ist Produktbestandteil.

## v1.2 E — Vollständiges NeXifyAI-Leistungsmodell

NeXifyAI ist:
1. AI-Agentur
2. Webentwicklungsagentur
3. Plattform-/Portal-/App-Entwicklungspartner
4. Automatisierungsanbieter
5. AI-Service-Layer-Anbieter
6. Betreiber eigener NeXifyAI Modell-/API-Plattform
7. Betreiber zentraler Kunden-, Admin-, Billing-, Usage-, Docs-, Support- und Guthabenprozesse

Leistungen: Webseiten, Plattformen, Portale, Apps, Automatisierungen, KI-Leistungen, NeXifyAI Modell-/API-Plattform, Betrieb und Wartung.

## v1.2 F — Kundenprojekt-Golden-Path

Kundenprojekte nach denselben Standards wie interne Systeme. Jedes Kundenprojekt erhält eigenes Repo, eigene Deployment-Struktur, eigene Secrets, eigene DB, eigene CI/CD. Keine Vermischung mit Core. Definierte Schnittstellen zum zentralen Kundenportal. KI-Nutzung über Guthabenlogik und NeXify API Keys. Kein Provider-Key beim Kunden.

Pfad: Discovery -> Konzept -> Architektur -> Design/Text -> Umsetzung -> KI-Integration -> QA/Security -> Übergabe/Betrieb.

## v1.2 G — Tech-Stack 2026

Standard: Next.js App Router, React, TypeScript, Supabase/Postgres, Vercel, GitHub Actions, Cloudflare/DNS, Tailwind/shadcn, n8n, PostHog/Plausible/Clarity/Sentry/Uptime. Abweichungen nur mit ADR und Resource-first-Prüfung.

## v1.2 H — Compliance-Realitätsregel

ISO/DIN/Normen nur als erfüllt markieren, wenn konkrete Anforderungen und Nachweise vorhanden. Keine falschen Compliance-Behauptungen. Jede Vorgabe in prüfbare Gates übersetzen. Jede Compliance-Aussage braucht Quelle, Status und Evidence.

## v1.2 I — Automatische Aktualisierung

DOS ist lebendes System. Neue Erkenntnisse erweitern DOS. Keine Erkenntnis geht verloren. Jede Framework-Änderung erzeugt Changelog. Neue Lessons Learned erzeugen Prevention Rules.
