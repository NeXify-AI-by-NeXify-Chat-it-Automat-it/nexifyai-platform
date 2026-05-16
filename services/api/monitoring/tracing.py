"""
NeXifyAI — OpenTelemetry Tracing
Distributed tracing via OTLP (gRPC or HTTP) to Jaeger/Grafana Tempo.

Usage:
    from backend.monitoring.tracing import init_tracing
    init_tracing()
    
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("operation_name"):
        ...
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


def init_tracing(
    service_name: str = "nexifyai",
    otlp_endpoint: str = None,
    use_http: bool = False,
):
    """Initialize OpenTelemetry tracing. No-op if OTEL_EXPORTER_OTLP_ENDPOINT not configured."""
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp_endpoint:
        print("[monitoring] OpenTelemetry: No endpoint configured — skipping")
        return None

    # Create resource
    resource = Resource.create({
        SERVICE_NAME: service_name,
        "deployment.environment": os.getenv("ENVIRONMENT", "production"),
    })

    # Create exporter
    if use_http:
        exporter = HTTPExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    else:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

    # Create provider
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument libraries
    FastAPIInstrumentor().instrument()
    HTTPXInstrumentor().instrument()
    
    try:
        RedisInstrumentor().instrument()
    except Exception:
        pass  # Redis might not be installed

    print(f"[monitoring] OpenTelemetry initialized: endpoint={otlp_endpoint}")
    
    return trace.get_tracer(__name__)


def get_tracer(name: str = __name__):
    """Get a tracer instance."""
    return trace.get_tracer(name)
