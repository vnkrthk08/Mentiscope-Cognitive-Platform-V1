import pytest
import pytest_asyncio
from app.application.followup_subsystem.config import (
    MISSING_THRESHOLD,
    WEAK_THRESHOLD,
    STATUS_MISSING,
    STATUS_WEAK,
    STATUS_SUFFICIENT,
)
from app.application.followup_subsystem.session_state import (
    FollowUpSessionState,
    FollowUpSessionStateManager,
    ConstructCoverageItem,
    EvidenceLogEntry,
)
from app.application.followup_subsystem.adaptive_coverage_analyzer import AdaptiveCoverageAnalyzer
from app.application.followup_subsystem.adaptive_gap_detector import AdaptiveGapDetector
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem


def test_session_state_initialization():
    state = FollowUpSessionState(
        scenario_id="SCEN-001",
        candidate_id="CAND-123",
        primary_constructs=["DECISION_MAKING", "REASONING"],
        secondary_constructs=["COMMUNICATION", "ATTENTION"],
    )
    d = state.to_dict()
    assert d["scenario_id"] == "SCEN-001"
    assert d["candidate_id"] == "CAND-123"
    assert set(d["primary_constructs"]) == {"DECISION_MAKING", "REASONING"}
    assert set(d["secondary_constructs"]) == {"COMMUNICATION", "ATTENTION"}
    assert "DECISION_MAKING" in d["construct_coverage"]
    assert d["construct_coverage"]["DECISION_MAKING"]["status"] == STATUS_MISSING
    assert d["construct_coverage"]["DECISION_MAKING"]["confidence"] == 0.0


def test_coverage_status_thresholds():
    item = ConstructCoverageItem(confidence=0.1)
    item.update_status()
    assert item.status == STATUS_MISSING

    item.confidence = 0.4
    item.update_status()
    assert item.status == STATUS_WEAK

    item.confidence = 0.8
    item.update_status()
    assert item.status == STATUS_SUFFICIENT


def test_adaptive_coverage_analyzer():
    state = FollowUpSessionState(
        scenario_id="SCEN-001",
        candidate_id="CAND-123",
        primary_constructs=["DECISION_MAKING"],
        secondary_constructs=["COMMUNICATION"],
    )

    entry1 = EvidenceLogEntry(
        turn=1,
        source="initial_response",
        claims=["Decided to re-route current limits to 75% for emergency safety"],
        reasoning_shown=["Prevent battery overheating while preserving obstacle climbing"],
    )
    state.evidence_log.append(entry1)

    analyzer = AdaptiveCoverageAnalyzer()
    analyzer.analyze_coverage(state)

    cov = state.construct_coverage
    assert cov["DECISION_MAKING"].confidence >= 0.25
    assert cov["DECISION_MAKING"].status in (STATUS_WEAK, STATUS_SUFFICIENT)
    assert "turn_1" in cov["DECISION_MAKING"].evidence_refs


def test_adaptive_gap_detector():
    state = FollowUpSessionState(
        scenario_id="SCEN-001",
        candidate_id="CAND-123",
        primary_constructs=["DECISION_MAKING", "REASONING"],
        secondary_constructs=["COMMUNICATION", "ATTENTION"],
    )
    state.construct_coverage["DECISION_MAKING"].confidence = 0.75
    state.construct_coverage["DECISION_MAKING"].update_status()

    state.construct_coverage["REASONING"].confidence = 0.10
    state.construct_coverage["REASONING"].update_status()

    state.construct_coverage["COMMUNICATION"].confidence = 0.40
    state.construct_coverage["COMMUNICATION"].update_status()

    state.construct_coverage["ATTENTION"].confidence = 0.0
    state.construct_coverage["ATTENTION"].update_status()

    detector = AdaptiveGapDetector()
    primary_gaps, secondary_gaps = detector.detect_gaps(state)

    # DECISION_MAKING is sufficient (0.75), so REASONING (0.10) is the only primary gap
    assert len(primary_gaps) == 1
    assert primary_gaps[0]["construct"] == "REASONING"

    # Secondary gaps sorted lowest-confidence-first: ATTENTION (0.0), then COMMUNICATION (0.40)
    assert len(secondary_gaps) == 2
    assert secondary_gaps[0]["construct"] == "ATTENTION"
    assert secondary_gaps[1]["construct"] == "COMMUNICATION"


@pytest.mark.asyncio
async def test_shadow_adaptive_pipeline_execution():
    aiis = AdaptiveInterviewIntelligenceSystem()
    result = await aiis._run_shadow_adaptive_pipeline(
        session_id="test_shadow_session_999",
        scenario_title="Robotics Competition Battery Thermal Limit Crisis",
        transcript_text="I decided to re-route current limits to 75% to prevent the battery from overheating beyond 65°C.",
        target_constructs=["DECISION_MAKING", "REASONING", "COMMUNICATION", "ATTENTION"],
        turn_number=1,
        scenario_id="SCEN-001",
        candidate_id="CANDIDATE-001",
    )

    assert result["shadow_pipeline_stage"] == "STAGE_1_2_3_4_5_6_COMPLETE"
    assert "stage5_spec" in result
    assert "state" in result
    assert len(result["state"]["evidence_log"]) == 1
    assert "primary_gaps" in result
    assert "secondary_gaps" in result
