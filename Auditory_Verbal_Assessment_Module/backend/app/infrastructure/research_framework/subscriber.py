from typing import Callable, List, Dict, Any
from app.core.event_bus import event_bus
from app.domain.events.base_event import DomainEvent
from app.core.logging import logger


class EventSubscriber:
    """Subscribes exclusively to domain events on the central Event Bus for non-intrusive observation."""

    def __init__(self):
        self._received_events: List[DomainEvent] = []
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            # Register subscriber on global event bus
            event_bus.subscribe(event_type, self._handle_event)
        self._handlers[event_type].append(handler)

    async def _handle_event(self, event: DomainEvent):
        self._received_events.append(event)
        event_name = type(event).__name__
        logger.info(f"[RAVMF SUBSCRIBER] Observed event '{event_name}'")

        handlers = self._handlers.get(event_name, [])
        for handler in handlers:
            try:
                if callable(handler):
                    await handler(event)
            except Exception as e:
                logger.error(f"[RAVMF SUBSCRIBER] Handler error for '{event_name}': {str(e)}")

    def replay_events(self) -> List[DomainEvent]:
        """Returns copies of all observed events for analytical replay."""
        return list(self._received_events)
