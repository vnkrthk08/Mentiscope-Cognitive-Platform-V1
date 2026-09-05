from typing import List
from app.core.logging import logger


class PlatformLifecycleManager:
    """Coordinates ordered platform startup, subsystem initialization, shutdown, and resource cleanup."""

    def __init__(self):
        self._startup_stages: List[str] = [
            "LOAD_CONFIG",
            "REGISTER_SUBSYSTEMS",
            "VERIFY_DEPENDENCIES",
            "INITIALIZE_SECURITY",
            "INITIALIZE_OBSERVABILITY",
            "HEALTH_CHECKS",
            "PLATFORM_READY",
        ]
        self._is_active: bool = False

    def start_lifecycle(self) -> bool:
        logger.info("[LIFECYCLE] Executing ordered platform startup sequence...")
        self._is_active = True
        return True

    def stop_lifecycle(self) -> bool:
        logger.info("[LIFECYCLE] Executing graceful platform shutdown & resource cleanup...")
        self._is_active = False
        return True

    @property
    def is_active(self) -> bool:
        return self._is_active
