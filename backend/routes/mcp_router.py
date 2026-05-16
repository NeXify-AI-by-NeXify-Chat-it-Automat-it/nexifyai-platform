
import httpx, logging
from fastapi import APIRouter, HTTPException, Request
logger = logging.getLogger("nexifyai.mcp")
mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])
SERVICES = {
    "qdrant": {"host": "localhost", "port": 6333, "health_path": "/readyz"},
    "hermes": {"host": "localhost", "port": 8642, "health_path": "/health"},
    "mindsdb": {"host": "localhost", "port": 32779, "health_path": "/api/status"},
    "dashboard": {"host": "localhost", "port": 9119, "health_path": "/"},
    "workspace": {"host": "localhost", "port": 32776, "health_path": "/health"},
}
@mcp_router.get("/health")
async def health(): return {"status":"ok","router":"mcp","services":len(SERVICES)}
@mcp_router.get("/services")
async def list_svc():
    r={}
    for n,s in SERVICES.items():
        try:
            resp=httpx.get(f"http://{s['host']}:{s['port']}{s['health_path']}",timeout=5)
            r[n]={"host":s["host"],"port":s["port"],"status":"online" if resp.status_code<500 else "degraded"}
        except:
            r[n]={"host":s["host"],"port":s["port"],"status":"offline"}
    return {"services":r}
@mcp_router.get("/service/{name}")
async def get_svc(name:str):
    s=SERVICES.get(name)
    if not s: raise HTTPException(404,f"Service {name} not registered")
    try:
        resp=httpx.get(f"http://{s['host']}:{s['port']}{s['health_path']}",timeout=5)
        return {"name":name,"host":s["host"],"port":s["port"],"status":"online" if resp.status_code<500 else "degraded"}
    except:
        return {"name":name,"host":s["host"],"port":s["port"],"status":"offline"}
@mcp_router.post("/proxy/{name}")
async def proxy(name:str, request:Request):
    s=SERVICES.get(name)
    if not s: raise HTTPException(404,f"Service {name} not registered")
    body=await request.json() if await request.body() else {}
    path=request.query_params.get("path","")
    try:
        resp=httpx.post(f"http://{s['host']}:{s['port']}{path}",json=body,timeout=30)
        return {"status":resp.status_code,"response":resp.json() if resp.headers.get("content-type","").startswith("application/json") else resp.text[:1000]}
    except Exception as e:
        raise HTTPException(502,f"Proxy failed: {e}")
logger.info("MCP Router initialized - %d services", len(SERVICES))
