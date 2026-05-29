# ISMS-Scope (ISO 27001:2022)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI Security Officer / Pascal Courbois
**Geltungsbereich:** Informationssicherheits-Managementsystem gemäß ISO/IEC 27001:2022

---

## 1. Scope-Definition

### 1.1 Organisation
| Feld | Wert |
|------|------|
| Unternehmen | NeXifyAI — neXify (Chat it. Automate it.) |
| Standort | Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande |
| Scope-ID | ISMS-SCOPE-001 |
| Version | 1.0 |
| Datum | 2026-05-30 |

### 1.2 Scope-Erklärung
Das ISMS umfasst die Planung, Entwicklung, den Betrieb und die Wartung der **NeXifyAI Enterprise Brain v3 Plattform** — einer KI-gestützten Kundenkommunikations- und Automationsplattform. Die Plattform wird als SaaS (Software as a Service) betrieben und befindet sich in der Early-Access-Phase.

### 1.3 Im Scope enthalten

| Bereich | Enthalten | Begründung |
|---------|-----------|------------|
| **FastAPI Backend** (services/api/) | ✅ | Kern der Plattform — API, Agenten, Business-Logik |
| **React Frontend** (apps/web/) | ✅ | Admin-Cockpit, Kundenportal, Chat-UI |
| **Qdrant Vector DB** | ✅ | Wissensspeicher (112k+ Points, 27 Collections) |
| **MongoDB** | ✅ | Business-Daten (Leads, Conversations, Quotes) |
| **Supabase** | ✅ | Auth, PostgreSQL, Storage |
| **Kong API Gateway** | ✅ | Externes Routing, Rate-Limiting |
| **Redis Cache** | ✅ | Session-Caching |
| **Monitoring** (Prometheus/Grafana/Loki) | ✅ | System-Überwachung, Alerting |
| **GitHub Repository** | ✅ | Source Code, CI/CD, Issues |
| **Vercel Deployment** | ✅ | Frontend-Hosting, Preview-Deployments |
| **Cloudflare** | ✅ | DNS, CDN, DDoS-Schutz, Tunnel |
| **OpenRouter API** | ✅ | LLM/Embedding-Provider (Subprozessor) |
| **E-Mail (Resend)** | ✅ | Transaktions-E-Mails |
| **Entwicklungsumgebung** | ❌ | Lokale Dev-Umgebungen außerhalb des Scopes |
| **Kundenprojekt-Repos** | ❌ | Separate Repos mit eigenem CI/CD |

---

## 2. System-Grenzen

### 2.1 Physische Grenzen
| Komponente | Standort | Betreiber |
|-----------|----------|-----------|
| VPS (Hetzner) | Deutschland/Niederlande | Hetzner Online GmbH |
| Supabase Cloud | EU (Frankfurt) / US-East | Supabase Inc. |
| Vercel Edge | Global CDN | Vercel Inc. |
| Cloudflare Edge | Global CDN | Cloudflare Inc. |

### 2.2 Logische Grenzen
```
[Extern] Internet
    │
    ├── Cloudflare (DNS, CDN, DDoS)
    │   └── Traefik (TLS-Terminierung, Ports 80/443)
    │       ├── Kong Gateway (Port 8000 — API-Routing)
    │       ├── Frontend (React, Vercel-gehostet)
    │       └── Admin-Cockpit (Port 3000, Grafana)
    │
    └── Docker-Netzwerk (intern, nicht von außen erreichbar)
        ├── Brain API (8420) + Qdrant (6333)
        ├── MongoDB (27017) + Redis (6379)
        ├── Oracle Engine (8001)
        ├── Prometheus (9090) + Grafana (3000)
        └── Ollama (11434) + nscale
```

### 2.3 Externe Schnittstellen
| Schnittstelle | Typ | Sicherheitsmaßnahme |
|--------------|-----|---------------------|
| HTTPS (REST API) | Extern | TLS 1.3, JWT, Rate-Limiting |
| WebSocket (Chat) | Extern | JWT-Auth, Rate-Limiting |
| OpenRouter API | Extern (Subprozessor) | API-Key, DPA, keine dauerhafte Speicherung |
| Resend API | Extern (Subprozessor) | API-Key, DPA |
| GitHub Webhooks | Extern | Signatur-Prüfung, IP-Whitelist |
| Supabase API | Extern (Subprozessor) | Service-Role-Key, DPA |

---

## 3. Interessengruppen (Stakeholder)

| Gruppe | Anforderungen | Erwartungen |
|--------|--------------|-------------|
| **Kunden** (Early Access) | Verfügbarkeit, Datenschutz, Sicherheit | 95% Health Score, DSGVO-Konformität |
| **Pascal Courbois** (CEO) | Betriebssicherheit, Compliance, Skalierbarkeit | ISMS-Einführung, Audit-Fähigkeit |
| **Aufsichtsbehörden** | DSGVO-Konformität, Nachweispflicht | VVT, DSFA, Löschkonzept, TOM |
| **Subprozessoren** | AVV-Einhaltung, Datenschutz | DPA, Weisungsgebundenheit |
| **Mitarbeiter** (AI-Agenten) | Klare Rollen, Berechtigungen | 14 Agent-Verträge, RBAC |

---

## 4. Kritische Assets

| Asset | Typ | Vertraulichkeit | Integrität | Verfügbarkeit |
|-------|-----|----------------|------------|---------------|
| Kundendaten (MongoDB) | Daten | **Hoch** | **Hoch** | **Hoch** |
| API-Keys & Secrets | Konfiguration | **Hoch** | **Hoch** | Mittel |
| Brain-Wissen (Qdrant) | Daten | Mittel | **Hoch** | **Hoch** |
| Source Code (GitHub) | Code | Mittel | **Hoch** | Mittel |
| CI/CD Pipeline | Prozess | Mittel | **Hoch** | Mittel |
| Authentifizierungsdaten | Daten | **Hoch** | **Hoch** | **Hoch** |
| LLM-Zugriff (OpenRouter) | Dienst | Mittel | Mittel | **Hoch** |
| Audit-Logs | Daten | **Hoch** | **Hoch** | Mittel |

---

## 5. Kontext der Organisation

### 5.1 Interne Themen
- **Startup-Phase:** Schnelle Iteration vs. formelle Prozesse
- **Ein-Personen-Betrieb:** Pascal = CEO, DevOps, Support
- **AI-gesteuert:** 14 AI-Agenten ersetzen menschliche Mitarbeiter
- **Selbst-Hosting:** Volle Kontrolle über Infrastruktur

### 5.2 Externe Themen
- **DSGVO:** Niederländisches Unternehmen mit deutschen Kunden
- **EU AI Act:** KI-Regulierung ab 2026
- **NIS-2:** IT-Sicherheitsanforderungen für kritische Infrastruktur (nicht relevant für aktuelle Größe)
- **Marktposition:** Early Access — Fokus auf Funktionsumfang vor Formalisierung

---

## 6. Scope-Exklusionen (Begründet)

| Ausgeschlossen | Begründung |
|---------------|------------|
| **Physische Sicherheit** (RZ-Zutritt) | Hetzner als Rechenzentrumsbetreiber — ISO 27001-zertifiziert |
| **Personal-Sicherheit** (Mitarbeiter-Screening) | Ein-Personen-Unternehmen (Pascal) |
| **Entwicklungsumgebungen** | Lokale Dev-Umgebungen, kein Kundenkontakt |
| **Kundenprojekt-Repos** | Separate Repos, eigener CI/CD — Kundenprojekt-Golden-Path |
| **Business Continuity Management** | Für aktuelle Größe und Early-Access-Phase nicht verhältnismäßig |

---

## 7. Verweise

- [ISMS-Rahmendokument](../policies/isms-framework.md)
- [Security Policy](../policies/security-policy.md)
- [Vulnerability Policy](../policies/vulnerability-policy.md)
- [Incident Response Plan](../policies/incident-response-plan.md)
- [TOM (Art. 32)](../legal/tom.md)
- [Operational Constitution](../../operational-constitution.md)
- [Runtime Topology](../../runtime-topology.md)