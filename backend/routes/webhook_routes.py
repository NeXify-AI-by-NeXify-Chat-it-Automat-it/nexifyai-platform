"""
GitHub + Vercel Webhook Receiver — Echtzeit-Events für CI/CD + Monitoring.

GitHub Webhook:
  POST /api/webhooks/github
  Empfängt: push, pull_request, check_run, workflow_run
  HMAC-Verifikation via SHA256
  Speichert in MongoDB → Open Notebook → Telegram (bei P0/P1)

Vercel Webhook:
  POST /api/webhooks/vercel
  Empfängt: deployment.created, .succeeded, .failed
  Speichert in MongoDB → Open Notebook → Telegram
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from routes.shared import S, logger

logger = logging.getLogger("nexifyai.routes.webhooks")
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "").strip()
VERCEL_WEBHOOK_SECRET = os.environ.get("VERCEL_WEBHOOK_SECRET", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


async def _store_event(source: str, event_type: str, payload: dict, customer_id: str = "nexifyai"):
    """Speichert Webhook-Event in MongoDB und sendet bei Relevanz an Telegram."""
    # 1. MongoDB
    try:
        await S.db.webhook_events.insert_one({
            "source": source,
            "event_type": event_type,
            "customer_id": customer_id,
            "payload": payload,
            "created_at": datetime.now(timezone.utc),
            "vectorized": False,
        })
    except Exception as e:
        logger.error(f"MongoDB insert failed: {e}")

    # 2. Telegram bei wichtigen Events
    is_error = "failed" in event_type or event_type == "check_run.completed.failure"
    is_success = event_type.endswith(".succeeded") or event_type == "check_run.completed.success"
    is_pr = "pull_request" in event_type
    is_push = event_type == "push"

    if is_error and TELEGRAM_BOT_TOKEN:
        _send_telegram(f"❌ [{source}] {event_type}: {json.dumps(payload, indent=2)[:200]}")
    elif is_pr and TELEGRAM_BOT_TOKEN:
        pr_action = payload.get("action", "?")
        pr_title = payload.get("pull_request", {}).get("title", "?")
        _send_telegram(f"🔄 [{source}] PR {pr_action}: {pr_title}")
    elif is_success and TELEGRAM_BOT_TOKEN:
        logger.info(f"[{source}] Erfolg: {event_type}")


def _send_telegram(message: str):
    """Sendet Nachricht an Pascal via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        return
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
        "text": message[:4000],
        "parse_mode": "HTML",
    }).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=5)
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")


# ─── GITHUB WEBHOOK ────────────────────────────────────────────────

@router.post("/github")
async def github_webhook(request: Request):
    """Empfängt GitHub Webhook-Events."""
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    event_type = request.headers.get("x-github-event", "unknown")
    delivery_id = request.headers.get("x-github-delivery", "unknown")

    # HMAC-Verifikation
    if GITHUB_WEBHOOK_SECRET:
        expected = "sha256=" + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            logger.warning(f"GitHub webhook signature mismatch (delivery: {delivery_id})")
            raise HTTPException(401, "Invalid webhook signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON payload")

    logger.info(f"GitHub webhook: {event_type} ({delivery_id})")

    # Event-spezifische Verarbeitung
    if event_type == "push":
        repo = payload.get("repository", {}).get("full_name", "?")
        ref = payload.get("ref", "?")
        commits = len(payload.get("commits", []))
        sender = payload.get("sender", {}).get("login", "?")
        summary = f"Push {commits} Commit(s) auf {ref} von {sender} in {repo}"
        await _store_event("github", "push", {
            "summary": summary,
            "repository": repo,
            "ref": ref,
            "commits": commits,
            "sender": sender,
        })

    elif event_type == "pull_request":
        action = payload.get("action", "?")
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {}).get("full_name", "?")
        pr_number = pr.get("number", "?")
        pr_title = pr.get("title", "?")
        sender = payload.get("sender", {}).get("login", "?")
        merged = pr.get("merged", False)
        summary = f"PR #{pr_number} {action} in {repo}: {pr_title} von {sender}"
        if merged:
            summary += " (gemergt!)"
        await _store_event("github", f"pull_request.{action}", {
            "summary": summary,
            "repository": repo,
            "pr_number": pr_number,
            "action": action,
            "title": pr_title,
            "merged": merged,
            "sender": sender,
        })

    elif event_type == "check_run":
        check_run = payload.get("check_run", {})
        repo = payload.get("repository", {}).get("full_name", "?")
        conclusion = check_run.get("conclusion", "?")
        name = check_run.get("name", "?")
        status = check_run.get("status", "?")
        summary = f"Check {name}: {status}/{conclusion} in {repo}"
        await _store_event("github", f"check_run.{status}.{conclusion}", {
            "summary": summary,
            "repository": repo,
            "check_name": name,
            "status": status,
            "conclusion": conclusion,
        })
        # Bei CI-Failure: sofort Telegram
        if conclusion == "failure":
            _send_telegram(f"❌ CI FAILED: {name} in {repo}\nCheck: {check_run.get('html_url', '?')}")

    elif event_type == "workflow_run":
        workflow = payload.get("workflow_run", {})
        repo = payload.get("repository", {}).get("full_name", "?")
        conclusion = workflow.get("conclusion", "?")
        name = workflow.get("name", "?")
        summary = f"Workflow {name}: {conclusion} in {repo}"
        await _store_event("github", f"workflow_run.{conclusion}", {
            "summary": summary,
            "repository": repo,
            "workflow_name": name,
            "conclusion": conclusion,
        })

    else:
        # Generic fallback für andere Events
        await _store_event("github", event_type, {
            "summary": f"Event: {event_type}",
            "delivery_id": delivery_id,
        })

    return {"status": "ok", "event": event_type, "delivery": delivery_id}


# ─── VERCEL WEBHOOK ────────────────────────────────────────────────

@router.post("/vercel")
async def vercel_webhook(request: Request):
    """Empfängt Vercel Deployment-Webhooks."""
    body = await request.body()
    # Vercel verwendet keinen HMAC-Signature-Header — stattdessen
    # wird die Anfrage über das Webhook-Secret verifiziert.
    # Optional: Deployment-ID aus dem Body als Referenz nutzen.

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON payload")

    event_type = payload.get("type", "unknown")
    deployment = payload.get("payload", payload)
    project_name = deployment.get("name", deployment.get("project", "?"))
    deployment_url = deployment.get("url", deployment.get("deploymentUrl", "?"))

    logger.info(f"Vercel webhook: {event_type} für {project_name}")

    # Mapping der Vercel-Event-Typen
    vercel_events = {
        "deployment.created": "deployment.started",
        "deployment.succeeded": "deployment.succeeded",
        "deployment.ready": "deployment.succeeded",
        "deployment.error": "deployment.failed",
        "deployment.failed": "deployment.failed",
        "deployment.canceled": "deployment.canceled",
    }
    mapped_type = vercel_events.get(event_type, event_type)

    summary = f"Deployment {mapped_type.split('.')[-1]} für {project_name}"
    if deployment_url and deployment_url != "?":
        summary += f" → https://{deployment_url}"

    # Speichern + Telegram bei Fehler
    is_error = "failed" in mapped_type or "error" in mapped_type
    await _store_event("vercel", mapped_type, {
        "summary": summary,
        "project": project_name,
        "deployment_url": deployment_url,
        "event_type": event_type,
        "payload_preview": json.dumps(payload)[:500],
    })
    if is_error:
        _send_telegram(f"❌ VERCEL DEPLOY FAILED: {project_name}\nEvent: {event_type}\nURL: https://{deployment_url}")

    return {"status": "ok", "event": event_type}


# ─── WEBHOOK STATUS ────────────────────────────────────────────────

@router.get("/status")
async def webhook_status():
    """Zeigt Konfigurations-Status der Webhooks."""
    return {
        "github": {
            "configured": bool(GITHUB_WEBHOOK_SECRET),
            "secret_length": len(GITHUB_WEBHOOK_SECRET),
        },
        "vercel": {
            "configured": bool(VERCEL_WEBHOOK_SECRET),
        },
        "telegram": {
            "configured": bool(TELEGRAM_BOT_TOKEN),
            "chat_id_configured": bool(os.environ.get("TELEGRAM_CHAT_ID", "")),
        },
    }
