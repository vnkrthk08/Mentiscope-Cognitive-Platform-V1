from typing import Any, Callable, Dict, List
import asyncio
from app.core.logging import logger


class DomainEventPublisher:
    """In-memory domain event bus skeleton for async background processing of telemetry, research logging, and audit trails."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler '{handler.__name__}' to domain event '{event_type}'")

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        logger.info(f"[EVENT BUS] Publishing event '{event_type}'")
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                logger.error(f"Error executing event handler '{handler.__name__}' for '{event_type}': {str(e)}")


# Global singleton instance
event_bus = DomainEventPublisher()
