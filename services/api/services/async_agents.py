"""
LangChain Async Layer — Enterprise Async Agent Execution
=========================================================
Erweitert: langchain_config.py, agent_system.py, oracle_workflow.py

Bietet Async-Varianten aller Agent-Operationen für:
- FastAPI-Endpoints (kein Blocking)
- Parallele Task-Ausführung
- Streaming via Server-Sent Events

Nutzt LangChain's native Async-Support (.ainvoke(), .astream()).
"""
import os
import json
import logging
from typing import AsyncIterator, Optional

from langchain_core.messages import AIMessage

from langchain_config import get_llm_for_task, create_llm_with_fallbacks
from agent_system import build_supervisor_graph
from tool_registry import get_agent_tools, get_all_tools

logger = logging.getLogger("nexifyai.async_agents")


# ─── Async Agent Execution ───────────────────────────────────────────────────

async def arun_agent(
    task: str,
    thread_id: str = "default",
) -> dict:
    """Async-Version von run_agent().
    
    Nutzt LangGraph's ainvoke() für nicht-blockierende Ausführung.
    
    >>> result = await arun_agent("Was sind Python Decorators?")
    >>> print(result["messages"][-1].content)
    """
    graph = build_supervisor_graph()
    
    result = await graph.ainvoke(
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


async def astream_agent(task: str, thread_id: str = "default") -> AsyncIterator[dict]:
    """Async-Streaming-Version des Agenten.
    
    Nutzt LangGraph's astream() für Echtzeit-Output.
    
    async for event in astream_agent("Erkläre Lambda-Funktionen"):
        if "output" in event:
            print(event["output"], end="", flush=True)
    """
    graph = build_supervisor_graph()
    
    async for event in graph.astream(
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
    ):
        yield event


# ─── Async LLM Calls ─────────────────────────────────────────────────────────

async def allm_call(
    prompt: str,
    task_type: str = "chat",
    **kwargs,
) -> str:
    """Async LLM-Call mit automatischer Task-Routing.
    
    >>> result = await allm_call("Erkläre Quantencomputing", task_type="research")
    >>> print(result)
    """
    llm = get_llm_for_task(task_type, **kwargs)
    response = await llm.ainvoke(prompt)
    return response.content


async def allm_stream(
    prompt: str,
    task_type: str = "chat",
    **kwargs,
) -> AsyncIterator[str]:
    """Async Streaming LLM-Call.
    
    async for chunk in allm_stream("Erzähle eine Geschichte"):
        print(chunk, end="", flush=True)
    """
    llm = get_llm_for_task(task_type, **kwargs)
    async for chunk in llm.astream(prompt):
        if hasattr(chunk, "content"):
            yield chunk.content


# ─── Async RAG ────────────────────────────────────────────────────────────────

async def arag_query(
    query: str,
    k: int = 5,
    collection: str = "nexifyai_brain",
) -> dict:
    """Async RAG Query.
    
    >>> result = await arag_query("Was ist die Provider-Strategie?")
    >>> print(result["answer"])
    """
    from rag_pipeline import create_qa_chain
    
    qa = create_qa_chain(collection_name=collection, k=k)
    result = await qa.ainvoke({"query": query})
    
    return {
        "answer": result.get("result", ""),
        "sources": [
            {
                "content": d.page_content[:300],
                "source": d.metadata.get("source", "unknown"),
            }
            for d in result.get("source_documents", [])
        ],
    }


# ─── Async Batch Processing ─────────────────────────────────────────────────

async def abatch_agents(tasks: list[str], thread_prefix: str = "batch") -> list[dict]:
    """Führe mehrere Agent-Tasks parallel aus.
    
    >>> results = await abatch_agents([
    ...     "Recherchiere Thema A",
    ...     "Analysiere Code B",
    ...     "Prüfe Health C",
    ... ])
    >>> for r in results:
    ...     print(r["output"][:100])
    """
    import asyncio
    
    async def run_single(idx: int, task: str) -> dict:
        result = await arun_agent(task, f"{thread_prefix}_{idx}")
        messages = result.get("messages", [])
        return {
            "index": idx,
            "task": task,
            "output": messages[-1].content if messages else "Keine Antwort",
            "agent": result.get("current_agent", "unknown"),
            "error": result.get("error"),
        }
    
    tasks_coros = [run_single(i, t) for i, t in enumerate(tasks)]
    results = await asyncio.gather(*tasks_coros, return_exceptions=True)
    
    return [
        r if not isinstance(r, Exception) else {"error": str(r), "task": tasks[i]}
        for i, r in enumerate(results)
    ]


# ─── Async Oracle ────────────────────────────────────────────────────────────

async def aoracle_run(
    task: str,
    context: Optional[dict] = None,
    thread_id: str = "oracle_default",
) -> dict:
    """Async Oracle Task Lifecycle.
    
    >>> result = await aoracle_run("System-Health prüfen")
    >>> print(f"Status: {result['status']}")
    """
    from oracle_workflow import run_oracle_task
    import asyncio
    
    # run_oracle_task ist synchron — wrapper für async-Aufruf
    result = await asyncio.to_thread(
        run_oracle_task,
        task=task,
        context=context,
        thread_id=thread_id,
    )
    
    return result


# ─── Async Planner ──────────────────────────────────────────────────────────

async def aplanner_cycle(
    objectives: list[str],
    cycle_number: int = 0,
    thread_id: str = "planner_default",
) -> dict:
    """Async Planning Cycle.
    
    >>> result = await aplanner_cycle(["Security-Check", "Feature X"])
    >>> print(result["execution_plan"][:200])
    """
    from planner_workflow import run_planning_cycle
    import asyncio
    
    result = await asyncio.to_thread(
        run_planning_cycle,
        objectives=objectives,
        cycle_number=cycle_number,
        thread_id=thread_id,
    )
    
    return result


# ─── Async Tool Calls ────────────────────────────────────────────────────────

async def atool_call(tool_name: str, **kwargs) -> str:
    """Führe ein Tool asynchron aus.
    
    >>> result = await atool_call("search_code", query="def main")
    """
    tools = get_all_tools()
    tool_map = {t.name: t for t in tools}
    
    if tool_name not in tool_map:
        return f"Tool '{tool_name}' nicht gefunden. Verfügbar: {list(tool_map.keys())}"
    
    tool = tool_map[tool_name]
    
    try:
        result = tool.func(**kwargs)
        if hasattr(result, "__await__"):
            return await result
        return str(result)
    except Exception as e:
        return f"Fehler bei {tool_name}: {str(e)}"
