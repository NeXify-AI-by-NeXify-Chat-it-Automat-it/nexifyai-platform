
from fastapi import APIRouter

class CSOApiRouter:
    def __init__(self, core):
        self.core = core
    
    def to_fastapi_router(self):
        return APIRouter(prefix="/api/security", tags=["Security"])
