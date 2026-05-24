"""
LangGraph Oracle Workflow — Enterprise Autonomous Task Engine
==============================================================
Ersetzt: oracle_engine.py (815 Zeilen)

Der Oracle-Workflow implementiert den kompletten Task-Lifecycle als StateGraph:
  
  DISCOVERED → PLANNED → EXECUTING → VERIFIED → STORED → COMPLETED
                                                ↘ FAILED → LEARNED

Jeder Status ist ein Graph-Node mit:
- Klarer Eingabe-/Ausgabe-Schnittstelle
- Automatischer Status-Transition via Conditional Edges
- Learning-Persistenz (Brain-Store) bei Erfolg/Fehler
"""
import os
import json
import logging
from typing import Annotated, Sequence, TypedDict, Literal, Optional
from datetime import datetime, timezone
from enum import Enum

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor

from langchain_config import get_llm_for_task, create_llm_with_fallbacks
from tool_registry import get_agent_tools

logger = logging.getLogger("nexifyai.oracle")


# ─── Status-Enum ──────────────────────────────────────────────────────────────

class OracleStatus(str, Enum):
    """Task-Lifecycle-Status (ersetzt 13 Custom-Konstanten)."""
    DISCOVERED = "discovered"
    PLANNED = "planned"
    EXECUTING = "executing"
    VERIFIED = "verified"
    STORED = "stored"
    COMPLETED = "completed"
    FAILED = "failed"
    LEARNED = "learned"


# ─── Oracle State ─────────────────────────────────────────────────────────────

class OracleState(TypedDict):
    """State für den Oracle Workflow."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    task_id: str
    task: str
    status: OracleStatus
    context: dict                      # Task-Kontext (Kunde, Projekt, etc.)
    knowledge: list                    # Aggregiertes Wissen (Brain + Quellen)
    agent_result: Optional[str]        # Ergebnis des Ausführungs-Agenten
    verification_score: Optional[float] # Verifikations-Score (0-10)
    verification_feedback: Optional[str]
    error: Optional[str]
    retry_count: int
    created_at: str
    completed_at: Optional[str]


# ─── Agent Factory (Oracle-spezifisch) ────────────────────────────────────────

def create_oracle_agent(
    system_prompt: str,
    tools: list,
    temperature: float = 0.3,
) -> AgentExecutor:
    """Erstelle einen Oracle-spezifischen AgentExecutor."""
    llm = create_llm_with_fallbacks(temperature=temperature)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
    )


# ─── Prompt Templates ─────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """Du bist ein Enterprise-Analyst im Oracle-System.

Analysiere die folgende Aufgabe und erstelle einen detaillierten Ausführungsplan.

Aufgabe: {task}
Kontext: {context}

Erstelle einen Plan mit:
1. ANALYSE: Was wird benötigt?
2. QUELLEN: Welche Wissensquellen sind relevant?
3. LÖSUNGSANSATZ: Wie wird vorgegangen?
4. NÄCHSTE SCHRITTE: Konkrete Aktionen"""

EXECUTION_PROMPT = """Du bist ein Autonomous Execution Agent im Oracle-System.

Führe die geplante Aufgabe aus. Nutze die verfügbaren Tools.

Aufgabe: {task}
Plan: {plan}
Wissen: {knowledge}

Erwartete Ausgabe:
- ANALYSE: Vollständige Analyse
- LÖSUNG: Konkrete Lösung/Ergebnis
- NÄCHSTE SCHRITTE: Empfehlungen"""

VERIFICATION_PROMPT = """Du bist ein Quality Assurance Agent im Oracle-System.

Prüfe das folgende Ergebnis auf Korrektheit und Vollständigkeit.

Aufgabe: {task}
Ergebnis: {result}

Bewerte:
1. Korrektheit (0-10): Ist das Ergebnis fachlich richtig?
2. Vollständigkeit (0-10): Deckt das Ergebnis alle Aspekte ab?
3. Qualität (0-10): Ist die Antwort strukturiert und nützlich?
4. Kritik: Was könnte verbessert werden?

Gib ein JSON-Objekt mit: score, feedback, improvements"""


# ─── Graph Nodes ──────────────────────────────────────────────────────────────

def discover_node(state: OracleState) -> dict:
    """DISCOVERED → PLANNED: Aufgabe analysieren und Kontext sammeln."""
    tools = get_agent_tools("research")
    agent = create_oracle_agent(ANALYSIS_PROMPT.format(
        task=state["task"],
        context=json.dumps(state.get("context", {}), indent=2)
    ), tools)
    
    logger.info(f"[Oracle] Analysiere Aufgabe: {state['task'][:80]}...")
    
    result = agent.invoke({"input": f"Analysiere: {state['task']}"})
    
    return {
        "status": OracleStatus.PLANNED,
        "messages": [AIMessage(content=result["output"])],
    }


def execute_node(state: OracleState) -> dict:
    """PLANNED → EXECUTING: Aufgabe ausführen mit Tools."""
    tools = get_agent_tools("oracle")
    plan = state["messages"][-1].content if state["messages"] else "Kein Plan erstellt"
    knowledge = state.get("knowledge", [])
    
    agent = create_oracle_agent(EXECUTION_PROMPT.format(
        task=state["task"],
        plan=plan,
        knowledge=json.dumps(knowledge, indent=2)[:2000]
    ), tools)
    
    logger.info(f"[Oracle] Führe aus: {state['task'][:80]}...")
    
    try:
        result = agent.invoke({"input": f"Führe aus: {state['task']}"})
        return {
            "status": OracleStatus.EXECUTING,
            "agent_result": result["output"],
            "messages": [AIMessage(content=result["output"])],
        }
    except Exception as e:
        return {
            "status": OracleStatus.FAILED,
            "error": str(e),
            "retry_count": state.get("retry_count", 0) + 1,
        }


def verify_node(state: OracleState) -> dict:
    """EXECUTING → VERIFIED: Ergebnis verifizieren."""
    result = state.get("agent_result", "")
    if not result:
        return {"status": OracleStatus.FAILED, "error": "Kein Ergebnis zur Verifikation"}
    
    llm = get_llm_for_task("analyze", temperature=0.0)
    
    prompt = VERIFICATION_PROMPT.format(
        task=state["task"],
        result=result[:2000],
    )
    
    logger.info(f"[Oracle] Verifiziere Ergebnis...")
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Extrahiere Score (einfaches Parsing)
        import re
        score_match = re.search(r'(?:score|bewertung|gesamt)[:\s]*(\d+(?:\.\d+)?)', content.lower())
        score = float(score_match.group(1)) if score_match else 5.0
        
        return {
            "status": OracleStatus.VERIFIED,
            "verification_score": score,
            "verification_feedback": content,
            "messages": [AIMessage(content=f"Verifikation: {score}/10\n{content}")],
        }
    except Exception as e:
        return {
            "status": OracleStatus.VERIFIED,
            "verification_score": 5.0,
            "verification_feedback": f"Verifikation fehlgeschlagen: {str(e)}",
        }


def store_node(state: OracleState) -> dict:
    """VERIFIED → STORED: Ergebnis ins Brain persistieren."""
    result = state.get("agent_result", "")
    score = state.get("verification_score", 5.0)
    
    try:
        import httpx
        brain_url = os.getenv("BRAIN_API_URL", "http://localhost:8420")
        
        payload = {
            "content": f"# Oracle Task Result\n\n**Task:** {state['task']}\n\n**Score:** {score}/10\n\n**Ergebnis:**\n{result[:5000]}",
            "category": "oracle_result" if score >= 7 else "oracle_failed",
            "tags": ["oracle", state.get("context", {}).get("category", "general")],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        response = httpx.post(f"{brain_url}/store", json=payload, timeout=10)
        
        if response.status_code in (200, 201):
            logger.info(f"[Oracle] Ergebnis gespeichert (Score: {score}/10)")
            return {
                "status": OracleStatus.COMPLETED if score >= 7 else OracleStatus.STORED,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            logger.warning(f"[Oracle] Speichern fehlgeschlagen: HTTP {response.status_code}")
            return {"status": OracleStatus.COMPLETED}  # Trotzdem als completed markieren
            
    except Exception as e:
        logger.warning(f"[Oracle] Brain nicht erreichbar: {str(e)}")
        return {"status": OracleStatus.COMPLETED}


def learn_node(state: OracleState) -> dict:
    """FAILED → LEARNED: Aus Fehlern lernen."""
    error = state.get("error", "Unbekannter Fehler")
    
    try:
        import httpx
        brain_url = os.getenv("BRAIN_API_URL", "http://localhost:8420")
        
        payload = {
            "content": f"# Oracle Failure Learning\n\n**Task:** {state['task']}\n\n**Fehler:** {error}\n\n**Status:** Task fehlgeschlagen nach {state.get('retry_count', 0)} Versuchen",
            "category": "oracle_failure",
            "tags": ["oracle", "failure", "learning"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        httpx.post(f"{brain_url}/store", json=payload, timeout=5)
    except Exception:
        pass
    
    return {
        "status": OracleStatus.LEARNED,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Conditional Edges ────────────────────────────────────────────────────────

def route_from_verification(state: OracleState) -> Literal["store", "execute", "failed"]:
    """Nach Verifikation: Bestanden → Store, Grenzwertig → Retry, Durchgefallen → Failed."""
    score = state.get("verification_score", 0)
    
    if score >= 7:
        return "store"
    elif score >= 4 and state.get("retry_count", 0) < 2:
        return "execute"  # Retry mit verbessertem Kontext
    else:
        return "failed"


def route_from_execution(state: OracleState) -> Literal["verify", "discover", "failed"]:
    """Nach Execution: Normal → Verify, Fehler → Discover (Retry), Schwerer Fehler → Failed."""
    if state.get("error"):
        if state.get("retry_count", 0) < 2:
            return "discover"  # Neu planen mit Fehlerkontext
        return "failed"
    return "verify"


def route_from_failure(state: OracleState) -> Literal["learn", "discover"]:
    """Nach Failure: Lernen oder nochmal versuchen?"""
    if state.get("retry_count", 0) < 3:
        return "discover"
    return "learn"


# ─── Graph Builder ────────────────────────────────────────────────────────────

def build_oracle_graph() -> StateGraph:
    """Baue den Oracle StateGraph.
    
    Lifecycle:
        START → discover → execute → verify → store → END
                   ↑          ↑         ↓        ↓
                   └──── retry ┘     failed → learn → END
    
    Alle Nodes haben Zugriff auf den geteilten OracleState.
    LangGraph's Checkpointer sorgt für Persistenz und Recovery.
    """
    workflow = StateGraph(OracleState)
    
    # Nodes
    workflow.add_node("discover", discover_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("store", store_node)
    workflow.add_node("learn", learn_node)
    workflow.add_node("failed", lambda s: {"status": OracleStatus.FAILED, "completed_at": datetime.now(timezone.utc).isoformat()})
    
    # Edges
    workflow.add_edge(START, "discover")
    workflow.add_edge("discover", "execute")
    
    workflow.add_conditional_edges(
        "execute",
        route_from_execution,
        {
            "verify": "verify",
            "discover": "discover",
            "failed": "failed",
        }
    )
    
    workflow.add_conditional_edges(
        "verify",
        route_from_verification,
        {
            "store": "store",
            "execute": "execute",
            "failed": "failed",
        }
    )
    
    workflow.add_edge("store", END)
    
    workflow.add_conditional_edges(
        "failed",
        route_from_failure,
        {
            "learn": "learn",
            "discover": "discover",
        }
    )
    
    workflow.add_edge("learn", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# ─── Convenience API (ersetzt OracleEngine.process_cycle) ─────────────────────

_oracle_graph = None

def get_oracle() -> StateGraph:
    """Globaler Oracle-Graph (Singleton)."""
    global _oracle_graph
    if _oracle_graph is None:
        _oracle_graph = build_oracle_graph()
    return _oracle_graph


def run_oracle_task(
    task: str,
    context: Optional[dict] = None,
    task_id: Optional[str] = None,
    thread_id: str = "oracle_default",
) -> dict:
    """Führe einen kompletten Oracle-Task-Lifecycle aus.
    
    >>> result = run_oracle_task(
    ...     "Analysiere die aktuelle System-Health",
    ...     context={"category": "monitoring"}
    ... )
    >>> print(f"Status: {result['status']}, Score: {result.get('verification_score')}")
    
    Args:
        task: Die zu bearbeitende Aufgabe
        context: Task-Kontext (Kunde, Projekt, Kategorie)
        task_id: Eindeutige Task-ID (auto-generiert wenn None)
        thread_id: Session-ID für Checkpointing
    
    Returns: Kompletter OracleState mit allen Ergebnissen
    """
    import uuid
    
    graph = get_oracle()
    
    initial_state = {
        "task_id": task_id or f"oracle_{uuid.uuid4().hex[:12]}",
        "task": task,
        "status": OracleStatus.DISCOVERED,
        "context": context or {},
        "knowledge": [],
        "agent_result": None,
        "verification_score": None,
        "verification_feedback": None,
        "error": None,
        "retry_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "messages": [],
    }
    
    result = graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )
    
    return result


def get_oracle_status(task_id: str) -> Optional[dict]:
    """Hole den Status eines Oracle-Tasks aus dem Checkpointer.
    
    >>> get_oracle_status("oracle_abc123def456")
    """
    graph = get_oracle()
    try:
        state = graph.get_state({"configurable": {"thread_id": f"oracle_{task_id}"}})
        return state.values if state else None
    except Exception:
        return None
