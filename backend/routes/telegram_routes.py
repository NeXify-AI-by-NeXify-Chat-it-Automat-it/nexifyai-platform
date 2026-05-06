"""Telegram Webhook Routes for NeXifyAI Backend."""
import logging
from fastapi import APIRouter, Request
from routes.shared import S

logger = logging.getLogger("nexifyai.routes.telegram")
router = APIRouter(tags=["telegram"])


@router.post("/api/webhooks/telegram")
async def telegram_webhook(request: Request):
    """Telegram Bot Webhook — empfaengt Nachrichten von Nutzern."""
    update = await request.json()
    bot = getattr(S, "telegram_bot", None)
    if bot:
        result = await bot.handle_update(update)
        return result
    logger.warning("Telegram bot not initialized")
    return {"status": "error", "detail": "Bot not configured"}


@router.post("/api/admin/telegram/set-webhook")
async def admin_set_telegram_webhook(request: Request):
    """Admin: Telegram Webhook registrieren (nach Backend-Deploy)."""
    body = await request.json()
    base_url = body.get("base_url", "https://www.nexify-automate.com")
    bot = getattr(S, "telegram_bot", None)
    if bot:
        result = await bot.set_webhook(base_url)
        return result
    return {"status": "error", "detail": "Bot not configured"}


@router.get("/api/admin/telegram/status")
async def telegram_status():
    """Admin: Telegram Bot-Status abfragen."""
    bot = getattr(S, "telegram_bot", None)
    if not bot:
        return {"configured": False, "hint": "TELEGRAM_BOT_TOKEN in .env setzen"}
    return {"configured": True, "webhook_path": "/api/webhooks/telegram"}
