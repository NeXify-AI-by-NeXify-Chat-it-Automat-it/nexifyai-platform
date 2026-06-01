# ADR-019: LangChain/LangGraph Agenten-Optimierung

## Status
2026-05-21 — Implementierung läuft

## Kontext
Die Agenten-Infrastruktur umfasst ~5.000 Zeilen Custom-Code:
- Custom LLM-Provider (687 Zeilen) für OpenRouter, NeXify, EmergentGPT
- Custom Model-Router (292 Zeilen) mit Circuit-Breaker, Fallback-Chain
- Custom Agent Executor (537 Zeilen) mit OODA-Loop
- Custom Agent Mesh (676 Zeilen) mit Peer-to-Peer-Netzwerk
- Custom Oracle Engine (815 Zeilen) mit Status-Lifecycle
- Custom Brain API (243 Zeilen) mit Zero-Vector-Placeholder
- Custom MCP-Runtime (151 Zeilen) mit Event-Bus
- Custom Planner-System (197 Zeilen) mit Subprocess-Orchestrierung

All dies sind etablierte Patterns, die LangChain/LangGraph nativ und production-ready abbildet.

## Entscheidung
Wir ersetzen die gesamte Custom-Agent-Infrastruktur durch LangChain 0.3+ und LangGraph.

### Architektur

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI (server.py)                 │
│  Router-Mounting, CORS, Rate-Limiting, Auth bleiben  │
├─────────────────────────────────────────────────────┤
│              LangGraph StateGraph (Top-Level)         │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌───────────┐  │
│  │ Intake  │ │ Research │ │ Code    │ │ Deploy    │  │
│  │ Agent   │ │ Agent    │ │ Agent   │ │ Pipeline  │  │
│  └────┬────┘ └────┬─────┘ └────┬────┘ └─────┬─────┘  │
│       └───────────┴────────────┴─────────────┘         │
│                    Shared State (TypedDict)             │
├─────────────────────────────────────────────────────┤
│              LangChain Core Layer                      │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ Chat Models  │ │ Tool Registry│ │ Vector Store   │  │
│  │ (Provider-   │ │ (@tool       │ │ (Qdrant +      │  │
│  │  Swapping)   │ │  decorators) │ │  Embeddings)   │  │
│  └─────────────┘ └──────────────┘ └────────────────┘  │
├─────────────────────────────────────────────────────┤
│              LangSmith Observability                   │
│              Tracing + Evaluation + Monitoring         │
└─────────────────────────────────────────────────────┘
```

### Komponenten

| Custom-Komponente | LOC | LangChain-Ersatz | LOC | Sparpotenzial |
|---|---|---|---|---|
| `llm_provider.py` | 687 | `ChatOpenAI` / `ChatAnthropic` + `with_fallbacks()` | ~30 | ~96% |
| `model_router.py` | 292 | `RunnableLambda` + `RunnableBranch` | ~50 | ~83% |
| `nexify_provider.py` | 102 | `ChatOpenAI(api_base=..., model=...)` | ~1 | ~99% |
| `brain_api.py` | 243 | `QdrantVectorStore` + `HuggingFaceEmbeddings` | ~30 | ~88% |
| `supabase_client.py` | 229 | `SQLDatabase` + `PostgresChatMessageHistory` | ~80 | ~65% |
| `base_agent.py` | 118 | `create_react_agent()` | ~0 | 100% |
| `agent_executor.py` | 537 | `AgentExecutor` | ~50 | ~91% |
| `orchestrator.py` | 125 | `StateGraph` + `add_conditional_edges` | ~40 | ~68% |
| `orchestrator_v3.py` | 448 | `StateGraph` + Subgraphs | ~80 | ~82% |
| `oracle_engine.py` | 815 | `StateGraph` + `create_retrieval_chain()` | ~150 | ~82% |
| `mesh/agent_mesh.py` | 676 | LangGraph `Send` API + `add_node()` | ~150 | ~78% |
| `strategic_planner.py` | 40 | `StateGraph` + `WebHealthTool` | ~15 | ~63% |
| `task_graph_planner.py` | 21 | `PlanAndExecute` | ~10 | ~52% |
| `capability_router.py` | 18 | `RunnableBranch` | ~8 | ~56% |
| `autonomous_program_manager.py` | 32 | StateGraph mit Subgraphs | ~15 | ~53% |
| `mcp_daemon.py` | 61 | LangGraph Recursion + Callbacks | ~20 | ~67% |
| `mcp_tool_registry.py` | 51 | `@tool` decorators | ~15 | ~71% |
| `mcp_capability_router.py` | 39 | Conditional Graph Edges | ~0 | 100% |
| **Total** | **~4.534** | | **~744** | **~84%** |

### Provider-Strategie
```
Primary:   LangChain ChatOpenAI → openrouter.ai (NeXify V4)
Fallback:  LangChain ChatOpenAI → emergent-gpt (GPT-4o-mini)
Secondary: LangChain ChatAnthropic → Claude (für komplexe Reasoning-Aufgaben)
```
Alle Provider sind über LangChain's `BaseChatModel`-Interface abstrahiert.

### RAG-Strategie
```
Dokumente → RecursiveCharacterTextSplitter → HuggingFaceEmbeddings → Qdrant
Retriever → ContextualCompressionRetriever → LLM (Stuff/MapReduce)
```
Brain-API wird durch native QdrantVectorStore-Integration ersetzt.

## Konsequenzen
- **+Production-Stabilität**: LangChain 0.3+ ist battle-tested (119K GitHub Stars)
- **-Custom-Code**: ~3.800 Zeilen weniger Wartungsaufwand
- **+Observability**: LangSmith gibt uns Tracing, Evaluation, Monitoring out-of-the-box
- **+Schnellere Entwicklung**: Neue Agent-Patterns in < 20 Zeilen statt 500+
- **+Provider-Flexibilität**: OpenAI ↔ Anthropic ↔ Google in 1 Zeile konfigurierbar
- **+Streaming**: Native Unterstützung für Token-Streaming
- **±Migration**: Alte API-Endpoints müssen kompatibel bleiben während der Umstellung

## Migrations-Plan
1. **Phase 1**: ADR + Dependency-Update + LangChain Config Layer
2. **Phase 2**: Tool Registry + RAG Pipeline (Brain-API ersetzt)
3. **Phase 3**: Agent-Migration (Executor → Orchestrator → Mesh → Oracle)
4. **Phase 4**: Planner-Migration (strategic_planner → capability_router → program_manager)
5. **Phase 5**: Governance/Deployment (LangSmith + Kubernetes + Streaming)

## Alternativen
- **LlamaIndex**: Besser für reine RAG-Szenarien, schwächer bei Multi-Agent-Orchestrierung
- **LangGraph pur**: Mehr Kontrolle, aber mehr Code — für die meisten unserer Agenten nicht nötig
- **Custom bleiben**: Hohe Wartungslast, keine Community-Innovationen — keine Option
