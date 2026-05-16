"""
NeXifyAI — Sentry Error Tracking
Initialisiert Sentry SDK für Backend und Frontend.

Usage:
    import sentry_sdk
    from backend.monitoring.sentry import init_sentry
    init_sentry()
"""

import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration


def init_sentry(dsn: str = None, environment: str = None):
    """Initialize Sentry SDK. No-op if SENTRY_DSN not configured."""
    dsn = dsn or os.getenv("SENTRY_DSN")
    if not dsn:
        print("[monitoring] Sentry: No SENTRY_DSN configured — skipping")
        return

    environment = environment or os.getenv("ENVIRONMENT", "production")

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            HttpxIntegration(),
        ],
        
        # Release tracking
        release=os.getenv("GIT_SHA") or os.getenv("VERCEL_GIT_COMMIT_SHA"),
        
        # PII protection
        send_default_pii=False,
        
        # Performance
        _experiments={
            "continuous_profiling_auto_start": True,
        },
    )
    
    print(f"[monitoring] Sentry initialized: env={environment}")

    return sentry_sdk


def capture_exception(error: Exception, context: dict = None):
    """Capture exception with optional context data."""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        sentry_sdk.capture_exception(error)


def set_user_context(user_id: str, email: str = None, tenant_id: str = None):
    """Set user context for error tracking (no PII)."""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,  # Will be hashed if send_default_pii=False
        "tenant_id": tenant_id,
    })
