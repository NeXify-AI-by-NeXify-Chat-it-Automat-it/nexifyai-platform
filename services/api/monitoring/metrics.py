"""
NeXifyAI — Prometheus Metrics
Exposes /metrics endpoint in Prometheus text format.

Usage:
    from backend.monitoring.metrics import get_metrics, HTTP_REQUEST_COUNT
    HTTP_REQUEST_COUNT.labels(method="GET", endpoint="/api/health", status="200").inc()
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from prometheus_client.exposition import CONTENT_TYPE_LATEST

# ══════════════════════════════════════════
# HTTP METRICS
# ══════════════════════════════════════════

HTTP_REQUEST_COUNT = Counter(
    'nexifyai_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_LATENCY = Histogram(
    'nexifyai_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    'nexifyai_http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method']
)

# ══════════════════════════════════════════
# BUSINESS METRICS
# ══════════════════════════════════════════

AI_TOKENS_USED = Counter(
    'nexifyai_ai_tokens_total',
    'Total AI tokens used',
    ['model', 'provider', 'operation']
)

AI_REQUEST_LATENCY = Histogram(
    'nexifyai_ai_request_duration_seconds',
    'AI request latency',
    ['model', 'provider'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

LEADS_CREATED = Counter(
    'nexifyai_leads_created_total',
    'Total leads created',
    ['source', 'segment']
)

CONVERSIONS = Counter(
    'nexifyai_conversions_total',
    'Total conversions',
    ['type']  # demo_request, trial_start, purchase
)

# ══════════════════════════════════════════
# SYSTEM METRICS
# ══════════════════════════════════════════

SYSTEM_HEALTH = Gauge(
    'nexifyai_health_score',
    'Overall system health score (0-100)'
)

CONNECTION_STATUS = Gauge(
    'nexifyai_connection_status',
    'Connection health per service (0=down, 1=up)',
    ['service']
)

CRON_JOBS_EXECUTED = Counter(
    'nexifyai_cron_jobs_executed_total',
    'Total cron job executions',
    ['job_name', 'status']
)

TASKS_COMPLETED = Counter(
    'nexifyai_tasks_completed_total',
    'Total tasks completed',
    ['source']
)

# ══════════════════════════════════════════
# APP INFO
# ══════════════════════════════════════════

APP_INFO = Info('nexifyai_app', 'Application information')
APP_INFO.info({
    'version': '2.0.0',
    'environment': 'production',
})


# ══════════════════════════════════════════
# METRICS ENDPOINT HELPER
# ══════════════════════════════════════════

def get_metrics() -> bytes:
    """Generate Prometheus metrics in text format."""
    return generate_latest(REGISTRY)


def get_metrics_content_type() -> str:
    """Return content type for metrics endpoint."""
    return CONTENT_TYPE_LATEST
