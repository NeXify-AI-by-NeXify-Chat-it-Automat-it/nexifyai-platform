# Bauplan → Siehe System-Katalog + ADRs

> ⚠️ **Dieses Dokument wurde durch den detaillierten System-Katalog abgelöst.**
>
> Der vollständige Bauplan der NeXifyAI-Plattform ist in folgenden Dokumenten beschrieben:

## Aktuelle Bauplan-Quellen

### System-Katalog
| # | System | Beschreibung |
|---|--------|-------------|
| 001 | [Operations](docs/systems/sys-001-operations.md) | Betriebsprozesse |
| 002 | [Agency CRM](docs/systems/sys-002-agency-crm.md) | Kundenbeziehungsmanagement |
| 003 | [Web Architecture](docs/systems/sys-003-web-architecture.md) | Web-Frontend & API |
| 004 | [AI Runtime](docs/systems/sys-004-ai-runtime.md) | KI-Agenten & Orchestrierung |
| 005 | [MCP Infrastructure](docs/systems/sys-005-mcp-infrastructure.md) | Tool-Integration |
| 006 | [Infrastructure](docs/systems/sys-006-infrastructure.md) | Hosting & Netzwerk |
| 007 | [Production Pipeline](docs/systems/sys-007-production-pipeline.md) | CI/CD & Delivery |
| 008 | [Quality Management](docs/systems/sys-008-quality-management.md) | Qualitätssicherung |
| 009 | [Security](docs/systems/sys-009-security.md) | Sicherheit |
| 010 | [Growth](docs/systems/sys-010-growth.md) | Wachstum |
| 011 | [Documentation](docs/systems/sys-011-documentation.md) | Dokumentation |
| 012 | [Monitoring](docs/systems/sys-012-monitoring.md) | Überwachung |

### Runtime-Topologie
Siehe [`runtime-topology.md`](../../runtime-topology.md) für:
- Netzwerk-Topologie (Gateways, Docker-Netze, Cloudflare Tunnel)
- Service-Abhängigkeiten (34+ Dienste)
- Port-Mapping und Verbindungen

*Archiviert: 2026-05-29 | Siehe ADR-031*