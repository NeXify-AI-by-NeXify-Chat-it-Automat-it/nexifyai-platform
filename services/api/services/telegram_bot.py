#!/usr/bin/env python3
"""Telegram Bot Service for NeXifyAI — Webhook-basierter Bot."""
import os, json, logging, httpx
from typing import Optional

logger = logging.getLogger("nexifyai.telegram")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBHOOK_PATH = "/api/webhooks/telegram"


class TelegramBot:
    def __init__(self, db=None, comms_service=None):
        self.db = db
        self.comms = comms_service
        self._client: Optional[httpx.AsyncClient] = None

    async def _http(self):
        if not self._client:
            self._client = httpx.AsyncClient(timeout=15)
        return self._client

    async def set_webhook(self, base_url: str) -> dict:
        """Register webhook with Telegram API."""
        c = await self._http()
        url = f"{base_url.rstrip('/')}{WEBHOOK_PATH}"
        r = await c.post(f"{API_BASE}/setWebhook", json={"url": url, "allowed_updates": ["message"]})
        data = r.json()
        logger.info(f"Telegram webhook set: {data.get('description', '?')}")
        return data

    async def delete_webhook(self) -> dict:
        c = await self._http()
        r = await c.post(f"{API_BASE}/deleteWebhook")
        return r.json()

    async def send_message(self, chat_id: int, text: str) -> dict:
        c = await self._http()
        r = await c.post(f"{API_BASE}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
        return r.json()

    async def handle_update(self, update: dict) -> dict:
        """Process incoming Telegram update."""
        msg = update.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        from_user = msg.get("from", {})

        if not chat_id or not text:
            return {"status": "ignored"}

        logger.info(f"Telegram from {from_user.get('id')}: {text[:80]}")

        # Route to AI via comms_service
        if self.comms and self.db:
            contact_email = f"tg_{chat_id}@telegram.nexifyai"
            conv = await self.db.conversations.find_one({"channel": "telegram", "channel_id": str(chat_id)})
            if not conv:
                conv_id = f"tg_{os.urandom(8).hex()}"
                await self.db.conversations.insert_one({
                    "conversation_id": conv_id, "channel": "telegram",
                    "channel_id": str(chat_id), "contact_email": contact_email,
                    "created_at": __import__("datetime").datetime.now().isoformat()
                })
            else:
                conv_id = conv["conversation_id"]

            await self.db.messages.insert_one({
                "conversation_id": conv_id, "channel": "telegram",
                "sender": "customer", "content": text,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            })

            reply = f"Danke fuer deine Nachricht, {from_user.get('first_name', 'User')}! Ein Mitarbeiter wird sich kuemmern."
            await self.send_message(chat_id, reply)
            return {"status": "ok", "chat_id": chat_id, "text": text}

        # Fallback: direct reply
        await self.send_message(chat_id, f"Empfangen: {text[:100]}")
        return {"status": "ok", "chat_id": chat_id}
