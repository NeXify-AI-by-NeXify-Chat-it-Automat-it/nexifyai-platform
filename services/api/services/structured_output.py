"""
LangChain Structured Output — Enterprise Pydantic-Schemas
==========================================================
Erweiterung für agent_system.py, oracle_workflow.py, planner_workflow.py.

Bietet typisierte, validierte Output-Schemas für alle Agents.
LangChain's with_structured_output() wandelt LLM-Responses automatisch
in Pydantic-Modelle um — kein manuelles JSON-Parsing mehr.
"""
import json
import logging
from typing import Optional, Literal
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger("nexifyai.structured_output")


# ═══════════════════════════════════════════════════════════════════
# Agent Output Schemas
# ═══════════════════════════════════════════════════════════════════

class AgentAnalysis(BaseModel):
    """Strukturierte Analyse eines Agent-Tasks."""
    task_type: Literal["code", "research", "qa", "plan", "deploy", "chat"] = Field(
        description="Klassifizierter Task-Typ"
    )
    summary: str = Field(
        description="Kurze Zusammenfassung der Aufgabe (max 2 Sätze)"
    )
    required_tools: list[str] = Field(
        description="Benötigte Tools zur Lösung",
        default_factory=list,
    )
    complexity: Literal["low", "medium", "high"] = Field(
        description="Geschätzte Komplexität",
        default="medium",
    )
    estimated_steps: int = Field(
        description="Geschätzte Anzahl Lösungsschritte",
        ge=1, le=20,
        default=3,
    )


class AgentResult(BaseModel):
    """Strukturiertes Ergebnis eines Agent-Durchlaufs."""
    success: bool = Field(description="War die Ausführung erfolgreich?")
    answer: str = Field(description="Die finale Antwort")
    confidence: float = Field(
        description="Konfidenz-Score (0.0 - 1.0)",
        ge=0.0, le=1.0,
        default=0.8,
    )
    sources: list[str] = Field(
        description="Verwendete Quellen/Tools",
        default_factory=list,
    )
    warnings: list[str] = Field(
        description="Warnungen oder Einschränkungen",
        default_factory=list,
    )
    suggested_followup: Optional[str] = Field(
        description="Empfohlene nächste Frage/Aktion",
        default=None,
    )


# ═══════════════════════════════════════════════════════════════════
# Oracle Output Schemas
# ═══════════════════════════════════════════════════════════════════

class OraclePlan(BaseModel):
    """Strukturierter Oracle-Ausführungsplan."""
    analysis: str = Field(description="Detaillierte Aufgabenanalyse")
    steps: list[dict] = Field(
        description="Ausführungsschritte mit tool und input",
        default_factory=list,
    )
    required_knowledge: list[str] = Field(
        description="Benötigte Wissensquellen",
        default_factory=list,
    )
    risk_assessment: Literal["low", "medium", "high"] = Field(
        description="Risikobewertung",
        default="low",
    )


class OracleVerification(BaseModel):
    """Strukturierte Verifikation eines Oracle-Ergebnisses."""
    passed: bool = Field(description="Hat die Verifikation bestanden?")
    score: float = Field(
        description="Qualitäts-Score (0.0 - 10.0)",
        ge=0.0, le=10.0,
    )
    strengths: list[str] = Field(
        description="Stärken des Ergebnisses",
        default_factory=list,
    )
    improvements: list[str] = Field(
        description="Verbesserungsvorschläge",
        default_factory=list,
    )
    critical_issues: list[str] = Field(
        description="Kritische Probleme (leer wenn keine)",
        default_factory=list,
    )


# ═══════════════════════════════════════════════════════════════════
# Planner Output Schemas
# ═══════════════════════════════════════════════════════════════════

class PrioritizedTask(BaseModel):
    """Ein priorisierter Task im Planner."""
    id: str = Field(description="Eindeutige Task-ID (z.B. T-1)")
    title: str = Field(description="Kurzer, präziser Task-Titel")
    description: str = Field(description="Detaillierte Task-Beschreibung")
    priority: Literal["P0", "P1", "P2", "P3"] = Field(
        description="Priorität: P0 (kritisch) bis P3 (nice-to-have)"
    )
    reasoning: str = Field(description="Begründung der Priorisierung")
    team: Literal["security", "infrastructure", "backend", "frontend", "ai", "research"] = Field(
        description="Zuständiges Team"
    )
    depends_on: list[str] = Field(
        description="Task-IDs von Abhängigkeiten",
        default_factory=list,
    )
    estimated_effort: Literal["XS", "S", "M", "L", "XL"] = Field(
        description="Geschätzter Aufwand",
        default="M",
    )


class PlanningCycleOutput(BaseModel):
    """Strukturiertes Ergebnis eines Planning-Cycles."""
    cycle_number: int = Field(description="Cycle-Nummer")
    health_status: str = Field(description="System-Health Status")
    total_tasks: int = Field(description="Anzahl priorisierter Tasks")
    prioritized_tasks: list[PrioritizedTask] = Field(
        description="Priorisierte Tasks",
        default_factory=list,
    )
    critical_count: int = Field(
        description="Anzahl P0 (kritischer) Tasks",
        default=0,
    )
    execution_plan: str = Field(
        description="Zusammenfassung des Ausführungsplans",
        default="",
    )


# ═══════════════════════════════════════════════════════════════════
# RAG Output Schemas
# ═══════════════════════════════════════════════════════════════════

class RAGSource(BaseModel):
    """Eine Quelle aus der RAG-Suche."""
    content: str = Field(description="Text-Auszug")
    source: str = Field(description="Quellen-Pfad/URL")
    category: str = Field(description="Dokumenten-Kategorie", default="unknown")
    relevance_score: Optional[float] = Field(
        description="Relevanz-Score",
        default=None,
    )


class RAGResponse(BaseModel):
    """Strukturierte RAG-Antwort."""
    answer: str = Field(description="Die finale Antwort mit Quellenbezügen")
    sources: list[RAGSource] = Field(
        description="Verwendete Quellen",
        default_factory=list,
    )
    confidence: float = Field(
        description="Konfidenz (0.0 - 1.0)",
        ge=0.0, le=1.0,
        default=0.7,
    )
    needs_update: bool = Field(
        description="Wissensbasis sollte aktualisiert werden?",
        default=False,
    )


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════

def get_output_parser(model_class: type[BaseModel]) -> PydanticOutputParser:
    """Erstelle einen PydanticOutputParser für ein Schema.
    
    >>> parser = get_output_parser(AgentResult)
    >>> formatted = parser.get_format_instructions()
    """
    return PydanticOutputParser(pydantic_object=model_class)


def format_structured_prompt(
    model_class: type[BaseModel],
    system_prompt: str,
) -> str:
    """Erweitere einen System-Prompt mit JSON-Output-Formatierung.
    
    >>> prompt = format_structured_prompt(
    ...     AgentResult,
    ...     "Du bist ein hilfreicher Assistent."
    ... )
    """
    parser = get_output_parser(model_class)
    return f"""{system_prompt}

WICHTIG: Deine Antwort MUSS als gültiges JSON-Objekt gemäß folgendem Schema formatiert werden:

{parser.get_format_instructions()}

Antworte NUR mit dem JSON-Objekt. Keine zusätzliche Formatierung, kein Markdown, kein Code-Block."""


def safe_parse(model_class: type[BaseModel], content: str) -> Optional[BaseModel]:
    """Versuche, Content in Pydantic-Modell zu parsen.
    
    Extrahiert JSON aus Code-Blöcken oder rohem Text,
    mit Graceful Degradation bei Fehlern.
    
    >>> result = safe_parse(AgentResult, '{"success": true, "answer": "42"}')
    >>> if result: print(result.answer)
    """
    import re
    
    # 1. Versuche: Inhalt ist direkt JSON
    try:
        return model_class.model_validate_json(content)
    except Exception:
        pass
    
    # 2. Versuche: JSON aus Code-Block extrahieren
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
    if json_match:
        try:
            return model_class.model_validate_json(json_match.group(1))
        except Exception:
            pass
    
    # 3. Versuche: JSON-Objekt aus Text extrahieren
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            return model_class.model_validate_json(json_match.group(0))
        except Exception:
            pass
    
    logger.warning(f"Konnte {model_class.__name__} nicht parsen aus: {content[:100]}...")
    return None


def extract_json_array(text: str) -> Optional[list]:
    """Extrahiere ein JSON-Array aus Text (mit Graceful Degradation).
    
    >>> extract_json_array('[{"a": 1}, {"b": 2}]')
    [{'a': 1}, {'b': 2}]
    """
    import re
    
    json_match = re.search(r'\[.*?\]', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None
