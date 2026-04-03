"""
NeXifyAI — mem0 Memory Service (Pflicht-Layer)
Zentraler Memory-Dienst mit agent_id Scoping.
Jeder Agent MUSS vor Arbeit lesen und nach jeder relevanten Änderung schreiben.

Pflicht-Scoping pro Eintrag:
  - user_id (Kontakt/Kunden-ID)
  - agent_id (z.B. emergent_build_agent, intake_agent, finance_agent)
  - app_id (nexifyai)
  - run_id (eindeutige Ausführungs-ID)
"""

from datetime import datetime, timezone
from domain import create_memory, new_id, utcnow

APP_ID = "nexifyai"

# Agent-IDs nach Dokumentation
AGENT_IDS = {
    "emergent_build": "emergent_build_agent",
    "intake": "intake_agent",
    "research": "research_agent",
    "outreach": "outreach_agent",
    "offer": "offer_agent",
    "planning": "planning_agent",
    "finance": "finance_agent",
    "support": "support_agent",
    "design": "design_agent",
    "qa": "qa_agent",
    "admin": "admin_agent",
    "system": "system_agent",
    "chat": "chat_agent",
}


class MemoryService:
    """Zentraler mem0 Memory-Dienst — Pflicht für alle Agenten."""

    def __init__(self, db):
        self.db = db
        self.collection = db.customer_memory

    async def read(self, contact_id: str, agent_id: str = None, category: str = None, limit: int = 20) -> list:
        """Pflicht-Read: Kontext vor Arbeit laden."""
        query = {"contact_id": contact_id}
        if agent_id:
            query["agent_id"] = agent_id
        if category:
            query["category"] = category
        facts = []
        async for mem in self.collection.find(query, {"_id": 0}).sort("created_at", -1).limit(limit):
            facts.append(mem)
        return facts

    async def read_all_for_context(self, contact_id: str, limit: int = 30) -> str:
        """Alle Memory-Einträge als Kontext-String für Agenten aufbereiten."""
        facts = await self.read(contact_id, limit=limit)
        if not facts:
            return ""
        lines = []
        for f in facts:
            agent = f.get("agent_id", "?")
            cat = f.get("category", "general")
            verified = f.get("verification_status", "nicht verifiziert")
            lines.append(f"[{agent}/{cat}/{verified}] {f.get('fact', '')}")
        return "\n".join(lines)

    async def write(self, contact_id: str, fact: str, agent_id: str, 
                    category: str = "general", source: str = "agent",
                    source_ref: str = "", confidence: float = 0.8,
                    verification_status: str = "nicht verifiziert",
                    run_id: str = None) -> dict:
        """Pflicht-Write: Nach jeder relevanten Änderung Memory schreiben."""
        mem = create_memory(
            contact_id, fact,
            user_id=contact_id,
            agent_id=agent_id,
            app_id=APP_ID,
            run_id=run_id or new_id("run"),
            category=category,
            source=source,
            source_ref=source_ref,
            confidence=confidence,
            verification_status=verification_status,
        )
        await self.collection.insert_one(mem)
        mem.pop("_id", None)
        return mem

    async def write_verified(self, contact_id: str, fact: str, agent_id: str,
                              category: str = "general", source: str = "agent",
                              source_ref: str = "", run_id: str = None) -> dict:
        """Verifizierter Memory-Eintrag."""
        return await self.write(
            contact_id, fact, agent_id, category, source, source_ref,
            confidence=1.0, verification_status="verifiziert", run_id=run_id,
        )

    async def search(self, query_text: str, contact_id: str = None, limit: int = 10) -> list:
        """Einfache Text-Suche in Memory-Fakten."""
        match = {"fact": {"$regex": query_text, "$options": "i"}}
        if contact_id:
            match["contact_id"] = contact_id
        results = []
        async for mem in self.collection.find(match, {"_id": 0}).sort("created_at", -1).limit(limit):
            results.append(mem)
        return results

    async def get_agent_history(self, agent_id: str, limit: int = 20) -> list:
        """Alle Memory-Einträge eines bestimmten Agenten."""
        results = []
        async for mem in self.collection.find({"agent_id": agent_id}, {"_id": 0}).sort("created_at", -1).limit(limit):
            results.append(mem)
        return results
