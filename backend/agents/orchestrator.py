"""
NeXifyAI Orchestrator — Central AI Agent Router.
Routes tasks to specialized sub-agents based on intent.
Maintains audit trail in timeline_events.
"""
import os
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage
from domain import create_timeline_event, utcnow, new_id, Channel

logger = logging.getLogger("nexifyai.orchestrator")

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.2"

def _get_key():
    return os.environ.get("EMERGENT_LLM_KEY", "")

AGENT_ROLES = {
    "intake": "Leadaufnahme, Discovery und Erstklassifikation",
    "research": "Lead-Recherche und Firmenanalyse",
    "outreach": "Personalisierte Erstansprache und Nachfass-Kommunikation",
    "offer": "Angebotserstellung und Tarifberatung",
    "planning": "Projektplanung, Architektur und Build-Handover",
    "finance": "Rechnungsstellung, Zahlungen und Mahnwesen",
    "support": "Kundenbetreuung und Problemlösung",
    "design": "Design-Konzeption, Content-Strategie und SEO",
    "qa": "Qualitätssicherung, Audit und Selbstheilung",
}

ORCHESTRATOR_SYSTEM = """Du bist der NeXifyAI Orchestrator — die zentrale KI-Instanz, die eingehende Aufgaben analysiert und an spezialisierte Sub-Agenten delegiert.

DEINE ROLLEN:
- Eingehende Anfragen klassifizieren (research, outreach, offer, finance, support, qa)
- Den richtigen Sub-Agenten auswählen
- Kontext und Memory übergeben
- Ergebnis prüfen und zurückgeben

VERFÜGBARE AGENTEN:
{agents}

ANTWORTFORMAT:
Du antwortest IMMER im JSON-Format:
{{"agent": "<agent_name>", "task": "<aufgabe>", "priority": "high|medium|low", "context_needed": ["memory", "quotes", "invoices", "conversations"]}}

Wenn die Aufgabe direkt ohne Sub-Agent lösbar ist, antworte:
{{"agent": "self", "response": "<direkte_antwort>", "actions": []}}
""".format(agents="\n".join(f"- {k}: {v}" for k, v in AGENT_ROLES.items()))


class Orchestrator:
    """Central orchestrator that routes tasks to sub-agents."""

    def __init__(self, db):
        self.db = db
        self._sessions = {}

    def _get_chat(self, session_id: str) -> LlmChat:
        if session_id not in self._sessions:
            chat = LlmChat(
                api_key=_get_key(),
                session_id=f"orch_{session_id}",
                system_message=ORCHESTRATOR_SYSTEM,
            )
            chat.with_model(MODEL_PROVIDER, MODEL_NAME)
            self._sessions[session_id] = chat
        return self._sessions[session_id]

    async def route(self, task: str, context: dict = None, session_id: str = None) -> dict:
        """Route a task to the appropriate sub-agent."""
        sid = session_id or new_id("orch")
        chat = self._get_chat(sid)

        prompt = f"AUFGABE: {task}"
        if context:
            prompt += f"\n\nKONTEXT: {str(context)[:2000]}"

        try:
            response = await chat.send_message(UserMessage(text=prompt))
            import json
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {"agent": "self", "response": response, "raw": True}

            # Audit
            evt = create_timeline_event(
                "orchestrator", sid, "task_routed",
                actor="orchestrator", actor_type="ai",
                details={"task": task[:200], "routed_to": result.get("agent", "unknown")}
            )
            await self.db.timeline_events.insert_one(evt)

            return {
                "session_id": sid,
                "routing": result,
                "timestamp": str(utcnow()),
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {"session_id": sid, "error": str(e), "timestamp": str(utcnow())}


class SubAgent:
    """Base class for specialized sub-agents."""

    def __init__(self, name: str, system_prompt: str, db):
        self.name = name
        self.db = db
        self.system_prompt = system_prompt
        self._sessions = {}

    def _get_chat(self, session_id: str) -> LlmChat:
        if session_id not in self._sessions:
            chat = LlmChat(
                api_key=_get_key(),
                session_id=f"{self.name}_{session_id}",
                system_message=self.system_prompt,
            )
            chat.with_model(MODEL_PROVIDER, MODEL_NAME)
            self._sessions[session_id] = chat
        return self._sessions[session_id]

    async def execute(self, task: str, context: str = "", session_id: str = None) -> dict:
        sid = session_id or new_id(self.name[:4])
        chat = self._get_chat(sid)
        prompt = task
        if context:
            prompt = f"KONTEXT:\n{context}\n\nAUFGABE:\n{task}"
        try:
            response = await chat.send_message(UserMessage(text=prompt))
            evt = create_timeline_event(
                "agent", sid, f"{self.name}_executed",
                actor=self.name, actor_type="ai",
                details={"task": task[:200], "response_preview": response[:200]}
            )
            await self.db.timeline_events.insert_one(evt)
            return {"agent": self.name, "session_id": sid, "response": response, "timestamp": str(utcnow())}
        except Exception as e:
            logger.error(f"SubAgent {self.name} error: {e}")
            return {"agent": self.name, "session_id": sid, "error": str(e), "timestamp": str(utcnow())}
