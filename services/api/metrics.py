
import time
from fastapi import Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Metrics
HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
HTTP_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
WORKFLOW_EXECUTIONS = Counter("workflow_executions_total", "Total workflow executions", ["workflow_type", "status"])
WORKER_HEALTH = Gauge("worker_health", "Worker health status (1=up, 0=down)", ["worker_type"])
BRAIN_QUERIES = Counter("brain_queries_total", "Total Brain queries", ["collection", "status"])
AGENT_CALLS = Counter("agent_calls_total", "Total agent LLM calls", ["agent", "model", "status"])
AGENT_LATENCY = Histogram("agent_call_duration_seconds", "Agent call latency", ["agent", "model"])

async def metrics_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    
    # Only track API routes
    if path.startswith("/api/"):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        HTTP_REQUESTS.labels(method=method, endpoint=path, status=response.status_code).inc()
        HTTP_LATENCY.labels(method=method, endpoint=path).observe(duration)
        return response
    
    return await call_next(request)

def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
