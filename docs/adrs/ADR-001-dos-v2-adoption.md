# ADR-001: Einführung DOS v2.0 als verbindliches Betriebssystem

**Status:** accepted
**Datum:** 2026-05-08
**Autor:** NeXifyAI (Lead Agent)
**Stakeholder:** Pascal Courbois (CEO), Technical Lead

## Kontext

NeXifyAI operierte bisher ohne formalisiertes Betriebssystem. Das DOS v1.1 existierte als externes Dokument, war aber zu 0% im Repository operationalisiert. Es gab keine `/docs`, `/packages`, `/ops`, oder `/automations` Verzeichnisse. Die 15 strategischen Lücken (Rollen, ADR, API-Standards, Incident-Management, FinOps, Testing, etc.) waren nicht adressiert.

## Problem

Ohne verbindliches Betriebssystem:
- Keine einheitlichen Standards für Code, Design, Content
- Keine definierten Quality Gates
- Ad-hoc-Entscheidungen ohne Dokumentation
- Keine KI-Governance (Prompt-Policies, Model-Selection, Memory-Write-Regeln)
- Keine Test-Architektur
- Kein Incident-Management oder FinOps

## Optionen

### Option A: DOS v1.1 übernehmen und nur dokumentieren
- **Pro:** Minimaler Aufwand
- **Contra:** 15 strategische Lücken bleiben offen, keine KI-Governance

### Option B: DOS v2.0 — vollintegriertes Betriebssystem (GEWÄHLT)
- **Pro:** Alle Lücken geschlossen, KI-Kapitel integriert, operationalisiert
- **Contra:** Initialer Erstellungsaufwand (~31KB Dokument + 15+ Artefakte)

### Option C: Externes Framework (TOGAF, ITIL) adaptieren
- **Pro:** Industriestandard
- **Contra:** Überdimensioniert für NeXifyAI-Größe, hohe Komplexität

## Entscheidung

**Option B: DOS v2.0** — das vollintegrierte Betriebssystem.

Begründung:
1. DOS v1.1 liefert bewährte Grundlage (20 Kapitel)
2. +13 neue Kapitel schließen alle 15 Lücken
3. KI-Agent-Governance ist Business-kritisch (Kapitel 21)
4. Passt zur Unternehmensgröße und Agilität

## Konsequenzen

- **Positiv:** Einheitliche Standards, messbare Qualität, automatisierte Compliance-Prüfung
- **Negativ:** Erfordert Disziplin bei Einhaltung aller Quality Gates
- **Neutral:** Jedes Projekt muss zu Beginn klassifiziert werden (Typ A-F)

## Rollback-Plan

DOS v2.0 kann auf v1.1 zurückgestuft werden, falls sich das Framework als zu komplex erweist. Praktisch unwahrscheinlich, da v2.0 eine Obermenge von v1.1 ist.

## Verweise

- DOS v2.0: `/docs/DOS-v2.0.md`
- RACI-Matrix: `/docs/governance/raci.yaml`
- ADR-Template: `/docs/adrs/ADR_TEMPLATE.md`
