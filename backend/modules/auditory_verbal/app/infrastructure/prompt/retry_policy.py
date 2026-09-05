import asyncio
import random
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger("mentiscope.prompt.retry")


class TransientLLMError(Exception):
    pass


class FatalLLMError(Exception):
    pass


async def execute_with_retry(
    func: Callable[[], Awaitable[Any]],
    max_retries: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
) -> Any:
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except TransientLLMError as e:
            if attempt == max_retries:
                raise
            jitter = random.uniform(0.8, 1.2)
            sleep_time = delay * backoff_factor * jitter
            logger.warning(f"Transient LLM failure on attempt {attempt}: {str(e)}. Retrying in {sleep_time:.2f}s...")
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
        except FatalLLMError:
            raise
        except Exception as e:
            if attempt == max_retries:
                raise
            sleep_time = delay * backoff_factor
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
