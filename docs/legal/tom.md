# Technische und Organisatorische Massnahmen (TOM)
# gemaess Art. 32 DSGVO

**Stand:** 2026-05-30
**Verantwortlicher:** Pascal Courbois, NeXifyAI (KvK 90483944)
**System:** NeXifyAI Enterprise Brain v3

---

## 1. Zutrittskontrolle (physischer Zugang)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **Rechenzentrum** | Hetzner (Deutschland/Niederlande) — Zutritt nur mit RFID + PIN, Video, 24/7-Security | ✅ |
| **VPS-Zugang** | SSH-Key-Auth (keine Passwoerter), Cloudflared Tunnel fuer Admin-UI | ✅ |
| **Kein Vor-Ort-Zugriff** | Vollstaendig remote betrieben | ✅ |

## 2. Zugangskontrolle (IT-Systeme)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **SSH** | Public-Key-Auth, Port 22 via Tailscale/Cloudflared | ✅ |
| **Docker-Isolation** | Jeder Service in eigenem Container, minimale Netzwerk-Privilegien | ✅ |
| **Firewall** | Nur Ports 80/443 (Traefik), 8000 (Kong) nach aussen | ✅ |
| **OS** | Ubuntu 22.04 LTS, unattended-upgrades | ✅ |
| **Root-Zugriff** | Nur Pascal Courbois (CEO) | ✅ |

## 3. Zugriffskontrolle (Daten und Funktionen)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **JWT-Auth** | Admin + Customer + System-Rollen mit separaten Tokens | ✅ |
| **Supabase RLS** | Row-Level-Security auf 40+ Tabellen | ✅ |
| **RBAC** | Role-Based Access Control (Admin/Kunde/System) | ✅ |
| **Magic Link** | Passwortloser Login fuer Kunden | ✅ |
| **API-Key-Auth** | Service-Rollen und Integrationen via API-Keys | ✅ |
| **Least Privilege** | Minimal notwendige Rechte fuer jeden Service | ✅ |
| **Agent-Restriktionen** | 14 AI-Agenten mit definierten Vertraegen (kein Vollzugriff) | ✅ |

## 4. Weitergabekontrolle (Datentransfer)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **TLS 1.3** | Alle externen Verbindungen via HTTPS (Traefik) | ✅ |
| **DPA mit Subprozessoren** | AVV mit OpenRouter, Supabase, Vercel, Resend, Cloudflare, GitHub | ✅ |
| **Keine Rohdaten bei LLM-Providern** | OpenRouter speichert Input/Output nicht dauerhaft | ✅ |
| **Subprozessoren-Pruefung** | Quartalsweise DPA-Einhaltungspruefung | ✅ |

## 5. Eingabekontrolle (Dateneingabe)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **Pydantic-Validierung** | Alle API-Endpoints validieren via Pydantic-Modelle | ✅ |
| **Input-Sanitization** | XSS-Schutz, SQL-Injection via Parameterized Queries | ✅ |
| **Rate Limiting** | SlowAPI: 200/min (Admin), 20/300s (Auth) | ✅ |
| **Prompt-Injection-Schutz** | System-Prompt-Escaping, Zwangsbefehl-Header | ✅ |
| **CORS-Whitelist** | Nur explizit erlaubte Domains | ✅ |
| **API-Gateway** | Kong Gateway routet und limitt externen Traffic | ✅ |

## 6. Auftragskontrolle (Auftragsverarbeitung)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **AVV/DPA** | Schriftliche AVV mit allen Subprozessoren | ✅ |
| **Subprozessoren-Verzeichnis** | 9 Subprozessoren dokumentiert | ✅ |
| **Weisungsgebundenheit** | Vertraglich vereinbart | ✅ |
| **Pruefrecht** | Jederzeit, quartalsweise Pruefung | ✅ |
| **Kuendigungsrecht** | 30 Tage bei Vertragsverletzung | ✅ |

## 7. Verfuegbarkeitskontrolle

| Massnahme | Beschreibung | RPO/RTO | Status |
|-----------|-------------|---------|--------|
| **PostgreSQL-Backup (WAL)** | Point-in-Time Recovery | 1 Std / 15 Min | ✅ |
| **MongoDB-Backup** | Taegliche Dumps | 1 Std / 30 Min | ✅ |
| **Qdrant-Snapshots** | Taegliche Collection-Snapshots | 24 Std / 1 Std | ✅ |
| **Uptime Kuma** | Externes Monitoring (60s) | — | ✅ |
| **Health-Score** | Internes Metrik-System (30 Min) | — | ✅ |
| **Alertmanager** | Prometheus-Alerting | — | ✅ |

## 8. Datentrennung (Mandantenfaehigkeit)

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **Supabase RLS** | tenant_id-basierte Isolation auf 40+ Tabellen | ✅ |
| **MongoDB-Isolation** | Filterung nach customer_email | ✅ |
| **Kundenprojekt-Trennung** | Eigenes Repo/Secrets/DB/CI (Golden Path) | ✅ |
| **Audit-Log** | Alle Aktionen mit Customer-ID | ✅ |

## 9. Wiederherstellbarkeit

| Massnahme | Beschreibung | Status |
|-----------|-------------|--------|
| **Backup-Restore-Test** | Monatliche Integritaetspruefung | ✅ |
| **Incident Response Plan** | Definierter Prozess (SEV1-SEV4) | ✅ |
| **Postmortem** | Lessons Learned + Prevention Rules | ✅ |

## 10. Verweise

- [VVT (Verarbeitungsverzeichnis)](./vvt.md)
- [DSFA (Datenschutz-Folgenabschaetzung)](./dsfa.md)
- [Loeschkonzept](./loeschkonzept.md)
- [DPA/AVV](./dpa-nexifyai.md)
- [AVV-Verzeichnis](./avv-verzeichnis.md)
- [Security Policy](../policies/security-policy.md)
- [Incident Response Plan](../policies/incident-response-plan.md)
- [Betroffenenrechte](./betroffenenrechte.md)