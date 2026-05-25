"""Bearer token authentication with audit logging."""
import logging
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import PROJECT_MANAGER_API_TOKEN

logger = logging.getLogger("pm.auth")
_bearer = HTTPBearer()

async def verify_token(creds: HTTPAuthorizationCredentials = Security(_bearer)) -> str:
    if not PROJECT_MANAGER_API_TOKEN:
        logger.error("Server token not configured - rejecting all requests")
        raise HTTPException(status_code=500, detail="Server token not configured")
    if creds.credentials != PROJECT_MANAGER_API_TOKEN:
        logger.warning("Invalid token attempt (IP hidden)")
        raise HTTPException(status_code=401, detail="Invalid token")
    return creds.credentials
