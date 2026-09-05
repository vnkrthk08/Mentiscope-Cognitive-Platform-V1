import time
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger("mentiscope.speech.circuit_breaker")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker trips to OPEN state preventing requests to target provider."""
    pass


class CircuitBreaker:
    """Implements Circuit Breaker Pattern protecting speech providers from cascading overloads."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure: float = 0.0
        self.last_success: float = 0.0
        self.open_since: float = 0.0

    def record_success(self):
        self.success_count += 1
        self.last_success = time.time()
        if self.state == "HALF_OPEN":
            # Success in HALF_OPEN resets breaker back to CLOSED
            self.reset()

    def record_failure(self):
        self.failure_count += 1
        self.last_failure = time.time()
        if self.state in {"CLOSED", "HALF_OPEN"}:
            if self.failure_count >= self.failure_threshold:
                self.trip()

    def trip(self):
        self.state = "OPEN"
        self.open_since = time.time()
        logger.error(f"[CIRCUIT BREAKER] Tripped to OPEN state at {self.open_since}. Failure threshold reached.")

    def reset(self):
        self.state = "CLOSED"
        self.failure_count = 0
        self.success_count = 0
        self.open_since = 0.0
        logger.info("[CIRCUIT BREAKER] Reset to CLOSED state. Provider connection restored.")

    def attempt_execution(self) -> bool:
        """Determines if requests are allowed to proceed through the breaker."""
        now = time.time()
        if self.state == "OPEN":
            if now - self.open_since > self.recovery_timeout:
                # Cooldown expired -> Transition to HALF_OPEN to probe provider health
                self.state = "HALF_OPEN"
                logger.warning("[CIRCUIT BREAKER] Cooldown expired. Transitioning to HALF_OPEN state.")
                return True
            return False
        return True

    async def execute(self, func: Callable[[], Awaitable[Any]]) -> Any:
        if not self.attempt_execution():
            raise CircuitBreakerOpenException("Circuit breaker is OPEN. Fast failing request.")

        try:
            result = await func()
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise


# Default global breaker pool mapped by provider name
breaker_pool = {
    "whisper": CircuitBreaker(),
    "azure": CircuitBreaker(),
    "deepgram": CircuitBreaker(),
}
