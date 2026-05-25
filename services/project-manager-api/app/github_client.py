"""GitHub webhook receiver - MVP stub."""
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from app.config import EVIDENCE_DIR
import os

logger = logging.getLogger("pm.github")
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        logger.warning("No GITHUB_WEBHOOK_SECRET configured")
        return False
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def store_event(event_type: str, payload: dict) -> str:
    events_dir = EVIDENCE_DIR / "github-events"
    events_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    f = events_dir / f"{event_type}_{ts}.json"
    f.write_text(json.dumps(payload, indent=2, default=str))
    return str(f)
