"""Goose worker controller - runs goose in isolated, controlled mode."""
import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
from app.config import EVIDENCE_DIR, DATA_DIR
from app.schemas import TaskRecord, TaskStatus
from app.task_registry import update_status
from app.brain_client import check_health as brain_health
from app.redaction import redact_string
from app.evidence import save_evidence
from app.warning_classifier import classify_output, has_blocker_warnings
from app.skill_selector import select_and_validate
import os

logger = logging.getLogger("pm.goose")

DRY_RUN = os.environ.get("DRY_RUN_MODE", "true").lower() == "true"
# Fallback chain: env var → /root/.local/bin/goose → PATH goose
_goose_path = os.environ.get("GOOSE_BIN") or "/root/.local/bin/goose"
if not os.path.isfile(_goose_path):
    import shutil
    _goose_path = shutil.which("goose") or "goose"
GOOSE_BIN = _goose_path
WORKER_TIMEOUT = int(os.environ.get("WORKER_TIMEOUT", "600"))

GOOSE_TEMPLATE = """
AUFGABE:
{goal}

TASK-ID: {task_id}
MODUS: {mode}

Vor Ausfuehrung:
- Lade Brain-Kontext.
- Lade Project-Manager-Task-Kontext.
- Lade relevante Skills ausschliesslich aus der Master-Skill-Registry:
  /opt/nexify/goose-skill-bridge/registry/
- Nutze keine lokalen Fake-Skills aus /root/.config/goose/skills oder aehnlichen Pfaden.
- Wenn Skill-Herkunft unklar ist: STOPP.
- Wenn Project-Tracker nicht parsebar ist: STOPP.
- Wenn Warnungen auftreten: als Blocker oder Follow-up klassifizieren.

REGELN:
- Keine Secrets ausgeben.
- Keine produktiven Services aendern.
- Evidence-Pflicht fuer alle Ergebnisse.
- Abbruch bei: {abort_conditions}
"""

async def run_task(task: TaskRecord) -> dict:
    # Step 1: Skill registry check (wrapped in try/except — old tasks may have incompatible data)
    try:
        skill_ok, skill_err, skill_evidence = await select_and_validate(
            task.task_id, task.goal, task.mode.value
        )
    except Exception as e:
        logger.error("Skill registry crash for task %s: %s", task.task_id, e)
        update_status(task.task_id, TaskStatus.failed, error=f"Skill registry: {e}")
        return {"status": "failed", "error": f"Skill registry: {e}"}

    if not skill_ok:
        update_status(task.task_id, TaskStatus.blocked_skill_registry, error=skill_err)
        return {"status": "blocked_skill_registry", "error": skill_err}

    # Step 2: Brain health
    try:
        brain_ok = await brain_health()
    except Exception as e:
        logger.error("Brain health crash for task %s: %s", task.task_id, e)
        brain_ok = False

    if not brain_ok and not DRY_RUN:
        update_status(task.task_id, TaskStatus.blocked, error="Brain health check failed")
        return {"status": "blocked", "error": "Brain not reachable"}

    update_status(task.task_id, TaskStatus.running)

    if DRY_RUN:
        return await _dry_run(task, skill_evidence)

    prompt = GOOSE_TEMPLATE.format(
        goal=task.goal, task_id=task.task_id, mode=task.mode.value,
        abort_conditions=", ".join(task.abort_conditions) or "none specified",
    )

    try:
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                GOOSE_BIN, "run", "-i", "-",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(DATA_DIR),
            ), timeout=10.0
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=prompt.encode("utf-8")), timeout=WORKER_TIMEOUT
        )
        output = redact_string(stdout.decode("utf-8", errors="replace"))
        err_output = redact_string(stderr.decode("utf-8", errors="replace"))

        # Classify warnings
        warnings = classify_output(output)
        has_blockers = has_blocker_warnings(output)

        if has_blockers:
            result = {"stdout": output[-3000:], "warnings": warnings, "returncode": proc.returncode}
            evidence_path = save_evidence(task.task_id, json.dumps(result, indent=2), err_output)
            update_status(task.task_id, TaskStatus.blocked, result=result, evidence_path=evidence_path)
            return result

        if proc.returncode == 0:
            result = {"stdout": output[-3000:], "warnings": warnings, "returncode": 0, "skill_evidence": skill_evidence}
            evidence_path = save_evidence(task.task_id, output, err_output)
            update_status(task.task_id, TaskStatus.completed, result=result, evidence_path=evidence_path)
            return result
        else:
            result = {"stderr": err_output[-2000:], "warnings": warnings, "returncode": proc.returncode}
            evidence_path = save_evidence(task.task_id, output, err_output)
            update_status(task.task_id, TaskStatus.failed, result=result, evidence_path=evidence_path)
            return result
    except asyncio.TimeoutError:
        update_status(task.task_id, TaskStatus.failed, error=f"Timeout after {WORKER_TIMEOUT}s")
        return {"status": "timeout", "error": f"Timeout after {WORKER_TIMEOUT}s"}
    except Exception as e:
        update_status(task.task_id, TaskStatus.failed, error=str(e))
        return {"status": "error", "error": str(e)}

async def _dry_run(task: TaskRecord, skill_evidence: list) -> dict:
    brain_ok = await brain_health()
    result = {
        "dry_run": True,
        "task_id": task.task_id,
        "mode": task.mode.value,
        "goal": task.goal[:200],
        "brain_health": brain_ok,
        "skill_evidence": skill_evidence,
        "fake_skills_blocked": True,
        "warning_findings": [],
        "simulated": "Goose would execute this task in controlled isolation.",
    }
    evidence_path = save_evidence(task.task_id, json.dumps(result, indent=2), "")
    update_status(task.task_id, TaskStatus.completed, result=result, evidence_path=evidence_path)
    return result
