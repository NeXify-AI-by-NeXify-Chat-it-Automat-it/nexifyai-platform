# ADR-102: OpenRouter Auth-Flow

**Status:** proposed
**Datum:** 2026-05-22
**Autor:** NeXifyAI Architecture Team

## Kontext
OpenRouter (`http://127.0.0.1:8420 (Brain API)`) ist AI‑Provider‑Gateway. Aktuell kein JWT‑Auth konfiguriert – `/api/providers` gibt *Unauthorized*, `JWT_SECRET` fehlt in Umgebung. Notwendig: durchgängiger Authentifizierungsfluss von Supabase‑Auth bis OpenRouter‑API.

## Entscheidung
Implementiere **C4‑Dynamic** (Sequenz‑Diagramm) für OpenRouter Auth‑Flow. Supabase GoTrue als Identity‑Provider, JWT mit `role`‑Claim, Tenant‑Scope in `tenant_id`‑Claim. OpenRouter prüft JWT vor jedem API‑Call.

## Diagramme
### C4‑Context
```mermaid
C4Context
  title OpenRouter Auth Flow Context
  Person(user, "Kunde / Admin", "Ruft Provider‑API auf")
  System(admin, "Admin‑Portal", "React SPA")
  System(OpenRouter, "OpenRouter Gateway", "AI‑Provider‑Gateway")
  System_Ext(supabase, "Supabase Auth", "GoTrue JWT‑Ausstellung")
  Rel(user, admin, "Loggt sich ein", "HTTPS")
  Rel(admin, supabase, "Login / Token‑Refresh")
  Rel(admin, OpenRouter, "Bearer‑JWT", "HTTPS/JSON")
```

### C4‑Container
```mermaid
C4Container
  title OpenRouter Container Diagram
  Person(user, "Kunde / Admin")
  Container(spa, "Admin‑Portal", "React + Vite", "UI für Provider‑Verwaltung")
  Container(apiProxy, "Admin‑API‑Proxy", "FastAPI", "Proxy, forwardet JWT an OpenRouter")
  Container_Boundary(gw, "OpenRouter Gateway") {
    Container(api, "REST API", "Go/Echo", "JWT‑Middleware, Routing")
    ContainerDb(sqlite, "SQLite DB", "/app/data/db/data.sqlite", "Provider‑Config, User‑Mapping")
  }
  Container(sup, "Supabase", "PostgreSQL + GoTrue", "Auth‑Backend")
  Rel(user, spa, "Bedient UI")
  Rel(spa, apiProxy, "POST Login", "JSON/HTTPS")
  Rel(apiProxy, sup, "Validate Token", "REST")
  Rel(apiProxy, api, "Forward JWT", "JSON/HTTPS")
  Rel(api, sqlite, "Read/Write")
  UpdateRelStyle(apiProxy, api, $offsetX="-40", $offsetY="-20")
```

### C4‑Dynamic (Sequenz)
```mermaid
C4Dynamic
  title OpenRouter Auth Flow – Dynamisches Sequenz-Diagramm
  Person(user, "Kunde / Admin", "Menschlicher Benutzer")
  Container(spa, "Admin‑Portal", "React")
  Container(apiProxy, "Admin‑API‑Proxy", "FastAPI")
  Container(OpenRouter, "OpenRouter API", "Go/Echo")
  Container(sup, "Supabase Auth", "GoTrue + PostgreSQL")

  Rel(user, spa, "1. Login‑Formular ausfüllen")
  Rel(spa, sup, "2. POST /auth/v1/token (grant_type=password)")
  Rel(sup, spa, "3. access_token + refresh_token (JWT)")
  Rel(spa, apiProxy, "4. GET /api/providers (Authorization: Bearer <JWT>)")
  Rel(apiProxy, sup, "5. POST /auth/v1/user (verify token)")
  Rel(sup, apiProxy, "6. user object")
  Rel(apiProxy, OpenRouter, "7. GET /api/providers (Authorization: Bearer <JWT>)")
  Rel(OpenRouter, apiProxy, "8. providers list")

  UpdateRelStyle(spa, sup, $offsetX="-20", $offsetY="-20")
  UpdateRelStyle(apiProxy, sup, $offsetX="-20", $offsetY="-20")
  UpdateRelStyle(apiProxy, OpenRouter, $offsetX="20", $offsetY="-20")
```

### C4‑Component (OpenRouter Auth)
```mermaid
C4Component
  title OpenRouter Auth Middleware Components
  Container_Boundary(OpenRouter, "OpenRouter Gateway") {
    Component(jwtMid, "JWT Middleware", "Go/Echo middleware", "Prüft Bearer Token, validiert Signatur")
    Component(roleCheck, "Role Check", "Go", "Prüft role‑Claim (admin/user)")
    Component(tenantCheck, "Tenant Scope", "Go", "Extrahiert tenant_id‑Claim")
    Component(sqlProvider, "Provider Repository", "Go + SQLite", "Liest Provider‑Config")
    Component(handler, "Provider Handler", "Go", "Liefert Provider‑Liste")
  }
  Rel(jwtMid, roleCheck, "→")
  Rel(roleCheck, tenantCheck, "→")
  Rel(tenantCheck, handler, "→")
  Rel(handler, sqlProvider, "SQL")
```

## Konsequenzen
- **Positiv:** Durchgängiger JWT‑Flux, tenant‑scoped API‑Zugriff, nachvollziehbarer Auth‑Flow.
- **Negativ:** Abhängigkeit von Supabase‑Verfügbarkeit für jeden OpenRouter‑Call; SSO‑Mode nicht getestet.
- **Neutral:** OpenRouter kann eigene JWT‑Signatur implementieren (z. B. RS256) für Offline‑Validierung.

## Nächste Schritte
1. Setze `JWT_SECRET`, `INITIAL_PASSWORD`, `API_KEY_SECRET`, `MACHINE_ID_SALT` in OpenRouter‑Umgebung.
2. Konfiguriere JWT‑Middleware in OpenRouter (`/api/*`).
3. Ergänze Supabase Auth‑Pfad im Admin‑Portal (Login → Token‑Speicherung).
4. Schreibe Integrationstest: Login → Token → Provider‑Abruf.
5. Dokumentiere Postman‑Collection für Auth‑API.
