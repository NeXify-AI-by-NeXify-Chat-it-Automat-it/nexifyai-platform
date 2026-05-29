"""Circuit Breaker — prevent cascading failures on external API calls.

Tracks failure rates per service. Opens (trips) when threshold exceeded.
Supports: OpenRouter, Supabase, NScale, external HTTP.
Uses Redis for distributed state, in-memory fallback for local mode.
"""

import time, logging, threading
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.circuit_breaker")

# States
STATE_CLOSED = "closed"       # Normal operation
STATE_OPEN = "open"           # Failing — fast-fail without calling
STATE_HALF_OPEN = "half_open" # Testing — allow one request to check recovery


class CircuitBreaker:
    """Per-service circuit breaker with failure threshold and cooldown."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_requests: int = 1,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_requests = half_open_max_requests

        self._state = STATE_CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._last_state_change = time.time()
        self._half_open_requests = 0
        self._lock = threading.Lock()
        self._total_calls = 0
        self._total_failures = 0

    @property
    def state(self) -> str:
        self._check_auto_recovery()
        return self._state

    def _check_auto_recovery(self):
        """Transition from open->half_open after cooldown."""
        if self._state == STATE_OPEN:
            elapsed = time.time() - self._last_state_change
            if elapsed >= self.recovery_timeout:
                logger.info(f"CB [{self.name}]: open→half_open (cooldown={elapsed:.0f}s)")
                self._state = STATE_HALF_OPEN
                self._half_open_requests = 0
                self._last_state_change = time.time()

    def _trip(self):
        """Open the circuit."""
        self._state = STATE_OPEN
        self._last_failure_time = time.time()
        self._last_state_change = time.time()
        self._half_open_requests = 0
        logger.warning(f"CB [{self.name}]: TRIPPED → OPEN (failures={self._failure_count})")

    def call(self, fn, *args, **kwargs):
        """Execute fn with circuit breaker protection.

        Returns fn result on success.
        Raises CircuitBreakerOpen if circuit is open (fast-fail).
        """
        self._check_auto_recovery()

        with self._lock:
            if self._state == STATE_OPEN:
                raise CircuitBreakerOpen(f"CB [{self.name}]: circuit open, fast-fail")
            
            if self._state == STATE_HALF_OPEN:
                if self._half_open_requests >= self.half_open_max_requests:
                    raise CircuitBreakerOpen(f"CB [{self.name}]: half-open max requests reached")
                self._half_open_requests += 1

            self._total_calls += 1

        try:
            result = fn(*args, **kwargs)
            
            # Success — reset on half-open (full recovery)
            with self._lock:
                if self._state == STATE_HALF_OPEN:
                    logger.info(f"CB [{self.name}]: half_open→closed (recovered)")
                    self._reset()
            
            return result

        except Exception as e:
            with self._lock:
                self._failure_count += 1
                self._total_failures += 1
                self._last_failure_time = time.time()

                if self._state == STATE_HALF_OPEN:
                    self._trip()
                elif self._failure_count >= self.failure_threshold:
                    self._trip()

            raise

    def _reset(self):
        """Reset to closed state."""
        self._state = STATE_CLOSED
        self._failure_count = 0
        self._last_state_change = time.time()

    def reset(self):
        """Manual reset."""
        with self._lock:
            self._reset()
            logger.info(f"CB [{self.name}]: manually reset → closed")

    def status(self) -> dict:
        """Return detailed status for monitoring."""
        with self._lock:
            return {
                "name": self.name,
                "state": self._state,
                "failure_count": self._failure_count,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "total_calls": self._total_calls,
                "total_failures": self._total_failures,
                "last_failure": datetime.fromtimestamp(self._last_failure_time, tz=timezone.utc).isoformat() if self._last_failure_time else None,
                "last_state_change": datetime.fromtimestamp(self._last_state_change, tz=timezone.utc).isoformat(),
            }


class CircuitBreakerOpen(Exception):
    """Raised when circuit is open — don't call the remote service."""
    pass


# Registry of circuit breakers by service name
_registry: dict[str, CircuitBreaker] = {}
_registry_lock = threading.Lock()


def get_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker for a service."""
    with _registry_lock:
        if name not in _registry:
            _registry[name] = CircuitBreaker(name=name, **kwargs)
        return _registry[name]


def all_breaker_statuses() -> dict[str, dict]:
    """Get status of all registered circuit breakers."""
    return {name: cb.status() for name, cb in _registry.items()}
