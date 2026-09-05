import pytest
from app.infrastructure.research_framework import (
    ResearchAnalyticsFramework,
    EventSubscriber,
    ResearchMetricsCollector,
    PsychometricValidationEngine,
    ExperimentManager,
    PlatformMonitoringService,
    AnalyticsRepository,
    ResearchDashboardModel,
)
from app.domain.events.assessment_events import AssessmentStarted, AssessmentCompleted
from app.domain.events.scoring_events import ScoringCompleted


def test_collector_and_subscriber():
    collector = ResearchMetricsCollector()
    subscriber = EventSubscriber()

    ev_start = AssessmentStarted(session_id="SESS-RAVMF-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    ev_comp = AssessmentCompleted(session_id="SESS-RAVMF-001", candidate_id="CAND-01", total_duration_seconds=120)

    collector.process_event(ev_start)
    collector.process_event(ev_comp)

    metrics = collector.collect_metrics()
    assert metrics["total_assessments_started"] == 1
    assert metrics["total_assessments_completed"] == 1
    assert metrics["completion_rate_percentage"] == 100.0


def test_validation_and_monitoring():
    val_engine = PsychometricValidationEngine()
    mon_service = PlatformMonitoringService()

    val_summary = val_engine.validate_psychometrics()
    assert "STABLE" in val_summary.reliability_status
    assert "CALIBRATED" in val_summary.calibration_status

    mon_summary = mon_service.get_monitoring_summary()
    assert mon_summary.health_status == "HEALTHY"
    assert "ScenarioEngine" in mon_summary.subsystem_status


def test_experiment_manager_and_repository():
    exp_mgr = ExperimentManager()
    repo = AnalyticsRepository()

    exps = exp_mgr.get_experiments()
    assert len(exps) >= 1
    assert exps[0].winner == "VARIANT_B"

    dash = ResearchDashboardModel(research_metrics={"test": 1})
    repo.save_snapshot(dash)
    assert repo.get_snapshot(dash.snapshot_id) is not None


@pytest.mark.asyncio
async def test_ravmf_facade_dashboard_generation():
    ravmf = ResearchAnalyticsFramework()

    # Trigger mock domain event observation
    ev_start = AssessmentStarted(session_id="SESS-RAVMF-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    await ravmf.on_event_received(ev_start)

    dashboard = await ravmf.generate_research_dashboard()

    assert dashboard.snapshot_id is not None
    assert "completion_rate_percentage" in dashboard.research_metrics
    assert dashboard.validation_metrics.reliability_status is not None
    assert dashboard.monitoring_metrics.health_status == "HEALTHY"
    assert len(dashboard.experiment_results) >= 1
