# ADR-003: OpenRouter als primärer LLM-Provider

**Status:** accepted
**Datum:** 2026-05-08
**Autor:** NeXifyAI (Lead Agent)
**Stakeholder:** Pascal Courbois (CEO)

## Kontext

NeXifyAI benötigt einen zuverlässigen, kosteneffizienten LLM-Provider für:
- Lead Agent (NeXifyAI/Hermes) — Architektur, Code, Reasoning
- 9 Fach-Agenten — Spezialisierte Aufgaben
- Subagenten — Einmal-Tasks
- Cron-Agenten — Wiederkehrende Prüfungen
- E-Mail-Autoreplies — Schnelle Textgenerierung

Die Anforderungen sind: Multi-Model-Routing, Fallback-Fähigkeit, OpenRouter-kompatibles API-Format, Kostenkontrolle.

## Problem

Ohne standardisierten Provider:
- Kein zentrales Kosten-Tracking (Token-Verbrauch pro Agent)
- Kein automatisches Fallback bei Provider-Ausfall
- Verschiedene API-Formate (OpenAI vs Anthropic vs OpenRouter)
- Risiko von Vendor-Lock-in bei Direktintegration

## Optionen

### Option A: OpenRouter als Primärprovider (GEWÄHLT)
- **Pro:** Multi-Model-Zugang (DeepSeek, Anthropic, OpenAI), einheitliches API-Format, Usage-Tracking, Fallback-Routing, $0.14-$1.40/M Tokens
- **Contra:** Abhängigkeit von Drittanbieter; OpenAI-only-Modelle nicht verfügbar

### Option B: DeepSeek Direct
- **Pro:** Direkte API, keine Mittelschicht
- **Contra:** Kein Fallback, nur DeepSeek-Modelle, kein Multi-Provider

### Option C: Vercel AI Gateway
- **Pro:** Edge-nah, einfache Integration
- **Contra:** Höhere Kosten, weniger Modell-Auswahl, Vendor-Lock-in zu Vercel

## Entscheidung

**Option A: OpenRouter als Primärprovider** mit DeepSeek Direct als Fallback und Vercel AI Gateway als zweite Route (optional).

Begründung:
1. Einheitliches API-Format reduziert Integrationsaufwand
2. Multi-Model → optimales Preis/Leistungs-Verhältnis (deepseek-v4-pro für Reasoning, -flash für einfache Tasks)
3. Usage-Tracking → FinOps-Kapitel 25 umsetzbar
4. Kein Lock-in: Provider-Wechsel durch API-Standardisierung möglich

## Konsequenzen

- **Positiv:** Kosteneffizienz (10:1 Preisunterschied nutzbar), automatisches Fallback, Modell-Vielfalt
- **Negativ:** $500/Monats-Budget muss aktiv gemonitort werden; OpenRouter 402-Fehler bei Guthaben-Erschöpfung
- **Neutral:** OpenRouter-Diagnose-Skill etabliert (`openrouter-402-diagnosis`)

## Rollback-Plan

- DeepSeek Direct API-Credentials liegen bereit für sofortigen Switch
- Vercel AI Gateway als dritte Route konfigurierbar
- Modell-Pinning in `/packages/config/prompts/` zentralisiert → ein Update genügt

## Verweise

- OpenRouter Diagnose: Skill `openrouter-402-diagnosis`
- Modell-Selection: DOS v2.0 Kapitel 21.6
- FinOps: DOS v2.0 Kapitel 25
- Vercel AI Gateway: Skill `vercel-ai-gateway`
