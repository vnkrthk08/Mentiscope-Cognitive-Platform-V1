import asyncio
import random
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger("mentiscope.speech.retry")


class TransientProviderError(Exception):
    """Exception class marking transient external speech provider errors that are eligible for retry."""
    pass


class FatalProviderError(Exception):
    """Exception class marking fatal/unrecoverable errors (e.g. Auth, Invalid Format) that must fail immediately."""
    pass


async def execute_with_retry(
    func: Callable[[], Awaitable[Any]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Any:
    """Executes asynchronous callable wrapping retry policies with exponential backoff and jitter."""
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except TransientProviderError as e:
            if attempt == max_retries:
                logger.error(f"Transient error occurred. Max retries ({max_retries}) reached: {str(e)}")
                raise
            
            # Apply backoff with random jitter (+/- 20%)
            jitter = random.uniform(0.8, 1.2)
            sleep_time = delay * backoff_factor * jitter
            logger.warning(
                f"Transient error on attempt {attempt}: {str(e)}. Retrying in {sleep_time:.2f} seconds..."
            )
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
        except FatalProviderError:
            # Re-raise fatal exceptions immediately without retry
            raise
        except Exception as e:
            # Treat generic connection/timeouts as transient errors
            if attempt == max_retries:
                raise
            sleep_time = delay * backoff_factor
            logger.warning(
                f"Unexpected exception {type(e).__name__} on attempt {attempt}. Retrying in {sleep_time:.2f}s..."
            )
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
