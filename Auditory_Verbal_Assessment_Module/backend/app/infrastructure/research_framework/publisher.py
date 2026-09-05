from app.core.event_bus import event_bus
from app.domain.events.research_events import (
    AnalyticsUpdated,
    ValidationCompleted,
    MonitoringUpdated,
    ExperimentCompleted,
    PlatformHealthUpdated,
    ResearchSnapshotCreated,
    FrameworkCompleted,
    FrameworkFailed,
)


class FrameworkEventPublisher:
    """Helper publishing research framework events to the Event Bus."""

    async def publish_analytics_updated(self, total_assessments: int, completion_rate: float):
        await event_bus.publish("AnalyticsUpdated", AnalyticsUpdated(total_assessments=total_assessments, completion_rate_percentage=completion_rate))

    async def publish_validation_completed(self, rel_status: str, drift_status: str):
        await event_bus.publish("ValidationCompleted", ValidationCompleted(reliability_status=rel_status, drift_status=drift_status))

    async def publish_monitoring_updated(self, overall_health: str, avg_latency: float):
        await event_bus.publish("MonitoringUpdated", MonitoringUpdated(overall_health=overall_health, avg_latency_ms=avg_latency))

    async def publish_experiment_completed(self, exp_id: str, winner: str):
        await event_bus.publish("ExperimentCompleted", ExperimentCompleted(experiment_id=exp_id, winner_variant=winner))

    async def publish_platform_health_updated(self, active_providers: int, system_status: str):
        await event_bus.publish("PlatformHealthUpdated", PlatformHealthUpdated(active_providers=active_providers, system_status=system_status))

    async def publish_snapshot_created(self, snapshot_id: str, count: int):
        await event_bus.publish("ResearchSnapshotCreated", ResearchSnapshotCreated(snapshot_id=snapshot_id, metrics_count=count))

    async def publish_completed(self, snapshot_id: str):
        await event_bus.publish("FrameworkCompleted", FrameworkCompleted(snapshot_id=snapshot_id))

    async def publish_failed(self, reason: str):
        await event_bus.publish("FrameworkFailed", FrameworkFailed(reason=reason))
