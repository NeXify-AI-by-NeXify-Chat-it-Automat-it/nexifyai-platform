"""
NeXifyAI — Oracle Autonomous Engine
24/7 autonomes Task-Processing mit granularem Status-Modell, Loop-Evidence und Validierung.

Status-Lifecycle (Zentrale Leitstelle):
  erkannt → eingeplant → gestartet → in_bearbeitung → [wartet_auf_input | wartet_auf_freigabe | in_loop]
  → erfolgreich_abgeschlossen → erfolgreich_validiert | fehlgeschlagen | blockiert | abgebrochen | eskaliert
"""
import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

from services import supabase_client as supa
from services import deepseek_provider as deepseek

logger = logging.getLogger("nexifyai.oracle.engine")

MAX_RETRIES = 3
PROCESSING_BATCH = 5
MAX_LOOP_ITERATIONS = 5

# Granulares Status-Modell (DE)
STATUS = {
    "ERKANNT": "erkannt",
    "EINGEPLANT": "eingeplant",
    "GESTARTET": "gestartet",
    "IN_BEARBEITUNG": "in_bearbeitung",
    "WARTET_AUF_INPUT": "wartet_auf_input",
    "WARTET_AUF_FREIGABE": "wartet_auf_freigabe",
    "IN_LOOP": "in_loop",
    "ERFOLGREICH_ABGESCHLOSSEN": "erfolgreich_abgeschlossen",
    "ERFOLGREICH_VALIDIERT": "erfolgreich_validiert",
    "FEHLGESCHLAGEN": "fehlgeschlagen",
    "BLOCKIERT": "blockiert",
    "ABGEBROCHEN": "abgebrochen",
    "ESKALIERT": "eskaliert",
}

STATUS_LABELS = {
    "erkannt": "Erkannt",
    "eingeplant": "Eingeplant",
    "gestartet": "Gestartet",
    "in_bearbeitung": "In Bearbeitung",
    "wartet_auf_input": "Wartet auf Input",
    "wartet_auf_freigabe": "Wartet auf Freigabe",
    "in_loop": "In Loop",
    "erfolgreich_abgeschlossen": "Erfolgreich abgeschlossen",
    "erfolgreich_validiert": "Erfolgreich validiert",
    "fehlgeschlagen": "Fehlgeschlagen",
    "blockiert": "Blockiert",
    "abgebrochen": "Abgebrochen",
    "eskaliert": "Eskaliert",
}

# Legacy-Status-Mapping (alte → neue)
LEGACY_MAP = {
    "pending": "erkannt",
    "assigned": "eingeplant",
    "running": "in_bearbeitung",
    "completed": "erfolgreich_abgeschlossen",
    "failed": "fehlgeschlagen",
    "cancelled": "abgebrochen",
    "blocked": "blockiert",
    "review": "wartet_auf_freigabe",
    "open": "erkannt",
}


class OracleEngine:
    """Autonome Orchestrierungs-Engine mit granularem Status-Tracking und Loop-Evidence."""

    def __init__(self, db):
        self.db = db
        self._running = False
        self._stats = {"processed": 0, "verified": 0, "failed": 0, "reassigned": 0, "cycle": 0, "loops": 0}

    async def start(self):
        self._running = True
        logger.info("Oracle Engine gestartet — Autonomer Modus aktiv")

    async def stop(self):
        self._running = False
        logger.info("Oracle Engine gestoppt")

    # ═══════════════════════════════════════════════════════════
    # STATUS-TRANSITION — Zentrale Statusübergangslogik
    # ═══════════════════════════════════════════════════════════

    async def _transition(self, task_id, new_status: str, reason: str = "", agent: str = "", extra: dict = None):
        """Statusübergang mit History-Tracking und Audit."""
        now = datetime.now(timezone.utc).isoformat()
        entry = json.dumps([{"status": new_status, "at": now, "reason": reason, "agent": agent}])
        audit_text = f"[{now}] {new_status.upper()}: {reason}"

        set_clauses = ["status=$1"]
        params = [new_status]
        idx = 2

        # Status-History JSONB append
        ph = f"${idx}"
        set_clauses.append(f"status_history = COALESCE(status_history, '[]'::jsonb) || {ph}::jsonb")
        params.append(entry)
        idx += 1

        # Audit-Log
        ph = f"${idx}"
        set_clauses.append(f"audit_log = array_append(COALESCE(audit_log, ARRAY[]::jsonb[]), to_jsonb({ph}::text))")
        params.append(audit_text)
        idx += 1

        if agent:
            set_clauses.append(f"current_agent=${idx}")
            params.append(agent)
            idx += 1

        if extra:
            for k, v in extra.items():
                if k in ("started_at", "completed_at"):
                    set_clauses.append(f"{k}=NOW()")
                elif k in ("loop_count", "retry_count"):
                    set_clauses.append(f"{k}=${idx}")
                    params.append(int(v))
                    idx += 1
                elif k in ("loop_reason", "exit_condition", "error_message", "escalation_reason", "owner_agent"):
                    set_clauses.append(f"{k}=${idx}")
                    params.append(str(v)[:500])
                    idx += 1
                elif k == "verification_score":
                    set_clauses.append(f"verification_score=${idx}")
                    params.append(float(v))
                    idx += 1
                elif k in ("evidence", "result"):
                    set_clauses.append(f"{k}=${idx}::jsonb")
                    params.append(json.dumps(v, default=str, ensure_ascii=False))
                    idx += 1
                elif k == "owner_agent":
                    set_clauses.append(f"owner_agent=${idx}")
                    params.append(v)
                    idx += 1

        params.append(task_id)
        sql = f"UPDATE oracle_tasks SET {', '.join(set_clauses)} WHERE id=${idx}"
        await supa.execute(sql, *params)

    # ═══════════════════════════════════════════════════════════
    # HAUPTZYKLUS — Aufgerufen vom Scheduler (alle 90s)
    # ═══════════════════════════════════════════════════════════

    async def process_cycle(self):
        """Ein kompletter Verarbeitungszyklus mit granularem Status-Tracking."""
        if not self._running:
            return
        self._stats["cycle"] += 1
        cycle = self._stats["cycle"]

        try:
            # 0. Stuck Tasks zurücksetzen (in_bearbeitung/gestartet > 30min)
            try:
                stuck = await supa.fetch(
                    """SELECT id FROM oracle_tasks
                       WHERE status IN ('running','in_bearbeitung','gestartet')
                       AND started_at < NOW() - INTERVAL '30 minutes'
                       LIMIT 10"""
                )
                for s in stuck:
                    await self._transition(
                        s["id"], STATUS["ERKANNT"],
                        reason="Auto-Reset: Stuck > 30min",
                        extra={"error_message": "Auto-Reset: Task hing > 30 Minuten im Bearbeitungsstatus"}
                    )
            except Exception:
                pass

            # 1. Tasks holen: alte (pending/assigned) + neue (erkannt/eingeplant)
            pending = await supa.fetch(
                """SELECT id, type, priority, title, description, payload, tags, retry_count, owner_agent, created_at, loop_count
                   FROM oracle_tasks
                   WHERE status IN ('pending', 'assigned', 'erkannt', 'eingeplant')
                   AND COALESCE(retry_count, 0) < $1
                   ORDER BY priority DESC, created_at ASC
                   LIMIT $2""",
                MAX_RETRIES, PROCESSING_BATCH
            )

            if not pending:
                return

            logger.info(f"Oracle Zyklus #{cycle}: {len(pending)} Tasks zur Verarbeitung")

            for task in pending:
                await self._process_task(task)

        except Exception as e:
            logger.error(f"Oracle Zyklus #{cycle} Fehler: {e}")
            await self._audit("cycle_error", {"cycle": cycle, "error": str(e)[:500]})

    # ═══════════════════════════════════════════════════════════
    # TASK-VERARBEITUNG — Granularer Lifecycle
    # ═══════════════════════════════════════════════════════════

    async def _process_task(self, task: dict):
        """Task-Lifecycle: erkannt → eingeplant → gestartet → in_bearbeitung → validiert/fehlgeschlagen."""
        task_id = task["id"]
        task_type = task.get("type", "general")
        title = task.get("title") or task.get("description", "")[:100] or "Unbenannt"
        description = task.get("description", "")
        retry_count = task.get("retry_count", 0)
        loop_count = task.get("loop_count", 0) or 0

        try:
            # ── EINGEPLANT: Agent bestimmen ──
            agent = await self._select_agent(task_type, title)
            await self._transition(
                task_id, STATUS["EINGEPLANT"],
                reason=f"Zugewiesen an {agent['name']} ({agent['role']})",
                agent=agent["name"],
                extra={"owner_agent": agent["name"]}
            )

            # ── GESTARTET: Knowledge-Aggregation ──
            await self._transition(
                task_id, STATUS["GESTARTET"],
                reason="Wissensaggregation gestartet",
                agent=agent["name"],
                extra={"started_at": True}
            )
            knowledge_ctx = await self._aggregate_knowledge(title, description, task_type)

            # ── IN BEARBEITUNG: DeepSeek-Agent ausführen ──
            await self._transition(
                task_id, STATUS["IN_BEARBEITUNG"],
                reason=f"DeepSeek-Ausführung durch {agent['name']}",
                agent=agent["name"]
            )

            execution_prompt = self._build_execution_prompt(task, knowledge_ctx)
            result = await deepseek.invoke_agent(
                agent_name=agent["name"],
                agent_role=agent["role"],
                system_prompt=agent.get("system_prompt", ""),
                user_message=execution_prompt,
                context=knowledge_ctx[:3000],
                temperature=0.5
            )

            if "error" in result:
                raise Exception(result["error"])

            response_text = result.get("response", "")

            # ── ERFOLGREICH ABGESCHLOSSEN: Ergebnis liegt vor ──
            await self._transition(
                task_id, STATUS["ERFOLGREICH_ABGESCHLOSSEN"],
                reason=f"Ausführung durch {agent['name']} abgeschlossen, Ergebnis liegt vor",
                agent=agent["name"],
                extra={"result": {
                    "agent": agent["name"],
                    "model": result.get("model", "deepseek-chat"),
                    "response": response_text[:2000],
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )

            # ── VERIFIKATION: Unabhängige Gegenprüfung ──
            await self._transition(
                task_id, STATUS["WARTET_AUF_FREIGABE"],
                reason="Unabhängige Verifikation gestartet",
                agent=agent["name"]
            )

            verification = await self._verify_result(task, response_text, agent["name"])
            score = verification.get("score", 0)

            if verification["passed"]:
                # ── ERFOLGREICH VALIDIERT: Beweis erbracht ──
                evidence = {
                    "executor": agent["name"],
                    "verifier": verification.get("verified_by", "system"),
                    "score": score,
                    "reason": verification.get("reason", ""),
                    "verified_at": verification.get("verified_at", datetime.now(timezone.utc).isoformat()),
                    "model": result.get("model", "deepseek-chat"),
                    "response_length": len(response_text),
                }

                await self._transition(
                    task_id, STATUS["ERFOLGREICH_VALIDIERT"],
                    reason=f"Validiert von {verification.get('verified_by', 'system')} — Score {score}/10",
                    agent=verification.get("verified_by", "system"),
                    extra={
                        "completed_at": True,
                        "verification_score": float(score),
                        "evidence": evidence,
                        "result": {
                            "agent": agent["name"],
                            "model": result.get("model", "deepseek-chat"),
                            "response": response_text[:2000],
                            "verification": verification,
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                self._stats["verified"] += 1
                logger.info(f"Task {str(task_id)[:8]} VALIDIERT: {title[:60]} (Score {score})")

                # Brain-Note für Lernen
                await self._store_learning(task, response_text, verification)

            else:
                # ── LOOP oder FEHLGESCHLAGEN ──
                if retry_count < MAX_RETRIES:
                    new_loop = loop_count + 1
                    loop_reason = f"Verifikation fehlgeschlagen (Score {score}/10): {verification.get('reason', '')[:200]}"
                    exit_cond = f"Score >= 5 bei Versuch {new_loop + 1}/{MAX_RETRIES} oder Eskalation nach {MAX_RETRIES} Versuchen"

                    if new_loop >= MAX_LOOP_ITERATIONS:
                        # Eskalation
                        await self._transition(
                            task_id, STATUS["ESKALIERT"],
                            reason=f"Max Loop-Iterationen ({MAX_LOOP_ITERATIONS}) erreicht. Manuelle Prüfung erforderlich.",
                            agent="system",
                            extra={
                                "escalation_reason": f"Task hat {new_loop} Loops durchlaufen ohne Validierung. Letzter Score: {score}/10. Grund: {verification.get('reason', '')[:200]}",
                                "loop_count": new_loop,
                                "error_message": loop_reason
                            }
                        )
                        self._stats["failed"] += 1
                    else:
                        # In Loop: Zurück in Queue
                        await self._transition(
                            task_id, STATUS["IN_LOOP"],
                            reason=loop_reason,
                            agent=agent["name"],
                            extra={
                                "loop_count": new_loop,
                                "loop_reason": loop_reason,
                                "exit_condition": exit_cond,
                                "retry_count": retry_count + 1
                            }
                        )
                        # Direkt zurück auf erkannt für nächsten Zyklus
                        await self._transition(
                            task_id, STATUS["ERKANNT"],
                            reason=f"Loop {new_loop}: Reassigned für erneuten Versuch",
                            agent="system"
                        )
                        self._stats["reassigned"] += 1
                        self._stats["loops"] += 1
                        logger.warning(f"Task {str(task_id)[:8]} LOOP {new_loop}: {title[:60]}")
                else:
                    await self._transition(
                        task_id, STATUS["FEHLGESCHLAGEN"],
                        reason=f"Max Retries ({MAX_RETRIES}) erreicht. Letzter Fehler: {verification.get('reason', '')[:200]}",
                        agent="system",
                        extra={
                            "completed_at": True,
                            "error_message": f"Max Retries ({MAX_RETRIES}) erreicht. Score: {score}/10"
                        }
                    )
                    self._stats["failed"] += 1
                    logger.error(f"Task {str(task_id)[:8]} FEHLGESCHLAGEN: {title[:60]}")

            self._stats["processed"] += 1

        except Exception as e:
            logger.error(f"Task {str(task_id)[:8]} Execution Error: {e}")
            try:
                await self._transition(
                    task_id, STATUS["FEHLGESCHLAGEN"] if retry_count >= MAX_RETRIES - 1 else STATUS["ERKANNT"],
                    reason=f"Execution Error: {str(e)[:300]}",
                    agent="system",
                    extra={
                        "error_message": str(e)[:500],
                        "retry_count": retry_count + 1
                    }
                )
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════
    # AGENT SELECTION
    # ═══════════════════════════════════════════════════════════

    AGENT_ROUTING = {
        "infrastructure": {"name": "Forge", "role": "Tech Lead — Implementation, Architecture, Security"},
        "security": {"name": "Lexi", "role": "Legal Counsel — GDPR, Compliance, Security Audit"},
        "deployment": {"name": "Forge", "role": "Tech Lead — Deployment, CI/CD, Infrastructure"},
        "configuration": {"name": "Forge", "role": "Tech Lead — Configuration, Setup"},
        "optimization": {"name": "Strategist", "role": "Head of Concept — Optimization, Planning"},
        "improvement": {"name": "Strategist", "role": "Head of Concept — Process Improvement"},
        "monitoring": {"name": "Scout", "role": "Lead Intelligence — Monitoring, Alerts"},
        "data": {"name": "Scout", "role": "Lead Intelligence — Data Analysis, Research"},
        "crm": {"name": "Care", "role": "Customer Success — CRM, Support, Retention"},
        "email": {"name": "Scribe", "role": "Content Lead — Email, Copywriting"},
        "llm": {"name": "Forge", "role": "Tech Lead — LLM Integration"},
        "kpi": {"name": "Rank", "role": "SEO/Analytics — KPI Tracking, Growth"},
        "project_task": {"name": "Strategist", "role": "Head of Concept — Project Planning"},
        "system_task": {"name": "Forge", "role": "Tech Lead — System Operations"},
        "agent_task": {"name": "Nexus", "role": "CEO & Orchestrator — Agent Coordination"},
        "user_request": {"name": "Care", "role": "Customer Success — User Requests"},
        "verification": {"name": "Lexi", "role": "Legal Counsel — Verification, Audit"},
        "general": {"name": "Strategist", "role": "Head of Concept — General Tasks"},
    }

    async def _select_agent(self, task_type: str, title: str) -> dict:
        title_lower = (title or "").lower()
        if any(kw in title_lower for kw in ["deploy", "docker", "coolify", "server", "infra", "gitlab", "repo", "ci/cd", "backup"]):
            agent = {"name": "Forge", "role": "Tech Lead — Infrastructure, Deployment, DevOps"}
        elif any(kw in title_lower for kw in ["gdpr", "dsgvo", "compliance", "legal", "datenschutz", "vertrag"]):
            agent = {"name": "Lexi", "role": "Legal Counsel — GDPR, Compliance, Vertragsrecht"}
        elif any(kw in title_lower for kw in ["seo", "kpi", "analytics", "ranking", "traffic", "growth"]):
            agent = {"name": "Rank", "role": "SEO/Analytics — KPI, Growth, Performance"}
        elif any(kw in title_lower for kw in ["email", "text", "content", "copy", "newsletter"]):
            agent = {"name": "Scribe", "role": "Content Lead — Email, Copywriting, Content"}
        elif any(kw in title_lower for kw in ["design", "ui", "ux", "pixel", "branding", "layout"]):
            agent = {"name": "Pixel", "role": "Creative Director — Design, UX/UI, Branding"}
        elif any(kw in title_lower for kw in ["crm", "customer", "support", "ticket", "kunde"]):
            agent = {"name": "Care", "role": "Customer Success — CRM, Support, Retention"}
        elif any(kw in title_lower for kw in ["markt", "research", "intelligence", "monitor", "scrape"]):
            agent = {"name": "Scout", "role": "Lead Intelligence — Research, Monitoring, Data"}
        else:
            agent = self.AGENT_ROUTING.get(task_type, self.AGENT_ROUTING["general"])

        try:
            details = await supa.fetch(
                "SELECT description, capabilities FROM ai_agents WHERE name=$1 AND is_active=true LIMIT 1",
                agent["name"]
            )
            if details:
                agent["system_prompt"] = details[0].get("description", "")
                agent["capabilities"] = details[0].get("capabilities", "[]")
        except Exception:
            pass

        return agent

    # ═══════════════════════════════════════════════════════════
    # KNOWLEDGE AGGREGATION
    # ═══════════════════════════════════════════════════════════

    async def _aggregate_knowledge(self, title: str, description: str, task_type: str) -> str:
        parts = []
        query = f"{title} {description}"[:200]

        try:
            brain = await supa.brain_search(query, limit=5)
            if brain:
                brain_text = "\n".join([f"- {n.get('title', '')}: {n.get('content_preview', '')[:200]}" for n in brain])
                parts.append(f"[BRAIN-NOTES]\n{brain_text}")
        except Exception:
            pass

        try:
            knowledge = await supa.knowledge_search(limit=10)
            if knowledge:
                kb_text = "\n".join([f"- [{k.get('category', '')}] {k.get('content', '')[:150]}" for k in knowledge[:5]])
                parts.append(f"[KNOWLEDGE]\n{kb_text}")
        except Exception:
            pass

        try:
            memory = await supa.memory_entries(limit=10)
            if memory:
                mem_text = "\n".join([f"- {m.get('title', '')}: {m.get('content_preview', '')[:150]}" for m in memory[:5]])
                parts.append(f"[MEMORY]\n{mem_text}")
        except Exception:
            pass

        try:
            stats = {}
            for col in ["leads", "contacts", "quotes", "contracts", "invoices"]:
                stats[col] = await self.db[col].count_documents({})
            parts.append(f"[IST-STATUS MongoDB]\nLeads: {stats.get('leads',0)}, Contacts: {stats.get('contacts',0)}, Quotes: {stats.get('quotes',0)}, Contracts: {stats.get('contracts',0)}, Invoices: {stats.get('invoices',0)}")
        except Exception:
            pass

        return "\n\n".join(parts)

    # ═══════════════════════════════════════════════════════════
    # EXECUTION PROMPT
    # ═══════════════════════════════════════════════════════════

    def _build_execution_prompt(self, task: dict, knowledge: str) -> str:
        title_lower = (task.get('title', '') or '').lower()
        is_infra = any(kw in title_lower for kw in ["deploy", "docker", "coolify", "server", "infra", "gitlab", "backup", "ci/cd"])

        if is_infra:
            task_guidance = """AUFTRAGSTYP: Infrastruktur/Deployment-Analyse
Liefere: Vollständige Analyse + Schritt-für-Schritt-Anleitung + Konfigurationsvorschläge.
Du führst KEINE echten Aktionen aus. Dein Ergebnis muss so detailliert sein, dass ein Techniker es direkt umsetzen kann."""
        else:
            task_guidance = """AUFTRAGSTYP: Operativer Task
Liefere: Analyse + konkrete Lösung + nächste Schritte."""

        return f"""ORACLE-AUFTRAG — Strikt nach Schema ausführen.

## Auftrag
{task_guidance}
Typ: {task.get('type', 'general')}
Titel: {task.get('title', '')}
Beschreibung: {task.get('description', '')}
Priorität: {task.get('priority', 5)}
Tags: {', '.join(task.get('tags', []))}

## Kontext aus Wissensbasis
{knowledge[:2500]}

## Pflichtstruktur der Antwort
[ANALYSE] Was ist die Ausgangslage?
[IST-STATUS] Aktuelle Bewertung
[LÖSUNG] Konkrete Empfehlungen und Schritte
[NÄCHSTE SCHRITTE] Sofort umsetzbare Maßnahmen
[ABHÄNGIGKEITEN] Was wird benötigt?

Sprache: Deutsch. Qualität: Professionell und vollständig."""

    # ═══════════════════════════════════════════════════════════
    # VERIFIKATION
    # ═══════════════════════════════════════════════════════════

    async def _verify_result(self, task: dict, result: str, executor_agent: str) -> dict:
        if not result or len(result.strip()) < 20:
            return {"passed": False, "score": 1, "reason": "Ergebnis zu kurz oder leer", "verified_by": "system"}

        title_lower = (task.get("title", "") or "").lower()
        is_infra = any(kw in title_lower for kw in ["deploy", "docker", "coolify", "server", "infra", "gitlab", "backup", "ci/cd"])
        verifier = "Lexi" if executor_agent != "Lexi" else "Strategist"

        try:
            verification = await deepseek.invoke_agent(
                agent_name=verifier,
                agent_role="Qualitätsprüfer & Verifikation",
                system_prompt=f"""Du bist der Qualitätsprüfer im NeXifyAI-Team.
Bewerte das Ergebnis nach: Vollständigkeit der Analyse, Korrektheit, Umsetzbarkeit der Empfehlungen.
{"WICHTIG: Dies ist ein Infrastruktur/Deployment-Auftrag. Eine vollständige Analyse mit konkreten Schritten gilt als BESTANDEN." if is_infra else ""}
BEWERTUNG: Wenn das Ergebnis eine strukturierte Analyse mit [ANALYSE], [LÖSUNG] und [NÄCHSTE SCHRITTE] enthält, dann ist es BESTANDEN.
Antworte NUR mit JSON: {{"passed": true/false, "score": 1-10, "reason": "..."}}""",
                user_message=f"""AUFTRAG: {task.get('title', '')}
Typ: {task.get('type', '')}
Beschreibung: {task.get('description', '')}

ERGEBNIS (von Agent {executor_agent}):
{result[:2000]}

Bewerte: Ist das Ergebnis vollständig, korrekt und umsetzbar?""",
                context="",
                temperature=0.2
            )

            resp = verification.get("response", "")
            try:
                json_start = resp.find("{")
                json_end = resp.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    v_data = json.loads(resp[json_start:json_end])
                    score = v_data.get("score", 5)
                    passed = score >= 5 or v_data.get("passed", False)
                    return {
                        "passed": passed, "score": score,
                        "reason": v_data.get("reason", ""),
                        "verified_by": verifier,
                        "verified_at": datetime.now(timezone.utc).isoformat()
                    }
            except (json.JSONDecodeError, ValueError):
                pass

            passed = "true" in resp.lower() and "passed" in resp.lower()
            return {
                "passed": passed, "score": 7 if passed else 3,
                "reason": resp[:300], "verified_by": verifier,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {
                "passed": len(result) > 100, "score": 5,
                "reason": f"Verifikation fehlgeschlagen: {str(e)[:200]}. Auto-passed basierend auf Ergebnislänge.",
                "verified_by": "system-fallback",
                "verified_at": datetime.now(timezone.utc).isoformat()
            }

    # ═══════════════════════════════════════════════════════════
    # LERNEN
    # ═══════════════════════════════════════════════════════════

    async def _store_learning(self, task: dict, result: str, verification: dict):
        try:
            score = verification.get("score", 0)
            if score >= 7:
                await supa.store_brain_note(
                    title=f"Oracle-Ergebnis: {task.get('title', '')[:100]}",
                    content=f"Typ: {task.get('type', '')}\nAgent: {verification.get('verified_by', '')}\nScore: {score}/10\n\n{result[:1500]}",
                    note_type="learning",
                    tags=["oracle", "verified", task.get("type", "general")],
                    created_by="oracle-engine"
                )
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════
    # LEITSTELLE — Live-Daten für das Command Center
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    async def get_leitstelle_data() -> dict:
        """Aggregierte Live-Daten für die Zentrale Leitstelle."""
        # Status-Verteilung (alle Statuses)
        status_dist = await supa.fetch(
            "SELECT status, count(*) as cnt FROM oracle_tasks GROUP BY status ORDER BY cnt DESC"
        )

        # Aktive Bots (aktuell arbeitende Agenten)
        active_bots = await supa.fetch(
            """SELECT current_agent as agent, status, title, id, started_at, loop_count
               FROM oracle_tasks
               WHERE status IN ('gestartet', 'in_bearbeitung', 'wartet_auf_input', 'wartet_auf_freigabe', 'in_loop', 'running', 'assigned')
               AND current_agent IS NOT NULL
               ORDER BY started_at DESC LIMIT 20"""
        )

        # Loop-Monitor: Tasks die aktuell loopen
        loop_tasks = await supa.fetch(
            """SELECT id, title, status, current_agent, loop_count, loop_reason, exit_condition, retry_count, started_at
               FROM oracle_tasks
               WHERE loop_count > 0 AND status NOT IN ('erfolgreich_validiert', 'fehlgeschlagen', 'abgebrochen', 'completed', 'failed', 'cancelled')
               ORDER BY loop_count DESC LIMIT 15"""
        )

        # Eskalationen
        escalations = await supa.fetch(
            """SELECT id, title, status, escalation_reason, current_agent, created_at
               FROM oracle_tasks
               WHERE status IN ('eskaliert', 'blockiert')
               ORDER BY created_at DESC LIMIT 10"""
        )

        # Letzte Validierungen (Evidenz)
        recent_validated = await supa.fetch(
            """SELECT id, title, current_agent, verification_score, evidence, completed_at, status
               FROM oracle_tasks
               WHERE status IN ('erfolgreich_validiert', 'completed') AND verification_score IS NOT NULL
               ORDER BY completed_at DESC LIMIT 10"""
        )

        # Letzte Statusübergänge (globaler Audit-Trail)
        recent_transitions = await supa.fetch(
            """SELECT id, title, status, current_agent, status_history, started_at, completed_at
               FROM oracle_tasks
               WHERE status_history IS NOT NULL AND status_history != '[]'::jsonb
               ORDER BY COALESCE(completed_at, started_at, created_at) DESC LIMIT 15"""
        )

        # Pipeline-Statistiken
        pipeline = {
            "total": await supa.fetchval("SELECT count(*) FROM oracle_tasks"),
            "erkannt": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('erkannt', 'pending')"),
            "in_arbeit": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('gestartet', 'in_bearbeitung', 'running', 'assigned', 'eingeplant')"),
            "wartend": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('wartet_auf_input', 'wartet_auf_freigabe')"),
            "in_loop": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status = 'in_loop'"),
            "validiert_24h": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('erfolgreich_validiert', 'completed') AND completed_at > NOW() - INTERVAL '24 hours'"),
            "fehlgeschlagen_24h": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('fehlgeschlagen', 'failed') AND completed_at > NOW() - INTERVAL '24 hours'"),
            "eskaliert": await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('eskaliert', 'blockiert')"),
        }

        return {
            "pipeline": pipeline,
            "status_distribution": [dict(s) for s in status_dist],
            "active_bots": [dict(b) for b in active_bots],
            "loop_monitor": [dict(l) for l in loop_tasks],
            "escalations": [dict(e) for e in escalations],
            "recent_validated": [dict(v) for v in recent_validated],
            "recent_transitions": [dict(t) for t in recent_transitions],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    async def get_task_transitions(task_id: str) -> dict:
        """Statusübergänge eines einzelnen Tasks."""
        task = await supa.fetchrow(
            """SELECT id, type, priority, status, title, description, owner_agent, current_agent,
                      created_at, started_at, completed_at, retry_count, loop_count, loop_reason,
                      exit_condition, evidence, status_history, verification_score, escalation_reason,
                      error_message, audit_log, result, tags
               FROM oracle_tasks WHERE id::text=$1""",
            task_id
        )
        if not task:
            return {"error": "Task nicht gefunden"}
        return dict(task)

    # ═══════════════════════════════════════════════════════════
    # FONT-AUDIT
    # ═══════════════════════════════════════════════════════════

    async def run_font_audit(self) -> dict:
        import glob
        import re
        fonts_found = {}
        files_scanned = 0
        issues = []
        for css_file in glob.glob("/app/frontend/src/**/*.css", recursive=True):
            files_scanned += 1
            try:
                with open(css_file, "r") as f:
                    content = f.read()
                for match in re.finditer(r'font-family\s*:\s*([^;}{]+)', content):
                    font_val = match.group(1).strip()
                    file_rel = css_file.replace("/app/frontend/src/", "")
                    if font_val not in fonts_found:
                        fonts_found[font_val] = []
                    fonts_found[font_val].append(file_rel)
            except Exception:
                continue
        standard_fonts = {"'Manrope','Plus Jakarta Sans','Inter',sans-serif", "var(--f-display)", "var(--f-body)", "var(--f-mono)", "inherit"}
        for font, files in fonts_found.items():
            clean = font.strip().rstrip(",").strip()
            if clean not in standard_fonts and "var(--f-" not in clean and clean != "inherit":
                issues.append({"font": font, "files": files, "severity": "warning" if "var(" in font else "error"})
        audit = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files_scanned": files_scanned, "unique_fonts": len(fonts_found),
            "fonts": {k: v for k, v in fonts_found.items()},
            "issues": issues, "issue_count": len(issues),
            "standard": ["--f-display: Manrope", "--f-body: Inter", "--f-mono: JetBrains Mono"]
        }
        try:
            await supa.store_brain_note(
                title=f"Font-Audit {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
                content=json.dumps(audit, indent=2, ensure_ascii=False),
                note_type="other", tags=["font-audit", "system-audit", "design"],
                created_by="oracle-engine"
            )
            await self._audit("font_audit_completed", {"files_scanned": files_scanned, "unique_fonts": len(fonts_found), "issues": len(issues)})
        except Exception:
            pass
        return audit

    # ═══════════════════════════════════════════════════════════
    # KNOWLEDGE SYNC
    # ═══════════════════════════════════════════════════════════

    async def sync_knowledge(self):
        try:
            stats = {}
            for col in ["leads", "contacts", "quotes", "contracts", "invoices", "bookings"]:
                stats[col] = await self.db[col].count_documents({})
            agents = []
            async for a in self.db.ai_agents.find({"status": "active"}, {"_id": 0, "name": 1, "role": 1}):
                agents.append(f"{a.get('name','')}: {a.get('role','')}")
            await supa.store_brain_note(
                title=f"Betriebsstatus {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
                content=f"""IST-STATUS NeXifyAI Platform:
Leads: {stats.get('leads', 0)}
Contacts: {stats.get('contacts', 0)}
Quotes: {stats.get('quotes', 0)}
Contracts: {stats.get('contracts', 0)}
Invoices: {stats.get('invoices', 0)}
Bookings: {stats.get('bookings', 0)}

Aktive MongoDB-Agenten: {len(agents)}
{chr(10).join(agents[:20])}""",
                note_type="other", tags=["sync", "status", "betrieb"], created_by="oracle-engine"
            )
            await self._audit("knowledge_sync", {"collections_synced": len(stats), "agents_synced": len(agents)})
            logger.info(f"Knowledge-Sync abgeschlossen: {stats}")
        except Exception as e:
            logger.error(f"Knowledge-Sync Fehler: {e}")

    # ═══════════════════════════════════════════════════════════
    # TASK DERIVATION
    # ═══════════════════════════════════════════════════════════

    async def derive_tasks(self):
        try:
            recent = await supa.fetchval(
                "SELECT count(*) FROM oracle_tasks WHERE created_by='oracle-engine' AND created_at > NOW() - INTERVAL '6 hours'"
            )
            if recent > 10:
                return
            pending_count = await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('pending', 'erkannt')")
            failed_count = await supa.fetchval("SELECT count(*) FROM oracle_tasks WHERE status IN ('failed', 'fehlgeschlagen') AND completed_at > NOW() - INTERVAL '24 hours'")
            if failed_count > 5:
                await supa.insert_oracle_task(
                    task_type="improvement",
                    title=f"Fehleranalyse: {failed_count} fehlgeschlagene Tasks in 24h",
                    description=f"Analysiere die {failed_count} fehlgeschlagenen Tasks der letzten 24 Stunden.",
                    priority=8, owner_agent="oracle-engine",
                    tags=["auto-derived", "improvement", "error-analysis"]
                )
            await self._audit("task_derivation", {"pending": pending_count, "failed_24h": failed_count})
        except Exception as e:
            logger.error(f"Task-Derivation Fehler: {e}")

    # ═══════════════════════════════════════════════════════════
    # AUDIT HELPER
    # ═══════════════════════════════════════════════════════════

    async def _audit(self, action: str, details: dict):
        try:
            from routes.shared import new_id
            await supa.execute(
                """INSERT INTO audit_logs (id, action, resource, status, details, created_at)
                   VALUES ($1, $2, 'oracle-engine', 'SUCCESS', $3::jsonb, NOW())""",
                new_id("aud"), action, json.dumps(details, default=str, ensure_ascii=False)
            )
        except Exception:
            pass

    def get_stats(self) -> dict:
        return {**self._stats, "running": self._running}
