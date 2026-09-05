import time
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger("mentiscope.prompt.circuit_breaker")


class LLMCircuitBreakerOpenException(Exception):
    pass


class LLMCircuitBreaker:
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

    def reset(self):
        self.state = "CLOSED"
        self.failure_count = 0
        self.success_count = 0
        self.open_since = 0.0

    def attempt_execution(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            if now - self.open_since > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    async def execute(self, func: Callable[[], Awaitable[Any]]) -> Any:
        if not self.attempt_execution():
            raise LLMCircuitBreakerOpenException("LLM Circuit breaker is OPEN. Fast failing request.")

        try:
            result = await func()
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise


# Breaker pool mapped by LLM provider
llm_breaker_pool = {
    "openai": LLMCircuitBreaker(),
    "claude": LLMCircuitBreaker(),
    "gemini": LLMCircuitBreaker(),
    "openrouter": LLMCircuitBreaker(),
    "mock": LLMCircuitBreaker(),
}
