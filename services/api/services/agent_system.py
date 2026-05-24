"""
LangGraph Agent System — Enterprise Multi-Agent Orchestration
=============================================================
Ersetzt: agent_executor.py (537 Z.), orchestrator_v3.py (448 Z.), mesh/agent_mesh.py (676 Z.)

Architektur:
  ┌──────────────────────────────────────────────────┐
  │              Supervisor Graph (Top-Level)          │
  │  Input → Classifier → [Research|Code|QA|Deploy]   │
  │                    ↓                              │
  │              Synthesizer → Output                 │
  └──────────────────────────────────────────────────┘

Jeder Sub-Agent ist ein eigener StateGraph mit:
  - ReAct-Pattern (Reason + Act + Observe)
  - Tool-Zugriff (rollenbasiert via tool_registry.get_agent_tools())
  - Shared State (TypedDict)
  - Fehlerbehandlung (Retry + Fallback)
"""
import os
import json
import logging
from typing import Annotated, Sequence, TypedDict, Literal, Optional, Union

# LangGraph Core
from langgraph.graph import StateGraph, Graph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# LangChain
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool

# Intern
from langchain_config import get_llm_for_task, create_llm_with_fallbacks
from tool_registry import get_agent_tools, get_all_tools

logger = logging.getLogger("nexifyai.agents")

# ─── Shared State ─────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Zentraler Zustand, der durch alle Agenten geteilt wird.
    
    Ersetzt das Custom `AgentResult`-Dataclass + manuelle State-Übergabe.
    LangGraph's `add_messages` reduziert automatisch Nachrichten-Listen.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    task: str                          # Ursprüngliche Aufgabe
    task_type: str                     # Klassifizierter Task-Typ
    plan: Optional[str]                # Generierter Plan
    current_agent: Optional[str]       # Aktuell aktiver Agent
    intermediate_results: dict         # Ergebnisse aller Sub-Agents
    error: Optional[str]               # Fehlermeldung (falls vorhanden)
    retry_count: int                   # Retry-Zähler


# ─── Agent Factory ───────────────────────────────────────────────────────────

def create_agent_executor(
    agent_name: str,
    system_prompt: str,
    tools: list,
    model_type: str = "primary",
    max_iterations: int = 10,
) -> AgentExecutor:
    """Erstelle einen standardisierten LangChain AgentExecutor.
    
    >>> code_agent = create_agent_executor(
    ...     "CodeAgent",
    ...     "Du bist ein Senior Software Engineer...",
    ...     tools=[run_shell, search_code],
    ... )
    """
    llm = get_llm_for_task(model_type)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=os.getenv("AGENT_VERBOSE", "false").lower() == "true",
        max_iterations=max_iterations,
        handle_parsing_errors=True,
        max_execution_time=120,  # 2 Minuten Max
        return_intermediate_steps=True,
    )


# ─── Task Classifier ─────────────────────────────────────────────────────────

TASK_ROUTING = {
    "code": "code_agent",
    "research": "research_agent",
    "analyze": "research_agent",
    "deploy": "deploy_agent",
    "qa": "qa_agent",
    "chat": "research_agent",
    "plan": "plan_agent",
    "default": "research_agent",
}

def classify_task(state: AgentState) -> str:
    """Klassifiziere den Task-Typ und route zum richtigen Agenten.
    
    Ersetzt: orchestrator_v3.py's Intent-basiertes Routing + keyword matching.
    """
    task = state.get("task", "")
    task_lower = task.lower()
    
    # Keyword-basierte Klassifikation (schnell, kein LLM nötig)
    if any(w in task_lower for w in ["code", "programmier", "implementier", "schreib", "entwickel", "refactor", "fix"]):
        task_type = "code"
    elif any(w in task_lower for w in ["recherchier", "forschung", "analysier", "vergleich", "erkläre", "was ist"]):
        task_type = "research"
    elif any(w in task_lower for w in ["deploy", "deployment", "release", "ausliefer"]):
        task_type = "deploy"
    elif any(w in task_lower for w in ["test", "prüf", "validier", "qa", "qualität"]):
        task_type = "qa"
    elif any(w in task_lower for w in ["plan", "strategie", "roadmap", "architektur"]):
        task_type = "plan"
    else:
        task_type = "research"
    
    return TASK_ROUTING.get(task_type, "research_agent")


# ─── Agent Prompt Templates ──────────────────────────────────────────────────

CODE_AGENT_PROMPT = """Du bist ein Senior Software Engineer in einem Enterprise-Projekt.

Deine Aufgabe: Implementiere, refaktoriere oder repariere Code.

Richtlinien:
- Lese immer zuerst den bestehenden Code (search_code)
- Mache minimale, fokussierte Änderungen
- Füge Typannotationen und Docstrings hinzu
- Teste deine Änderungen
- Dokumentiere Architektur-Entscheidungen im Brain

Verfügbare Tools:
- search_code: Durchsuche die Codebase
- run_shell: Führe Shell-Befehle aus
- brain_search: Suche im Enterprise Brain
- store_brain_note: Speichere Wissen"""

RESEARCH_AGENT_PROMPT = """Du bist ein Enterprise Research Analyst.

Deine Aufgabe: Recherchiere, analysiere und fasse Informationen zusammen.

Richtlinien:
- Suche immer zuerst im Enterprise Brain (brain_search)
- Nutze externe Quellen bei Bedarf
- Zitiere deine Quellen mit [Source N]
- Strukturiere Antworten mit Überschriften
- Bei Unsicherheit: Sag es, statt zu raten

Verfügbare Tools:
- brain_search: Suche in der Wissensdatenbank
- check_system_health: Prüfe System-Status
- query_database: Führe Datenbank-Abfragen aus"""

QA_AGENT_PROMPT = """Du bist ein Quality Assurance Engineer.

Deine Aufgabe: Prüfe und validiere Code, Konfiguration und Architektur.

Richtlinien:
- Prüfe auf Security-Issues (harte Kodierung, SQL-Injection, XSS)
- Validiere Code-Style und Best Practices
- Prüfe auf fehlende Tests
- Dokumentiere gefundene Issues im Brain

Verfügbare Tools:
- search_code: Durchsuche die Codebase
- run_shell: Führe Tests aus
- brain_search: Suche nach bekannten Issues
- store_brain_note: Dokumentiere QA-Ergebnisse"""


# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def create_agent_node(agent_name: str, prompt: str, tools_list: list):
    """Factory für Agent-Nodes im StateGraph.
    
    Jeder Node erhält:
    - Einen spezifischen System-Prompt
    - Rollenbasierte Tools
    - Zugriff auf den Shared State
    """
    executor = create_agent_executor(agent_name, prompt, tools_list)
    
    def node_fn(state: AgentState) -> dict:
        """Führe den Agent aus und aktualisiere den State."""
        task = state.get("task", "")
        
        logger.info(f"[{agent_name}] Verarbeite: {task[:80]}...")
        
        try:
            result = executor.invoke({
                "input": task,
                "chat_history": state.get("messages", []),
            })
            
            # Ergebnisse in den State schreiben
            new_messages = [AIMessage(content=result["output"])]
            intermediate = state.get("intermediate_results", {})
            intermediate[agent_name] = {
                "output": result["output"],
                "steps": result.get("intermediate_steps", []),
            }
            
            return {
                "messages": new_messages,
                "current_agent": agent_name,
                "intermediate_results": intermediate,
                "error": None,
            }
        except Exception as e:
            logger.error(f"[{agent_name}] Fehler: {str(e)}")
            return {
                "error": str(e),
                "current_agent": agent_name,
                "retry_count": state.get("retry_count", 0) + 1,
            }
    
    return node_fn


# ─── Synthesizer (Ergebnis-Zusammenführung) ──────────────────────────────────

def create_synthesizer():
    """Fasst Ergebnisse aller Sub-Agents zusammen.
    
    Ersetzt: oracle_engine.py's _verify_result() + manuelle Ergebnis-Extraktion.
    """
    llm = get_llm_for_task("summarize")
    
    def synthesize(state: AgentState) -> dict:
        """Synthetisiere die Ergebnisse aller Agenten."""
        results = state.get("intermediate_results", {})
        task = state.get("task", "")
        
        if not results:
            return {"messages": [AIMessage(content="Keine Ergebnisse von Sub-Agents.")]}
        
        # Bei nur einem Agent: direkt zurückgeben
        if len(results) == 1:
            result = list(results.values())[0]
            return {"messages": [AIMessage(content=result["output"])]}
        
        # Mehrere Agenten: Zusammenfassung generieren
        synthesis_prompt = f"""Fasse die folgenden Agent-Ergebnisse für die Aufgabe "{task}" zusammen.
        
Ergebnisse:
{json.dumps({k: v["output"][:500] for k, v in results.items()}, indent=2)}

Gib eine konsolidierte Antwort mit den wichtigsten Erkenntnissen."""
        
        response = llm.invoke(synthesis_prompt)
        return {"messages": [AIMessage(content=response.content)]}
    
    return synthesize


# ─── Entscheidungslogik für Graph-Edges ──────────────────────────────────────

def should_retry(state: AgentState) -> Literal["agent", "synthesize", "error"]:
    """Entscheide basierend auf dem State: Retry? Weiter? Abbruch?"""
    if state.get("error"):
        if state.get("retry_count", 0) < 2:
            return "agent"  # Max 2 Retrys
        return "error"
    return "synthesize"


def route_to_agent(state: AgentState) -> str:
    """Route zur richtigen Agent-Klasse basierend auf Task-Typ."""
    return classify_task(state)


# ─── Main Graph Builder ──────────────────────────────────────────────────────

def build_supervisor_graph() -> StateGraph:
    """Baue den Supervisor-Graphen (Top-Level Orchestrator).
    
    Ersetzt: orchestrator_v3.py (448 Zeilen)
    
    Der Graph:
    1. START → classifier (bestimmt Agent-Typ)
    2. classifier → [code_agent | research_agent | qa_agent | deploy_agent]
    3. agent → should_retry? (retry | synthesize | error)
    4. synthesize → END
    
    Nutzung:
        graph = build_supervisor_graph()
        result = graph.invoke({
            "task": "Implementiere eine Login-Funktion",
            "messages": [],
            "intermediate_results": {},
            "retry_count": 0,
        })
    """
    # Tools vorbereiten
    all_tools = get_all_tools()
    code_tools = get_agent_tools("developer")
    research_tools = get_agent_tools("research")
    qa_tools = [t for t in all_tools if t.name in ["search_code", "run_shell", "brain_search", "store_brain_note"]]
    
    # Graph definieren
    workflow = StateGraph(AgentState)
    
    # Nodes registrieren
    workflow.add_node("classifier", classify_task)
    workflow.add_node("code_agent", create_agent_node("code_agent", CODE_AGENT_PROMPT, code_tools))
    workflow.add_node("research_agent", create_agent_node("research_agent", RESEARCH_AGENT_PROMPT, research_tools))
    workflow.add_node("qa_agent", create_agent_node("qa_agent", QA_AGENT_PROMPT, qa_tools))
    workflow.add_node("synthesize", create_synthesizer())
    workflow.add_node("error", lambda s: {"messages": [AIMessage(content=f"Fehler nach Retry: {s.get('error', 'Unknown')}")]})
    
    # Edges definieren
    workflow.add_edge(START, "classifier")
    workflow.add_conditional_edges(
        "classifier",
        route_to_agent,
        {
            "code_agent": "code_agent",
            "research_agent": "research_agent",
            "qa_agent": "qa_agent",
        }
    )
    
    # Alle Agenten → Synthesizer (mit Retry-Möglichkeit)
    for agent in ["code_agent", "research_agent", "qa_agent"]:
        workflow.add_conditional_edges(
            agent,
            should_retry,
            {
                "agent": agent,      # Retry
                "synthesize": "synthesize",
                "error": "error",
            }
        )
    
    workflow.add_edge("synthesize", END)
    workflow.add_edge("error", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# ─── Convenience API (ersetzt agent_executor.py's main) ──────────────────────

_supervisor = None

def get_supervisor() -> StateGraph:
    """Globaler Supervisor (Singleton)."""
    global _supervisor
    if _supervisor is None:
        _supervisor = build_supervisor_graph()
    return _supervisor


def run_agent(task: str, thread_id: str = "default") -> dict:
    """Führe einen Task mit dem Supervisor-Graphen aus.
    
    >>> result = run_agent("Recherchiere die neuesten AI-Trends")
    >>> print(result["messages"][-1].content)
    
    Args:
        task: Die Aufgabe für den Agenten
        thread_id: Session-ID für Conversation Memory
    
    Returns: Kompletter State mit allen Ergebnissen
    """
    graph = get_supervisor()
    
    result = graph.invoke(
        {
            "task": task,
            "messages": [],
            "intermediate_results": {},
            "retry_count": 0,
            "task_type": "",
            "current_agent": None,
            "plan": None,
            "error": None,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    
    return result


def stream_agent(task: str, thread_id: str = "default"):
    """Streaming-Version des Agenten.
    
    >>> for event in stream_agent("Erkläre Lambda-Funktionen"):
    ...     if isinstance(event, AIMessage):
    ...         print(event.content, end="", flush=True)
    """
    graph = get_supervisor()
    
    for event in graph.stream(
        {
            "task": task,
            "messages": [],
            "intermediate_results": {},
            "retry_count": 0,
        },
        config={"configurable": {"thread_id": thread_id}},
    ):
        yield event
