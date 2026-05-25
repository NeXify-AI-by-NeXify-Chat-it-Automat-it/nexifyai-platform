"""Bearer token authentication."""
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import PROJECT_MANAGER_API_TOKEN

_bearer = HTTPBearer()

async def verify_token(creds: HTTPAuthorizationCredentials = Security(_bearer)) -> str:
    if not PROJECT_MANAGER_API_TOKEN:
        raise HTTPException(status_code=500, detail="Server token not configured")
    if creds.credentials != PROJECT_MANAGER_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return creds.credentials
