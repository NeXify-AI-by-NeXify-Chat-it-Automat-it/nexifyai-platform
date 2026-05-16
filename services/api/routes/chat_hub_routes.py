"""Cross-platform chat hub — eine Konversation für CLI, Telegram, Admin Chat"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from routes.shared import S, get_current_admin

logger = logging.getLogger("nexifyai.chat_hub")
router = APIRouter(prefix="/api/admin/chat-hub", tags=["chat-hub"])

class ChatMessage(BaseModel):
    platform: str  # "cli", "telegram", "admin-chat"
    content: str
    role: str = "user"  # "user" oder "assistant"
    conversation_id: Optional[str] = None

@router.post("")
async def save_message(msg: ChatMessage, admin: dict = Depends(get_current_admin)):
    """Speichert eine plattformübergreifende Chat-Nachricht."""
    doc = msg.dict()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["admin_email"] = admin.get("email", "unknown")
    result = await S.db.chat_hub.insert_one(doc)
    return {"status": "ok", "id": str(result.inserted_id)}

@router.get("")
async def get_messages(limit: int = 20, admin: dict = Depends(get_current_admin)):
    """Gibt die letzten plattformübergreifenden Chat-Nachrichten zurück."""
    cursor = S.db.chat_hub.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    messages = await cursor.to_list(length=limit)
    messages.reverse()
    return messages
