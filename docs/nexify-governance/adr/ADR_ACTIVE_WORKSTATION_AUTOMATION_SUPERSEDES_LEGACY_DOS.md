# ADR: Active Workstation/Automation Supersedes Legacy Governance

**Status:** AKTIV — V1, 2026-06-10
**Owner:** Pascal Courbois / NeXify AI CEO
**Geltungsbereich:** NeXify AI Gesamtsystem

## Kontext

Im Repo existieren Governance-Aussagen, die Goose als Primärintelligenz setzen und Hermes/Oracle/Autopilot als Legacy beschreiben. Diese Aussagen kollidieren mit dem aktuellen aktiven Zielzustand der NeXify AI Plattform.

## Entscheidung

1. **NeXify AI ist das gesamte Agentur-Betriebssystem.** Kein Einzelwerkzeug ist Primärintelligenz.
2. **Die Workstation (NeXify AI Workspace) ist die zentrale Steueroberfläche** für Pascal, Tasks, Agenten und Automationen.
3. **Hermes Agent ist die technische Basis** der Workstation, nicht die sichtbare Zielmarke.
4. **Claude Code, Goose ACC/ACP, Goose CLI und weitere Agenten** sind spezialisierte Werkzeuge/Rollen innerhalb des NeXify-Systems, keine Primärintelligenzen.
5. **Primär ist der NeXify AI CEO / Orchestrator** mit Brain, Regelwerk, Policy Gate, 12 Teams, Dispatcher und Evidence-System.
6. **Automatik nur über kontrollierte Architektur** (Automation Controller → Policy Gate → Skill Router → Dispatcher → Execution).
7. **User-Chat-Driver** darf interne USER-Fortsetzungsnachrichten erzeugen, nur gekennzeichnet `[FORTSETZUNG — Automatisch fuer Pascal erzeugt]` und nur in erlaubten Sessions.
8. **Alte Legacy-Aussagen** werden archiviert oder durch dieses ADR übersteuert.

## Konsequenzen

- Legacy-Governance-Dokumente, die Goose als Primärintelligenz setzen, sind ab sofort nicht mehr führend.
- Dieses ADR hat Vorrang vor widersprüchlichen älteren Governance-Aussagen.
- Alle neuen Governance-Dokumente folgen dieser Entscheidungslinie.

## Status

- [x] ADR erstellt
- [ ] Legacy-Dokumente identifiziert und mit Verweis auf dieses ADR versehen
- [ ] Brain-Sync erfolgt

