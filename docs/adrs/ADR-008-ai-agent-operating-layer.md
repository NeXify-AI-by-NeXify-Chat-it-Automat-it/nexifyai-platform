# ADR-008: AI Agent Operating Layer

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), NeXifyAI Agents

## Kontext

NeXifyAI betreibt multiple KI-Agenten (Orchestrator, Sub-Agenten, Cron-Jobs, BrainForge). Ohne standardisierte Governance-Schicht agieren Agenten inkonsistent — keine Memory-Write-Regeln, keine Prompt-Policies, keine Model-Selection-Strategie.

## Problem

KI-Agenten müssen:
- Wissen konsistent im Brain persistieren
- Modellkosten kontrollieren (NeXify vs. Claude vs. GPT)
- Memory-Write-Policies einhalten (Attributed, Corroborated, Governed)
- Sub-Agent-Isolation gewährleisten (kein Cross-Kunden-Zugriff)

## Optionen

1. **Option A: Keine Governance** — Agenten agieren frei
   - Pro: Kein Overhead
   - Contra: Inkonsistenz, Kostenexplosion, Sicherheitsrisiken

2. **Option B: DOS v2.0 AI Agent Operating Layer (GEWÄHLT)**
   - Pro: Standardisierte Policies, BrainGovernor, Model-Auto-Select
   - Contra: Initiale Komplexität

3. **Option C: Externes Agent-Framework (LangChain, CrewAI)**
   - Pro: Ökosystem
   - Contra: Vendor Lock-in, Overhead für unsere Use Cases

## Entscheidung

**Option B** — DOS v2.0 AI Agent Operating Layer mit:
- BrainGovernor für Memory-Access-Control (5 Write-Policies)
- model-auto-select Skill für Kostenoptimierung
- Sub-Agent-Isolation via Context-Trennung (INTERN vs. KUNDE)
- Enforcement-System (4 Schichten) für Customer-Notebook-Zugriff

## Konsequenzen

- **Positiv:** Konsistente Agent-Interaktionen, kontrollierte Kosten, auditierbar
- **Negativ:** Agent-Latenz erhöht sich durch Governance-Checks
- **Neutral:** BrainGovernor wird zu Single-Point-of-Truth für Memory-Access

## Rollback-Plan

BrainGovernor kann deaktiviert werden (Write-Policy ANY). Enforcement-Scripts entfernen. Agenten laufen dann ohne Governance.

## Verweise

- DOS v2.0 Teil XIV: AI Agent Operating Layer
- Skill: brain-first-enforcement
- Skill: nexifyai-identity
