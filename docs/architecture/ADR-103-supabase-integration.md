# ADR-103: Supabase Integration

**Status:** proposed
**Datum:** 2026-05-22
**Autor:** NeXifyAI Architecture Team

## Kontext
NeXifyAI hat Supabase als primäre Datenbank (ADR‑002) migriert. IST‑Analyse zeigt: Service‑Role‑Key API‑Call schlägt fehl (`Invalid API key`), keine Schema‑Dokumentation sichtbar. RLS und Multi‑Tenant‑Policies müssen dokumentiert werden.

## Entscheidung
Erstelle C4‑Diagramme (Context, Container, Component) für Supabase‑Integration. Verbinde Supabase mit Multi‑Tenant‑Architektur, Auth (GoTrue), Storage und Realtime‑Push.

## Diagramme
### C4‑Context
```mermaid
C4Context
  title NeXifyAI – Supabase Integration Context
  Person(admin, "Admin", "Verwaltet Schema und RLS")
  Person(agent, "KI‑Agent", "Nutzt DB‑gestützte Funktionen")
  System(portal, "Admin‑Portal", "React SPA")
  System(brain, "Brain API", "Wissens‑System")
  System(OpenRouter, "OpenRouter Gateway", "AI‑Provider Gateway")
  System_Ext(supabase, "Supabase", "PostgreSQL + GoTrue + Storage + Realtime")
  Rel(admin, portal, "Verwaltet Schema", "HTTPS")
  Rel(portal, supabase, "SQL/REST", "RLS")
  Rel(agent, brain, "Queries", "HTTPS")
  Rel(brain, supabase, "Metadaten‑CRUD", "SQL")
  Rel(OpenRouter, supabase, "User‑Info", "REST")
```

### C4‑Container
```mermaid
C4Container
  title Supabase Container Diagram
  Person(admin, "Admin")
  Person(agent, "KI‑Agent")
  Container(spa, "Admin‑Portal", "React + Vite", "UI")
  Container(apiProxy, "Admin‑API‑Proxy", "FastAPI", "Zwischenschicht")
  Container_Boundary(sup, "Supabase Self‑Hosted") {
    Container(goTrue, "GoTrue", "Auth Service", "JWT‑Ausstellung, User‑Management")
    ContainerDb(postgres, "PostgreSQL", "Relational DB", "Schema‑Governance, RLS")
    Container(storage, "Storage API", "S3‑compatible", "Datei‑Ablage")
    Container(realTime, "Realtime", "WebSocket", "Daten‑Streaming")
  }
  Rel(spa, apiProxy, "JSON/HTTPS")
  Rel(apiProxy, goTrue, "Login / Token‑Refresh")
  Rel(apiProxy, postgres, "SQL (anon key)")
  Rel(agent, postgres, "SQL (service key)", "Intern")
  Rel(agent, storage, "Upload/Download", "Intern")
  Rel(realTime, spa, "Push‑Events", "WebSocket")
  Rel(realTime, agent, "Push‑Events", "WebSocket")
```

### C4‑Component (Schema Layer)
```mermaid
C4Component
  title Supabase Schema Components
  Container_Boundary(sup, "Supabase Schema") {
    ComponentDb(tenantsCol, "tenants", "PostgreSQL", "Mandanten‑Stammdaten")
    ComponentDb(usersCol, "auth.users", "GoTrue", "User‑Identitäten")
    ComponentDb(incidents, "incidents", "PostgreSQL", "VDS‑Incidents (ADR‑012)")
    ComponentDb(decisions, "decisions", "PostgreSQL", "Architecture‑Decisions")
    ComponentDb(policiesTbl, "policies", "PostgreSQL", "Governance‑Policies")
    Component(rlsPolicy, "RLS Policy Engine", "PostgreSQL RLS", "tenant_id‑based Row‑Filter")
  }
  Rel(rlsPolicy, tenantsCol, "Filtert")
  Rel(rlsPolicy, usersCol, "Filtert")
  Rel(rlsPolicy, incidents, "Filtert")
  Rel(rlsPolicy, decisions, "Filtert")
```

### C4‑Deployment
```mermaid
C4Deployment
  title Supabase Deployment
  Deployment_Node(k8s, "Kubernetes Cluster", "AWS EKS") {
    Deployment_Node(ds, "Supabase Pod", "Docker") {
      Container(postgres, "PostgreSQL", "Postgres 15")
      Container(goTrue, "GoTrue", "Auth")
      Container(storage, "Storage", "S3")
      Container(realtime, "Realtime", "WebSocket")
    }
  }
  Rel(postgres, goTrue, "Intern")
```

## Konsequenzen
- **Positiv:** Definierte Schema‑Strukturen mit RLS‑Policies sicherstellen Multi‑Tenant‑Isolation; explizite Service/Anon‑Key‑Verwendung klären.
- **Negativ:** RLS‑Debugging komplex; kein automatischer Test.
- **Neutral:** Supabase‑Self‑Hosted gibt volle Kontrolle, aber Maintenance‑Overhead.

## Nächste Schritte
1. Debugge Service‑Role‑Key und stelle korrekte Rolle/Passwort für Admin‑API‑Proxy sicher.
2. Erstelle Migration‑Files für `tenants`, `decisions`, `policies`.
3. Aktiviere RLS auf `auth.users` und `tenants`.
4. Füge `tenant_id`‑Spalte als Pflichtfeld zu bestehenden Tabellen hinzu.
5. Schreibe Audit‑Trigger für Schema‑Änderungen.
