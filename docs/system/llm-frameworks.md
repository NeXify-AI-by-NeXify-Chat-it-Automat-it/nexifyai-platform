# NeXifyAI — LLM Frameworks Evaluation

## Aktueller Stack
- **Primary:** Hermes Agent (Container, CLI-first)
- **LLM Provider:** OpenRouter (deepseek-v4-pro / deepseek-v4-flash)
- **Fallback:** DeepSeek Direct API

## Evaluierte Frameworks

### LangChain
- **Status:** ⏸️ Nicht aktiv genutzt
- **Grund:** Hermes Agent deckt Orchestrierung ab. LangChain würde zusätzliche Abstraktionsebene einführen.
- **Möglicher Use Case:** Subagenten für spezifische RAG/Dokumentenanalyse-Workflows
- **Entscheidung:** Bei Bedarf in Phase 3+ evaluieren

### CrewAI / AutoGen
- **Status:** ❌ Nicht evaluiert
- **Grund:** Multi-Agent-Orchestrierung ist durch Hermes + 9 Fach-Agenten abgedeckt

### Semantic Kernel (Microsoft)
- **Status:** ❌ Nicht relevant
- **Grund:** C#/.NET-Fokus, passt nicht in Python/JS-Stack

### OpenRouter (Current)
- **Status:** ✅ Aktiv
- **Anbieter:** deepseek-v4-pro (primär), deepseek-v4-flash (Subagenten/Cron)
- **Kosten:** $1.40/M input (pro), $0.14/M input (flash)
- **Fallback:** DeepSeek Direct API bei OpenRouter-Ausfall

### Supabase Edge Functions + LLM
- **Status:** 🔜 Vorgemerkt
- **Use Case:** Leichtgewichtige LLM-Calls in Edge Functions (z.B. Lead-Scoring)
- **Aktivierung:** Phase 2 (CRM Core)

## Entscheidungslogik
- Hermes Agent = Orchestrator (bleibt)
- OpenRouter = LLM Gateway (bleibt)
- Kein weiteres Framework ohne validierten Use Case
