from app.core.event_bus import event_bus
from app.domain.events.scoring_events import (
    ScoringStarted,
    ConstructScoresCalculated,
    NormalizationCompleted,
    CalibrationCompleted,
    WeightingCompleted,
    ReliabilityEstimated,
    DecisionGenerated,
    ScoringValidated,
    ScoringCompleted,
    ScoringFailed,
)


class ScoringEventPublisher:
    """Helper publishing psychometric scoring & decision events to the Event Bus."""

    async def publish_started(self, session_id: str, scenario_id: str):
        await event_bus.publish("ScoringStarted", ScoringStarted(session_id=session_id, scenario_id=scenario_id))

    async def publish_construct_scores_calculated(self, session_id: str, count: int):
        await event_bus.publish("ConstructScoresCalculated", ConstructScoresCalculated(session_id=session_id, construct_count=count))

    async def publish_normalization_completed(self, session_id: str, scale_name: str):
        await event_bus.publish("NormalizationCompleted", NormalizationCompleted(session_id=session_id, scale_name=scale_name))

    async def publish_calibration_completed(self, session_id: str, calibration_version: str):
        await event_bus.publish("CalibrationCompleted", CalibrationCompleted(session_id=session_id, calibration_version=calibration_version))

    async def publish_weighting_completed(self, session_id: str, composite_score: float):
        await event_bus.publish("WeightingCompleted", WeightingCompleted(session_id=session_id, overall_composite_score=composite_score))

    async def publish_reliability_estimated(self, session_id: str, rel_coeff: float):
        await event_bus.publish("ReliabilityEstimated", ReliabilityEstimated(session_id=session_id, reliability_coefficient=rel_coeff))

    async def publish_decision_generated(self, session_id: str, band: str):
        await event_bus.publish("DecisionGenerated", DecisionGenerated(session_id=session_id, decision_band=band))

    async def publish_validated(self, session_id: str, status: str):
        await event_bus.publish("ScoringValidated", ScoringValidated(session_id=session_id, status=status))

    async def publish_completed(self, session_id: str, composite: float, band: str):
        await event_bus.publish("ScoringCompleted", ScoringCompleted(session_id=session_id, composite_score=composite, decision_band=band))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("ScoringFailed", ScoringFailed(session_id=session_id, reason=reason))
