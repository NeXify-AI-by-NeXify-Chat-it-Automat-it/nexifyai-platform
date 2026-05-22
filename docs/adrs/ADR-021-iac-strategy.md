# ADR-021: IaC-Strategie — Infrastructure as Code mit OpenTofu

**Status:** proposed
**Datum:** 2026-05-21
**Autor:** DevOps-Agent / AI-CEO (AIC-64)
**Stakeholder:** DevOps, CTO, Security

## Kontext
Die aktuelle Infrastruktur wird manuell oder via Docker-Compose verwaltet. Es gibt kein echtes Infrastructure-as-Code. Die DevOps-Analyse (Iteration 3) hat gezeigt:
- Kein Terraform/OpenTofu/Pulumi
- Nur Docker-Compose (sicher-repo) und manuelle Konfiguration (agentur-repo)
- Kein State-Management
- Keine reproduzierbaren Umgebungen

## Problem
Ohne IaC sind Umgebungen nicht reproduzierbar, Deployments fehleranfällig und Disaster Recovery kaum möglich (ISO 27001 A.12.3).

## Optionen
1. **Option A: OpenTofu** (Gewählt)
   - Pro: Open Source, Terraform-kompatibel, keine Vendor-Lock-in
   - Contra: Weniger Features als Terraform Cloud

2. **Option B: Terraform Cloud**
   - Pro: Enterprise-Features, Sentinel Policies
   - Contra: Kostenpflichtig, Vendor-Lock-in

3. **Option C: Pulumi**
   - Pro: Echter Code (Python/TypeScript)
   - Contra: Komplexität, kleinere Community

## Entscheidung
Option A: **OpenTofu** mit Supabase State Backend
- Open-Source-IaC
- State in Supabase (PostgreSQL-kompatibel)
- Erste Module: Supabase, Vercel, Monitoring (Grafana/Prometheus)

## Konsequenzen
### Positiv
- ✅ Reproduzierbare Infrastruktur
- ✅ Disaster Recovery möglich
- ✅ ISO 27001 A.12.3 (Backup) erfüllt
- ✅ DSGVO Art. 32 (Sicherheit) gestärkt

### Negativ
- ⏱️ Initialer Setup-Aufwand
- 📚 Team muss OpenTofu lernen

## Rollback-Plan
1. Aktuelle Docker-Compose-Konfiguration als Fallback behalten
2. Keine produktiven Ressourcen ohne manuelles Review

## Verweise
- [DevOps-Audit](docs/tasks/devops-infrastructure-audit.md)
- ISO 27001:2022 A.12.3 – Backup
- OpenTofu: https://opentofu.org
