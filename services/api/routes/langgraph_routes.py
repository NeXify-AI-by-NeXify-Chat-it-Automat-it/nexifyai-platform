"""
LangGraph API Routes — Enterprise Agent Endpoints
===================================================
Neue FastAPI-Endpoints für die LangChain/LangGraph-Integration.

Ersetzt/ergänzt: orchestator_routes.py (Custom), oracle_routes.py (Custom),
                 intelligence_routes.py (Custom)

Endpoints:
  POST /api/v2/agent/run       — Single-Task Agent
  POST /api/v2/agent/stream    — Streaming Agent
  POST /api/v2/oracle/run      — Oracle Task Lifecycle
  GET  /api/v2/oracle/{id}     — Oracle Task Status
  POST /api/v2/planner/cycle   — Planning Cycle
  GET  /api/v2/health/ai       — AI-Infrastructure Health
  POST /api/v2/rag/query       — RAG Query
  POST /api/v2/rag/conversation — Conversational RAG
"""
import os
import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# LangChain/LangGraph Services
from services.agent_system import run_agent, stream_agent, build_supervisor_graph
from services.oracle_workflow import run_oracle_task, get_oracle_status
from services.planner_workflow import run_planning_cycle, run_strategic_cycle
from services.governance import get_system_health, GovernanceCallback
from services.rag_pipeline import create_qa_chain, create_conversational_qa
from services.langchain_config import get_llm_for_task, create_llm_with_fallbacks
from services.tool_registry import get_all_tools, get_agent_tools

logger = logging.getLogger("nexifyai.routes.langgraph")

router = APIRouter(prefix="/api/v2", tags=["AI-Agents"])


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    task: str
    thread_id: str = "default"
    agent_type: Optional[str] = None  # developer, research, admin, oracle


class OracleRunRequest(BaseModel):
    task: str
    context: Optional[dict] = None
    task_id: Optional[str] = None
    thread_id: str = "oracle_default"


class PlannerCycleRequest(BaseModel):
    objectives: list[str]
    cycle_number: int = 0
    thread_id: str = "planner_default"


class RAGQueryRequest(BaseModel):
    query: str
    k: int = 5
    collection: str = "nexifyai_brain"


class RAGConversationRequest(BaseModel):
    question: str
    k: int = 5
    collection: str = "nexifyai_brain"


# ─── Agent Endpoints ──────────────────────────────────────────────────────────

@router.post("/agent/run", summary="Single-Task Agent ausführen")
async def agent_run(request: AgentRunRequest):
    """Führe einen einzelnen Task mit dem LangGraph Supervisor aus.
    
    Der Agent klassifiziert den Task automatisch (Code/Research/QA)
    und wählt die passenden Tools aus.
    
    Response:
        task: Ursprüngliche Aufgabe
        output: Agent-Antwort (letzte Message)
        agent: Verwendeter Agent-Typ
        intermediate_results: Detaillierte Ergebnisse aller Sub-Agents
    """
    logger.info(f"[Agent] Run: {request.task[:80]}...")
    
    try:
        result = run_agent(
            task=request.task,
            thread_id=request.thread_id,
        )
        
        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else "Keine Antwort"
        
        return {
            "success": True,
            "task": request.task,
            "output": last_message,
            "agent": result.get("current_agent", "unknown"),
            "intermediate_results": result.get("intermediate_results", {}),
        }
    except Exception as e:
        logger.error(f"[Agent] Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/stream", summary="Streaming Agent (SSE)")
async def agent_stream(request: AgentRunRequest):
    """Führe einen Agenten mit Streaming-Output aus.
    
    Verwendet Server-Sent Events für Echtzeit-Output.
    """
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        try:
            for event in stream_agent(request.task, request.thread_id):
                if isinstance(event, dict):
                    yield f"data: {json.dumps(event)}\n\n"
                else:
                    yield f"data: {str(event)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ─── Oracle Endpoints ─────────────────────────────────────────────────────────

@router.post("/oracle/run", summary="Oracle Task Lifecycle ausführen")
async def oracle_run(request: OracleRunRequest):
    """Führe einen kompletten Oracle Task-Lifecycle aus.
    
    Lifecycle: DISCOVERED → PLANNED → EXECUTING → VERIFIED → STORED → COMPLETED
    """
    logger.info(f"[Oracle] Run: {request.task[:80]}...")
    
    try:
        result = run_oracle_task(
            task=request.task,
            context=request.context,
            task_id=request.task_id,
            thread_id=request.thread_id,
        )
        
        return {
            "success": result.get("status") in ("completed", "stored", "learned"),
            "task_id": result.get("task_id"),
            "task": request.task,
            "status": result.get("status", "unknown"),
            "verification_score": result.get("verification_score"),
            "output": result.get("agent_result", "")[:2000],
            "error": result.get("error"),
        }
    except Exception as e:
        logger.error(f"[Oracle] Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oracle/{task_id}", summary="Oracle Task Status abrufen")
async def oracle_status(task_id: str):
    """Hole den aktuellen Status eines Oracle-Tasks."""
    result = get_oracle_status(task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} nicht gefunden")
    
    return {
        "task_id": task_id,
        "status": result.get("status", "unknown"),
        "verification_score": result.get("verification_score"),
        "error": result.get("error"),
        "completed_at": result.get("completed_at"),
    }


# ─── Planner Endpoints ────────────────────────────────────────────────────────

@router.post("/planner/cycle", summary="Planning Cycle ausführen")
async def planner_cycle(request: PlannerCycleRequest):
    """Führe einen kompletten Strategic Planning Cycle aus.
    
    Cycle: HEALTH_CHECK → PRIORITIZE → PLAN → ROUTE → EXECUTE → REVIEW
    """
    logger.info(f"[Planner] Cycle #{request.cycle_number} mit {len(request.objectives)} Objectives")
    
    try:
        result = run_planning_cycle(
            objectives=request.objectives,
            cycle_number=request.cycle_number,
            thread_id=request.thread_id,
        )
        
        return {
            "success": True,
            "cycle_number": request.cycle_number,
            "task_graph": result.get("task_graph", []),
            "routed_tasks": result.get("routed_tasks", []),
            "execution_plan": result.get("execution_plan", "")[:2000],
            "system_health": result.get("system_health"),
        }
    except Exception as e:
        logger.error(f"[Planner] Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── RAG Endpoints ────────────────────────────────────────────────────────────

@router.post("/rag/query", summary="RAG Query ausführen")
async def rag_query(request: RAGQueryRequest):
    """Führe eine RAG-Query mit Kontext aus der Wissensdatenbank aus.
    
    Verwendet: Qdrant Vector Store + HuggingFace Embeddings + Multi-Query Retriever
    """
    logger.info(f"[RAG] Query: {request.query[:80]}...")
    
    try:
        qa_chain = create_qa_chain(
            collection_name=request.collection,
            k=request.k,
        )
        
        result = qa_chain.invoke({"query": request.query})
        
        sources = []
        for doc in result.get("source_documents", []):
            sources.append({
                "content": doc.page_content[:300],
                "source": doc.metadata.get("source", "unknown"),
                "category": doc.metadata.get("category", "unknown"),
            })
        
        return {
            "success": True,
            "query": request.query,
            "answer": result.get("result", ""),
            "sources": sources[:5],
            "source_count": len(sources),
        }
    except Exception as e:
        logger.error(f"[RAG] Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/conversation", summary="Conversational RAG")
async def rag_conversation(request: RAGConversationRequest):
    """Conversational RAG mit Memory (merkt vorherige Fragen)."""
    try:
        qa = create_conversational_qa(
            collection_name=request.collection,
            k=request.k,
        )
        
        result = qa.invoke({"question": request.question})
        
        return {
            "success": True,
            "question": request.question,
            "answer": result.get("answer", ""),
        }
    except Exception as e:
        logger.error(f"[RAG Conversation] Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Health Endpoint ──────────────────────────────────────────────────────────

@router.get("/health/ai", summary="AI-Infrastructure Health")
async def ai_health():
    """Zeigt den Status aller AI-Komponenten.
    
    Prüft: LLM-Provider, Vector Store, Embeddings, Observability
    """
    return get_system_health()


# ─── Tools Endpoints ──────────────────────────────────────────────────────────

@router.get("/tools", summary="Verfügbare Tools auflisten")
async def list_tools():
    """Liste alle verfügbaren LangChain-Tools auf."""
    tools = get_all_tools()
    return {
        "count": len(tools),
        "tools": [
            {
                "name": t.name,
                "description": t.description.split(".")[0],
                "args": list(t.args.keys()) if hasattr(t, "args") else [],
            }
            for t in tools
        ],
    }


@router.get("/agent/tools/{agent_type}", summary="Agent-Tools auflisten")
async def agent_tools(agent_type: str = "default"):
    """Liste Tools für einen bestimmten Agent-Typ."""
    tools = get_agent_tools(agent_type)
    return {
        "agent_type": agent_type,
        "count": len(tools),
        "tools": [{"name": t.name, "description": t.description[:100]} for t in tools],
    }
