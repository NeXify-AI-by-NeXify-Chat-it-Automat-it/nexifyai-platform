# ADR Template

```markdown
# ADR-NNN: Titel

**Status:** proposed | accepted | deprecated | superseded
**Datum:** YYYY-MM-DD
**Autor:** [Rolle]
**Stakeholder:** [Liste]

## Kontext
[Beschreibung des Problems/der Situation. Warum muss eine Entscheidung getroffen werden?]

## Problem
[Konkrete Fragestellung. Was ist die zu lösende Herausforderung?]

## Optionen
1. Option A: [Beschreibung]
   - Pro: [Vorteile]
   - Contra: [Nachteile]

2. Option B: [Beschreibung]
   - Pro: [Vorteile]
   - Contra: [Nachteile]

3. Option C: [Beschreibung] (optional)
   - Pro: [Vorteile]
   - Contra: [Nachteile]

## Entscheidung
[Gewählte Option mit Begründung. Warum wurde diese Option gewählt?]

## Konsequenzen
### Positiv
- [Vorteile, die sich aus der Entscheidung ergeben]

### Negativ
- [Trade-offs, Risiken, technische Schulden]

### Neutral
- [Seiteneffekte ohne klare Wertung]

## Rollback-Plan
[Wie kann die Entscheidung rückgängig gemacht werden? Welche Kosten/Zeit entsteht dabei?]

## Verweise
- [PR-Link]
- [Issue-Link]
- [Dokumentation]
- [Superseded by: ADR-XXX] (wenn deprecated/superseded)
```

## Lifecycle

```
proposed ──→ accepted ──→ deprecated ──→ superseded
                │
                └──→ (direkt superseded)
```

- **proposed:** ADR wurde erstellt, aber noch nicht genehmigt
- **accepted:** ADR ist genehmigt und verbindlich
- **deprecated:** ADR ist nicht mehr gültig, aber noch nicht ersetzt
- **superseded:** ADR wurde durch einen neueren ADR abgelöst (Verweis auf neuen ADR)

## Naming-Konvention

- Dateiname: `ADR-NNN-kurztitel-mit-bindestrichen.md`
- NNN: Fortlaufende Nummer (001–999), führende Nullen
- Titel: Kurz, prägnant, verständlich
- Bei Supersede: `superseded_by: ADR-XXX` im Kopf des alten ADR
- Nummern werden NICHT wiederverwendet

## Pflicht-ADRs (Initial)

| ADR | Titel | Status |
|---|---|---|
| ADR-001 | Einführung DOS v2.0 als verbindliches Betriebssystem | accepted |
| ADR-002 | Supabase als Primary Database | proposed |
| ADR-003 | OpenRouter als primärer LLM-Provider | proposed |
| ADR-004 | Monorepo-Struktur und Package-Grenzen | proposed |
| ADR-005 | API-Standardisierung (Error-Schema, OpenAPI) | proposed |
