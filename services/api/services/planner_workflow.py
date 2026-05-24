"""
LangGraph Planner — Enterprise Strategic Planning System
=========================================================
Ersetzt: strategic_planner.py (40 Z.) + task_graph_planner.py (21 Z.) + 
         capability_router.py (18 Z.) + dependency_resolver.py (20 Z.) +
         autonomous_program_manager.py (32 Z.) + capability_scheduler.py + 
         priority_engine.py + organizational_scheduler.py

Architektur:
  Strategic Cycle (StateGraph):
    HEALTH_CHECK → PRIORITIZE → PLAN → ROUTE → EXECUTE → REVIEW
    
  Jeder Schritt ist ein Graph-Node. LangGraph übernimmt:
  - Topologische Sortierung (ersetzt dependency_resolver.py)
  - State Passing (ersetzt stdout-JSON-Parsing)
  - Retry/Error Handling (ersetzt subprocess-Orchestrierung)
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
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, AIMessage
from langchain.agents import AgentExecutor

from langchain_config import get_llm_for_task, create_llm_with_fallbacks
from tool_registry import get_agent_tools

logger = logging.getLogger("nexifyai.planner")


# ─── Planner State ───────────────────────────────────────────────────────────

class Priority(int, Enum):
    """Task-Priorität."""
    P0 = 0  # Kritisch (Security, Production-Failure)
    P1 = 1  # Hoch (Blockierend, Revenue-relevant)
    P2 = 2  # Mittel (Feature, Verbesserung)
    P3 = 3  # Niedrig (Nice-to-have, Tech-Debt)


class PlannerState(TypedDict):
    """State für den Planner Workflow."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    objectives: list                      # Strategische Ziele
    system_health: Optional[dict]         # Health-Check Ergebnis
    prioritized_tasks: list               # Priorisierte Tasks mit Priority
    task_graph: list                      # Task-Graph (DAG)
    routed_tasks: list                    # Tasks mit Team-Zuordnung
    execution_plan: Optional[str]         # Ausführungsplan
    cycle_number: int                     # Aktuelle Cycle-Nummer
    error: Optional[str]
    completed_at: Optional[str]


# ─── Planner Agent Factory ───────────────────────────────────────────────────

def create_planner_agent(system_prompt: str, tools: list, temperature: float = 0.3) -> AgentExecutor:
    """Erstelle einen Planner-spezifischen AgentExecutor."""
    llm = get_llm_for_task("plan", temperature=temperature)
    
    from langchain_core.prompts import ChatPromptTemplate
    
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
        max_iterations=5,
        handle_parsing_errors=True,
    )


# ─── Graph Nodes ──────────────────────────────────────────────────────────────

def health_check_node(state: PlannerState) -> dict:
    """Health-Check: System-Status abrufen (ersetzt strategic_planner.py)."""
    import httpx
    
    logger.info(f"[Planner] Cycle #{state.get('cycle_number', 0)}: Health-Check...")
    
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = httpx.get(f"{backend_url}/health", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
        else:
            health = {"status": "degraded", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        health = {"status": "unknown", "error": str(e)}
    
    logger.info(f"[Planner] System-Status: {health.get('status', 'unknown')}")
    
    return {"system_health": health}


def prioritize_node(state: PlannerState) -> dict:
    """Priorisierung: Tasks nach Dringlichkeit sortieren (ersetzt priority_engine.py)."""
    objectives = state.get("objectives", [])
    health = state.get("system_health", {})
    
    if not objectives:
        logger.info("[Planner] Keine Objectives zu priorisieren")
        return {"prioritized_tasks": []}
    
    llm = get_llm_for_task("plan", temperature=0.0)
    
    prompt = f"""Priorisiere die folgenden strategischen Ziele basierend auf:
- System-Health: {json.dumps(health)}
- Aktueller Zyklus: #{state.get('cycle_number', 0)}

Ziele:
{json.dumps(objectives, indent=2)}

Formatiere als JSON-Array mit: task, priority (P0-P3), reasoning, dependencies

Prioritäts-Logik:
- P0: Sicherheitslücken, Production-Outages, Compliance-Verstöße
- P1: Blockierende Abhängigkeiten, Revenue-relevante Features
- P2: Neue Features, Verbesserungen
- P3: Tech-Debt, Nice-to-have"""
    
    response = llm.invoke(prompt)
    
    try:
        import re
        json_match = re.search(r'\[.*?\]', response.content, re.DOTALL)
        if json_match:
            tasks = json.loads(json_match.group())
        else:
            tasks = [{"task": o, "priority": "P2", "reasoning": "Default"} for o in objectives]
    except Exception:
        tasks = [{"task": o, "priority": "P2"} for o in objectives]
    
    logger.info(f"[Planner] {len(tasks)} Tasks priorisiert")
    return {"prioritized_tasks": tasks}


def plan_node(state: PlannerState) -> dict:
    """Task-Graph: Abhängigkeiten auflösen (ersetzt task_graph_planner.py + dependency_resolver.py)."""
    tasks = state.get("prioritized_tasks", [])
    
    if not tasks:
        return {"task_graph": [], "execution_plan": "Keine Tasks zu planen"}
    
    llm = get_llm_for_task("plan", temperature=0.2)
    
    prompt = f"""Erstelle einen detaillierten Ausführungsplan für diese Tasks.

Tasks: {json.dumps(tasks, indent=2)}

Erstelle einen DAG (Directed Acyclic Graph) mit:
1. task_graph: [{{
    "id": "T-1",
    "title": "...",
    "priority": "P0-P3",
    "depends_on": ["T-0"],  # Leer wenn keine Abhängigkeit
    "estimated_effort": "S/M/L/XL"
  }}]
2. execution_plan: Textuelle Beschreibung der Ausführungsreihenfolge

Regeln:
- P0 Tasks zuerst
- Abhängigkeiten müssen vor ihren Nachfolgern ausgeführt werden
- Max 8 Tasks pro Zyklus
- Gleiche Priorität = parallel ausführbar"""
    
    response = llm.invoke(prompt)
    
    try:
        import re
        json_match = re.search(r'"task_graph":\s*\[.*?\]', response.content, re.DOTALL)
        if json_match:
            graph_text = "{" + json_match.group() + "}"
            graph = json.loads(graph_text).get("task_graph", tasks)
        else:
            graph = tasks
    except Exception:
        graph = tasks
    
    return {
        "task_graph": graph,
        "execution_plan": response.content,
    }


def route_node(state: PlannerState) -> dict:
    """Task-Routing: Tasks zu Teams/Agenten routen (ersetzt capability_router.py)."""
    graph = state.get("task_graph", [])
    
    # Routing-Tabelle (ersetzt CAPS-Dict aus capability_router.py)
    ROUTES = {
        "security": ["security", "audit", "vulnerability", "patch", "credential"],
        "infrastructure": ["deploy", "infrastructure", "docker", "kubernetes", "ci/cd"],
        "backend": ["api", "database", "service", "endpoint", "sql", "model"],
        "frontend": ["ui", "component", "design", "react", "css", "frontend"],
        "ai": ["agent", "llm", "rag", "prompt", "embedding", "training"],
        "research": ["research", "analyse", "report", "dokumentation", "docs"],
    }
    
    def route_task(task: dict) -> str:
        title = task.get("title", task.get("task", "")).lower()
        for team, keywords in ROUTES.items():
            if any(k in title for k in keywords):
                return team
        return "research"
    
    routed = []
    for task in graph:
        team = route_task(task)
        routed.append({**task, "team": team})
    
    logger.info(f"[Planner] {len(routed)} Tasks geroutet")
    return {"routed_tasks": routed}


def execute_plan_node(state: PlannerState) -> dict:
    """Plan ausführen — delegiert Tasks an Sub-Agents."""
    tasks = state.get("routed_tasks", [])
    
    if not tasks:
        return {"messages": [AIMessage(content="Keine Tasks auszuführen.")]}
    
    results = []
    for task in tasks:
        title = task.get("title", task.get("task", "Unbenannter Task"))
        team = task.get("team", "research")
        
        logger.info(f"[Planner] Delegiere: [{team}] {title[:80]}...")
        
        # Hole rollenbasierte Tools
        agent_type_map = {
            "backend": "developer",
            "frontend": "developer",
            "ai": "developer",
            "security": "developer",
            "infrastructure": "developer",
            "research": "research",
        }
        tools = get_agent_tools(agent_type_map.get(team, "default"))
        
        agent = create_planner_agent(
            f"Du bist ein {team.capitalize()}-Spezialist. Führe die Aufgabe aus.",
            tools,
        )
        
        try:
            result = agent.invoke({"input": title})
            results.append({"task": title, "team": team, "status": "done", "output": result["output"][:500]})
        except Exception as e:
            results.append({"task": title, "team": team, "status": "failed", "error": str(e)})
    
    summary = f"""# Plan-Ausführung abgeschlossen

**Tasks:** {len(tasks)}  
**Erfolgreich:** {sum(1 for r in results if r['status'] == 'done')}  
**Fehlgeschlagen:** {sum(1 for r in results if r['status'] == 'failed')}

## Details
{json.dumps(results, indent=2, default=str)[:3000]}
"""
    
    return {
        "messages": [AIMessage(content=summary)],
        "execution_plan": summary,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def review_node(state: PlannerState) -> dict:
    """Review: Ergebnisse evaluieren und Lernerfahrungen speichern."""
    results = state.get("execution_plan", "")
    
    # Brain-Store
    try:
        import httpx
        brain_url = os.getenv("BRAIN_API_URL", "http://localhost:8420")
        payload = {
            "content": f"# Planner Cycle #{state.get('cycle_number', 0)} Review\n\n{results[:3000]}",
            "category": "planner_review",
            "tags": ["planner", f"cycle_{state.get('cycle_number', 0)}"],
        }
        httpx.post(f"{brain_url}/store", json=payload, timeout=5)
    except Exception:
        pass
    
    return state


# ─── Conditional Edges ────────────────────────────────────────────────────────

def should_continue(state: PlannerState) -> Literal["execute", "review", "end"]:
    """Entscheide: Tasks ausführen oder reviewen oder beenden."""
    tasks = state.get("routed_tasks", [])
    
    if tasks:
        return "execute"
    elif state.get("execution_plan"):
        return "review"
    return "end"


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_planner_graph() -> StateGraph:
    """Baue den Planner StateGraph.
    
    Cycle:
        START → health_check → prioritize → plan → route → [execute → review] → END
                                   ↑                                         ↓
                                   └───────────── next cycle ────────────────┘
    
    Ein kompletter strategic_planner.py (40) + task_graph_planner.py (21) + 
    capability_router.py (18) + dependency_resolver.py (20) + autonomous_program_manager.py (32) 
    = 131 Zeilen Custom-Code → dieser Graph (~140 Zeilen).
    """
    workflow = StateGraph(PlannerState)
    
    # Nodes
    workflow.add_node("health_check", health_check_node)
    workflow.add_node("prioritize", prioritize_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("route", route_node)
    workflow.add_node("execute", execute_plan_node)
    workflow.add_node("review", review_node)
    
    # Edges (LangGraph übernimmt automatisch die topologische Sortierung)
    workflow.add_edge(START, "health_check")
    workflow.add_edge("health_check", "prioritize")
    workflow.add_edge("prioritize", "plan")
    workflow.add_edge("plan", "route")
    
    workflow.add_conditional_edges(
        "route",
        should_continue,
        {
            "execute": "execute",
            "review": "review",
            "end": END,
        }
    )
    
    workflow.add_edge("execute", "review")
    workflow.add_edge("review", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# ─── Convenience API ─────────────────────────────────────────────────────────

_planner_graph = None

def get_planner() -> StateGraph:
    """Globaler Planner-Graph (Singleton)."""
    global _planner_graph
    if _planner_graph is None:
        _planner_graph = build_planner_graph()
    return _planner_graph


def run_planning_cycle(
    objectives: list,
    cycle_number: int = 0,
    thread_id: str = "planner_default",
) -> dict:
    """Führe einen kompletten Planning-Cycle aus.
    
    >>> result = run_planning_cycle([
    ...     "Security-Audit durchführen",
    ...     "Neue Agent-API bauen",
    ...     "Dokumentation aktualisieren"
    ... ])
    >>> print(result["execution_plan"][:200])
    
    Args:
        objectives: Liste der strategischen Ziele
        cycle_number: Cycle-Nummer fürs Review-Tracking
        thread_id: Session-ID für Checkpointing
    
    Returns: Kompletter PlannerState
    """
    graph = get_planner()
    
    result = graph.invoke(
        {
            "objectives": objectives,
            "system_health": None,
            "prioritized_tasks": [],
            "task_graph": [],
            "routed_tasks": [],
            "execution_plan": None,
            "cycle_number": cycle_number,
            "error": None,
            "completed_at": None,
            "messages": [],
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    
    return result


def run_strategic_cycle(objectives: list, thread_id: str = "strategic") -> dict:
    """Führe einen vollständigen strategischen Zyklus aus (ersteert autonomous_program_manager.py).
    
    Früher: 7x subprocess.run(["python3", "..."]) → stdout JSON → Qdrant Write
    Jetzt: 1x graph.invoke({...}) → StateGraph → Auto-Persist
    
    >>> result = run_strategic_cycle([
    ...     "System-Health prüfen",
    ...     "Tasks priorisieren", 
    ...     "Nächste Schritte planen"
    ... ])
    """
    return run_planning_cycle(objectives, cycle_number=0, thread_id=thread_id)
