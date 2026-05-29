# MIGRATION GUIDE: Custom Agents → LangChain/LangGraph

**Datum:** 2026-05-21  
**Version:** 1.0  
**Status:** Active

## Übersicht

Dieser Guide beschreibt die Migration von der Custom-Agent-Infrastruktur (~4.500 Zeilen)
auf LangChain/LangGraph (~2.640 Zeilen).

### Ziel-Architektur

```
FastAPI (server.py)
  └─ LangGraph StateGraph (Supervisor)
       ├─ Code Agent    (create_react_agent + Shell/Search-Tools)
       ├─ Research Agent (create_react_agent + Brain/RAG-Tools)
       └─ QA Agent      (create_react_agent + Code-Analyse-Tools)
  └─ Oracle Workflow (StateGraph mit 8 Status)
  └─ Planner Workflow (StateGraph mit 6 Nodes)
  └─ RAG Pipeline (Qdrant + HuggingFace Embeddings)
```

## Quick Start

### Installation

```bash
pip install -r services/api/requirements.txt
```

### Initialisierung

```python
# In server.py lifespan() — automatisch via init_ai_infrastructure()
from services.governance import init_ai_infrastructure
governance = init_ai_infrastructure(
    enable_langsmith=True,
    enable_cache=True,
    project_name="nexifyai-production",
)
```

### Erste Schritte

```python
# 1. LLM nutzen
from services.langchain_config import get_llm_for_task, create_llm_with_fallbacks

llm = get_llm_for_task("research")  # Claude Sonnet (komplexes Reasoning)
llm = get_llm_for_task("chat")      # DeepSeek V4 (schnell, günstig)

response = llm.invoke("Erkläre Python Decorators")
print(response.content)

# 2. Agent nutzen
from services.agent_system import run_agent

result = run_agent("Implementiere eine Login-Funktion")
print(result["messages"][-1].content)

# 3. RAG Query
from services.rag_pipeline import create_qa_chain

qa = create_qa_chain(k=5)
result = qa.invoke({"query": "Was sagt ADR-019 zur Provider-Strategie?"})
print(result["result"])
```

## Migration-Tabelle

| Alte Datei | Neue Datei | API-Änderung |
|---|---|---|
| `services/llm_provider.py` (687 Z.) | `services/langchain_config.py` | `get_llm_for_task(task_type)` statt `create_llm_provider()` |
| `services/model_router.py` (292 Z.) | `services/langchain_config.py` | `CAPABILITY_ROUTING` Dict + `get_llm_for_task()` |
| `services/deepseek_provider.py` (102 Z.) | `services/langchain_config.py` | `ChatOpenAI(model="deepseek/deepseek-v4-flash", ...)` |
| `brain_api.py` (243 Z.) | `services/rag_pipeline.py` | `create_qa_chain()` statt `brain_api.ask()` |
| `services/llm_provider.py` → `_call_llm()` | `langchain_config.py` → `create_llm_with_fallbacks()` | Automatischer Fallback (Primary → EmergentGPT) |
| `agents/orchestrator.py` (125 Z.) | `services/agent_system.py` → `build_supervisor_graph()` | LangGraph StateGraph statt Custom Router |
| `agents/*.py` (Custom Agents) | `services/agent_system.py` → `create_agent_node()` | Factory-Funktion mit System-Prompt + Tools |
| `services/oracle_engine.py` (815 Z.) | `services/oracle_workflow.py` | `run_oracle_task()` statt `OracleEngine.process_cycle()` |
| `runtime/planner/*.py` (197 Z.) | `services/planner_workflow.py` | `run_planning_cycle()` statt 7 subprocess-Aufrufe |
| `runtime/mcp/mcp_tool_registry.py` (51 Z.) | `services/tool_registry.py` | `@tool` Decorator statt Custom Tool-Klasse |
| `runtime/governance/*` (758 Z.) | `services/governance.py` | `GovernanceCallback` + LangSmith Tracing |

## API-Endpoint Migration

| Alter Endpoint | Neuer Endpoint | Methode |
|---|---|---|
| Custom Agent Dispatch | `POST /api/v2/agent/run` | Single-Task |
| — | `POST /api/v2/agent/stream` | Streaming (SSE) |
| `POST /oracle/process` | `POST /api/v2/oracle/run` | Oracle Lifecycle |
| `GET /oracle/status` | `GET /api/v2/oracle/{task_id}` | Task-Status |
| `POST /planner/cycle` | `POST /api/v2/planner/cycle` | Planning Cycle |
| `GET /brain/query` | `POST /api/v2/rag/query` | RAG Query |
| — | `POST /api/v2/rag/conversation` | Conversational RAG |
| — | `GET /api/v2/health/ai` | AI Health |
| — | `GET /api/v2/tools` | Tool Registry |

## Neue Features (vorher nicht verfügbar)

### 1. Streaming

```python
for chunk in llm.stream("Erzähle mir eine Geschichte"):
    print(chunk.content, end="", flush=True)
```

### 2. Structured Output

```python
from services.structured_output import AgentResult
from langchain_core.pydantic_v1 import BaseModel, Field

# Definiere Output-Schema
class WeatherReport(BaseModel):
    city: str = Field(description="City name")
    temperature: float = Field(description="Temperature")

# Nutze with_structured_output
structured_llm = llm.with_structured_output(WeatherReport)
result = structured_llm.invoke("Weather in Paris?")
print(result.city, result.temperature)
```

### 3. Provider-Swapping in 1 Zeile

```python
# OpenAI
llm = ChatOpenAI(model="gpt-4o")
# Anthropic
llm = ChatOpenAI(model="deepseek/deepseek-v4-flash", openai_api_base="https://openrouter.ai/api/v1")  # OpenRouter only
# Google
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
```

### 4. LangSmith Tracing

```python
# Automatisch aktiviert via init_ai_infrastructure()
# Alle Chains/Agents sind getraced unter:
# https://smith.langchain.com
```

### 5. RAG mit Multi-Query + Contextual Compression

```python
retriever = get_retriever(
    k=5,
    use_multi_query=True,      # 3 verwandte Fragen für bessere Recall
    use_compression=True,       # Nur relevante Passagen ans LLM
)
```

## Provider-Konfiguration

Die Provider werden über Umgebungsvariablen konfiguriert:

```bash
# Primary LLM (OpenRouter/DeepSeek)
OPENROUTER_API_KEY=sk-or-v1-...

# Fallback LLM (EmergentGPT/GPT-4o-mini)
# EMERGENT_LLM_KEY — REMOVED 2026-05-29 (OpenRouter only)
# EMERGENT_LLM_KEY=...
# EMERGENT_LLM_BASE=https://emergent-gpt.com/api/v1

# Reasoning LLM (Anthropic/Claude)
# ANTHROPIC_API_KEY — REMOVED 2026-05-29
OPENROUTER_API_KEY=sk-or-...

# LangSmith Observability (optional)
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=nexifyai-production

# Qdrant Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Testing

```python
# Teste LLM-Verfügbarkeit
from services.langchain_config import get_primary_llm
llm = get_primary_llm()
response = llm.invoke("Antworte mit 'ok'")
assert response.content.strip() == "ok"

# Teste RAG
from services.rag_pipeline import create_qa_chain
qa = create_qa_chain(k=2)
result = qa.invoke({"query": "Test query"})
assert result.get("result")

# Teste Agent
from services.agent_system import run_agent
result = run_agent("Sag 'Hallo Welt'")
assert result.get("messages")
```

## Rollback-Plan

Falls Probleme auftreten:

1. **Phase 1:** Deaktiviere LangChain-Endpoints (entferne `app.include_router(langgraph_router)`)
2. **Phase 2:** Nutze alte API-Endpoints weiter (Custom-Code bleibt bis 2026-06-21 aktiv)
3. **Phase 3:** Melde Issue mit Logs aus LangSmith-Trace

## Zeitplan

| Phase | Datum | Aktion |
|---|---|---|
| 1. Core Layer | 2026-05-21 | ✅ langchain_config.py + tool_registry.py |
| 2. RAG Pipeline | 2026-05-21 | ✅ rag_pipeline.py (ersetzt brain_api.py) |
| 3. Agent Migration | 2026-05-21 | ✅ agent_system.py + oracle_workflow.py |
| 4. Planner Migration | 2026-05-21 | ✅ planner_workflow.py |
| 5. API + Routing | 2026-05-21 | ✅ langgraph_routes.py |
| 6. Deprecation | 2026-05-21 | ⬜ Legacy-Code markiert |
| 7. Cleanup | 2026-06-21 | ⬜ Legacy-Code entfernen |

## Support

Bei Fragen: Issue erstellen mit Label `langchain-migration`
Oder LangSmith-Trace-Link beifügen für Debugging.
