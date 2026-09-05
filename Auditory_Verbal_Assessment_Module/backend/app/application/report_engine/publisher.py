from app.core.event_bus import event_bus
from app.domain.events.report_events import (
    ReportGenerationStarted,
    ExecutiveSummaryGenerated,
    ConstructSectionsGenerated,
    TraceabilityBuilt,
    ReliabilitySectionGenerated,
    ReportValidated,
    ReportCompleted,
    ReportGenerationFailed,
)


class ReportEventPublisher:
    """Helper publishing assessment reporting & explainability events to the Event Bus."""

    async def publish_started(self, session_id: str, scenario_id: str):
        await event_bus.publish("ReportGenerationStarted", ReportGenerationStarted(session_id=session_id, scenario_id=scenario_id))

    async def publish_summary_generated(self, session_id: str, band: str):
        await event_bus.publish("ExecutiveSummaryGenerated", ExecutiveSummaryGenerated(session_id=session_id, decision_band=band))

    async def publish_sections_generated(self, session_id: str, count: int):
        await event_bus.publish("ConstructSectionsGenerated", ConstructSectionsGenerated(session_id=session_id, sections_count=count))

    async def publish_traceability_built(self, session_id: str, count: int):
        await event_bus.publish("TraceabilityBuilt", TraceabilityBuilt(session_id=session_id, trace_links_count=count))

    async def publish_reliability_generated(self, session_id: str, rel_coeff: float):
        await event_bus.publish("ReliabilitySectionGenerated", ReliabilitySectionGenerated(session_id=session_id, reliability_coefficient=rel_coeff))

    async def publish_validated(self, session_id: str, status: str):
        await event_bus.publish("ReportValidated", ReportValidated(session_id=session_id, status=status))

    async def publish_completed(self, session_id: str, report_id: str, band: str):
        await event_bus.publish("ReportCompleted", ReportCompleted(session_id=session_id, report_id=report_id, decision_band=band))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("ReportGenerationFailed", ReportGenerationFailed(session_id=session_id, reason=reason))
