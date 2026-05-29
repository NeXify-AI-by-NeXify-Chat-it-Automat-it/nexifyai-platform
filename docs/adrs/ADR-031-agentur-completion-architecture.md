# ADR-031: Agentur-Komplettabschluss Architektur-Entscheidungen
status: approved | date: 2026-05-29 | owner: goose

## Kontext
Der Agentur-Komplettabschluss (Übernacht-Build) brachte 12 Systeme auf Produktionsreife.
Dieses ADR dokumentiert die dabei getroffenen Architekturentscheidungen.

## Entscheidungen

### 1. Brain API als Source of Truth für System-State
- **Status:** Implementiert
- **Begründung:** Brain API (localhost:8420) liefert canonical Health + Store + Query.
  Qdrant (localhost:6333) ist der persistente Vektor-Store. Backup via 2. Qdrant-Instanz.
- **Konsequenz:** Einheitliche Health-Abfrage für alle 12 Systeme über /health-Endpoint.

### 2. Kong Gateway als API-Management-Layer
- **Status:** Implementiert
- **Begründung:** Kong (localhost:8000/8001) routet externen Traffic zu internen Services.
  Bietet Rate-Limiting, Auth-Plugin, Logging out-of-the-box.
- **Konsequenz:** Externe Consumer sehen nur Kong-Routen, nie interne Service-Ports.

### 3. Memory-Dreiteilung: Semantisch/Episodisch/Prozedural
- **Status:** Architektur definiert, Embedding-Pipeline via Qdrant
- **Begründung:** Drei Memory-Typen decken unterschiedliche kognitive Funktionen ab:
  Semantic (Fakten), Episodic (Ereignisse), Procedural (Workflows).
- **Konsequenz:** contextLoad() kombiniert alle drei für dynamischen Task-Kontext.

### 4. Quality-Gates via DOS v2.0 (17 Gates)
- **Status:** Implementiert
- **Begründung:** Jede Aufgabe durchläuft 17 definierte Gates vor Completion.
  Automatische Blocker bei fehlenden Docs/Tests/Security.
- **Konsequenz:** Kein Deployment ohne grüne Gates. Audit-Trail via Brain.

## Konsequenzen
- **Positiv:** Vollständige Rückverfolgbarkeit aller Architekturentscheidungen
- **Positiv:** Einheitliche Quality-Standards über alle 12 Systeme
- **Risiko:** Kong Single-Point-of-Failure (kein Failover auf Single VPS)
- **Mitigation:** Service-Discovery + Health-Checks für manuelles Failover

## Verweise
- DOS v2.0 (docs/DOS-v2.0.md)
- Operational Constitution E3.5 (docs/operational-constitution.md)
- Runtime Topology (docs/runtime-topology.md)