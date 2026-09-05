from app.core.event_bus import event_bus
from app.domain.events.platform_events import (
    PlatformStarting,
    PlatformStarted,
    PlatformStopping,
    PlatformStopped,
    HealthCheckCompleted,
    SubsystemRegistered,
    ConfigurationValidated,
    SecurityValidated,
    ObservabilityInitialized,
    PlatformReady,
    PlatformFailed,
)


class PlatformEventPublisher:
    """Helper publishing platform lifecycle and operational events to the Event Bus."""

    async def publish_starting(self, env: str):
        await event_bus.publish("PlatformStarting", PlatformStarting(environment=env))

    async def publish_started(self, count: int):
        await event_bus.publish("PlatformStarted", PlatformStarted(registered_subsystems_count=count))

    async def publish_stopping(self, reason: str):
        await event_bus.publish("PlatformStopping", PlatformStopping(reason=reason))

    async def publish_stopped(self, status: str):
        await event_bus.publish("PlatformStopped", PlatformStopped(status=status))

    async def publish_health_completed(self, health: str):
        await event_bus.publish("HealthCheckCompleted", HealthCheckCompleted(overall_health=health))

    async def publish_subsystem_registered(self, name: str, version: str):
        await event_bus.publish("SubsystemRegistered", SubsystemRegistered(subsystem_name=name, version=version))

    async def publish_config_validated(self, summary: str):
        await event_bus.publish("ConfigurationValidated", ConfigurationValidated(config_summary=summary))

    async def publish_security_validated(self, status: str):
        await event_bus.publish("SecurityValidated", SecurityValidated(security_status=status))

    async def publish_observability_initialized(self, active: bool):
        await event_bus.publish("ObservabilityInitialized", ObservabilityInitialized(correlation_id_active=active))

    async def publish_ready(self, version: str):
        await event_bus.publish("PlatformReady", PlatformReady(platform_version=version))

    async def publish_failed(self, reason: str):
        await event_bus.publish("PlatformFailed", PlatformFailed(reason=reason))
