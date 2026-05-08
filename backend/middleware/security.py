"""
NeXifyAI — Security Middleware
CSP Headers, Rate Limiting, JWT Rotation, API Signing Validation.

Usage (FastAPI):
    from backend.middleware.security import SecurityMiddleware
    app.add_middleware(SecurityMiddleware)
"""

import time
import hashlib
import hmac
from typing import Dict, Tuple
from datetime import datetime, timezone

# ══════════════════════════════════════════
# CSP HEADERS (Content Security Policy)
# ══════════════════════════════════════════

CSP_POLICY = "; ".join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://vercel.live",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://api.openrouter.ai https://*.supabase.co https://api.resend.com",
    "frame-src 'self' https://vercel.live",
    "frame-ancestors 'self'",
    "form-action 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "upgrade-insecure-requests",
])

SECURITY_HEADERS = {
    "Content-Security-Policy": CSP_POLICY,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def get_security_headers() -> Dict[str, str]:
    """Return standard security headers for all responses."""
    return SECURITY_HEADERS.copy()


# ══════════════════════════════════════════
# RATE LIMITING (Simple Token Bucket)
# ══════════════════════════════════════════

class RateLimiter:
    """In-memory token bucket rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: Dict[str, Tuple[int, float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        if key not in self._buckets:
            self._buckets[key] = (1, now)
            return True

        count, window_start = self._buckets[key]
        if now - window_start > self.window_seconds:
            self._buckets[key] = (1, now)
            return True

        if count < self.max_requests:
            self._buckets[key] = (count + 1, window_start)
            return True

        return False

    def cleanup(self):
        """Remove expired buckets (call periodically)."""
        now = time.time()
        expired = [
            k for k, (_, ws) in self._buckets.items()
            if now - ws > self.window_seconds * 2
        ]
        for k in expired:
            del self._buckets[k]


# Global instances
api_limiter = RateLimiter(max_requests=300, window_seconds=60)  # 5 req/s
auth_limiter = RateLimiter(max_requests=10, window_seconds=60)  # Login brute-force


# ══════════════════════════════════════════
# JWT ROTATION UTILITY
# ══════════════════════════════════════════

JWT_MAX_AGE_SECONDS = 15 * 60  # 15 minutes access token
JWT_REFRESH_MAX_AGE_SECONDS = 7 * 24 * 3600  # 7 days refresh token


def is_jwt_expiring_soon(issued_at: float, threshold_seconds: int = 300) -> bool:
    """Check if JWT should be rotated (within threshold of expiry)."""
    age = time.time() - issued_at
    return age > (JWT_MAX_AGE_SECONDS - threshold_seconds)


# ══════════════════════════════════════════
# API SIGNING (HMAC-SHA256)
# ══════════════════════════════════════════

def sign_payload(payload: str, secret: str) -> str:
    """Create HMAC-SHA256 signature for payload."""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature. Constant-time comparison."""
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)


# ══════════════════════════════════════════
# AUDIT LOGGING
# ══════════════════════════════════════════

def audit_log(
    event: str,
    actor: str,
    resource: str,
    detail: str = "",
    severity: str = "INFO"
) -> Dict:
    """Create structured audit log entry."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor": actor,
        "resource": resource,
        "detail": detail,
        "severity": severity,
        "version": "1.0",
    }
