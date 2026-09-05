import pytest
import uuid
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from sqlalchemy.orm.exc import StaleDataError

from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.models import (
    AssessmentSessionORM,
    ScenarioORM,
    BehavioralEvidenceORM,
    ConstructEvaluationORM,
    AssessmentScoreORM,
    AssessmentReportORM,
    PromptAuditORM,
    ResearchSnapshotORM,
    PlatformEventORM,
    TranscriptORM,
)
from app.infrastructure.persistence.repositories import (
    AssessmentRepository,
    ScenarioRepository,
    TranscriptRepository,
    EvidenceRepository,
    ConstructRepository,
    ScoringRepository,
    ReportRepository,
    ResearchRepository,
    PromptRepository,
    PlatformEventRepository,
)
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.entities.evidence import Evidence
from app.domain.entities.assessment_report import AssessmentReport
from app.domain.entities.metric import Metric
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.enums import (
    SessionStatus,
    AssessmentStage,
    ConstructType,
    EvidenceType,
    PolarityType,
    DifficultyLevel,
)
from app.domain.value_objects.confidence_level import ConfidenceLevel
from app.application.construct_engine.models import ConstructEvaluation
from app.application.scoring_engine.models import (
    AssessmentScoreSet,
    ConstructScore,
    CompositeScore,
    AssessmentDecision,
    ReliabilitySummary,
)
from app.infrastructure.research_framework.models import ResearchDashboardModel, ValidationSummary, MonitoringSummary


@pytest.fixture
async def test_db_session():
    """Provides an isolated in-memory SQLite database session for persistence testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_bidirectional_mappers(test_db_session):
    # 1. AssessmentSession Mapper
    session_id = str(uuid.uuid4())
    domain_session = AssessmentSession(
        session_id=session_id,
        candidate_id="CANDIDATE_01",
        scenario_id="SCENARIO_01",
        status=SessionStatus.IN_PROGRESS,
    )
    domain_session.metadata["test_key"] = "test_val"

    from app.infrastructure.persistence.mappers.session_mapper import SessionMapper

    orm_session = SessionMapper.to_orm(domain_session)
    assert str(orm_session.id) == session_id
    assert orm_session.status == "IN_PROGRESS"
    assert orm_session.metadata_json["test_key"] == "test_val"

    mapped_back = SessionMapper.to_domain(orm_session)
    assert mapped_back.session_id == session_id
    assert mapped_back.candidate_id == "CANDIDATE_01"
    assert mapped_back.status == SessionStatus.IN_PROGRESS
    assert mapped_back.metadata["test_key"] == "test_val"


@pytest.mark.asyncio
async def test_unit_of_work_commit_and_rollback(test_db_session):
    # Setup custom UOW factory using the fixture session
    def mock_session_factory():
        return test_db_session

    uow = UnitOfWork(session_factory=mock_session_factory)

    # Validate successful commit
    async with uow:
        session_id = str(uuid.uuid4())
        session = AssessmentSession(
            session_id=session_id,
            candidate_id="CAND_COMMIT",
            scenario_id="SCEN_COMMIT",
            status=SessionStatus.INITIALIZED,
        )
        await uow.assessments.save(session)

    # Verify committed state
    result = await test_db_session.execute(
        select(AssessmentSessionORM).where(AssessmentSessionORM.candidate_id == "CAND_COMMIT")
    )
    orm = result.scalars().first()
    assert orm is not None
    assert str(orm.id) == session_id

    # Validate rollback on error
    try:
        async with uow:
            session_id_error = str(uuid.uuid4())
            session_error = AssessmentSession(
                session_id=session_id_error,
                candidate_id="CAND_ROLLBACK",
                scenario_id="SCEN_ROLLBACK",
                status=SessionStatus.INITIALIZED,
            )
            await uow.assessments.save(session_error)
            raise ValueError("Forced error to trigger rollback")
    except ValueError:
        pass

    # Verify state rolled back
    result_err = await test_db_session.execute(
        select(AssessmentSessionORM).where(AssessmentSessionORM.candidate_id == "CAND_ROLLBACK")
    )
    assert result_err.scalars().first() is None


@pytest.mark.asyncio
async def test_optimistic_locking(test_db_session):
    # Set up entity
    orm = AssessmentSessionORM(
        id=uuid.uuid4(),
        candidate_id="CAND_LOCK",
        scenario_id="SCEN_LOCK",
        status="INITIALIZED",
        current_stage="DEVICE_CHECK",
        completed_stages=[],
        metadata_json={},
    )
    test_db_session.add(orm)
    await test_db_session.commit()

    # Load into two separate sessions/objects
    session_factory = async_sessionmaker(bind=test_db_session.bind, class_=AsyncSession)
    async with session_factory() as s1, session_factory() as s2:
        obj1 = await s1.get(AssessmentSessionORM, orm.id)
        obj2 = await s2.get(AssessmentSessionORM, orm.id)

        assert obj1.version == 1
        assert obj2.version == 1

        # Perform first modification & commit
        obj1.status = "IN_PROGRESS"
        await s1.commit()

        # Perform second modification & commit (should raise StaleDataError or version mismatch)
        obj2.status = "COMPLETED"
        with pytest.raises(StaleDataError):
            await s2.commit()


@pytest.mark.asyncio
async def test_soft_delete_and_indexing(test_db_session):
    orm = AssessmentSessionORM(
        id=uuid.uuid4(),
        candidate_id="CAND_SOFT",
        scenario_id="SCEN_SOFT",
        status="INITIALIZED",
        current_stage="DEVICE_CHECK",
        completed_stages=[],
        metadata_json={},
        is_deleted=True,  # Mark as soft deleted
    )
    test_db_session.add(orm)
    await test_db_session.commit()

    # Repository should respect soft delete filter
    repo = AssessmentRepository(test_db_session)
    loaded = await repo.get_by_id(str(orm.id))
    assert loaded is None

    # Database query direct should still be able to retrieve it
    result = await test_db_session.execute(
        select(AssessmentSessionORM).where(AssessmentSessionORM.id == orm.id)
    )
    direct = result.scalars().first()
    assert direct is not None
    assert direct.is_deleted is True


@pytest.mark.asyncio
async def test_scoring_evidence_and_reports(test_db_session):
    # Setup all engines/repositories
    sc_repo = ScoringRepository(test_db_session)
    ev_repo = EvidenceRepository(test_db_session)
    rep_repo = ReportRepository(test_db_session)
    con_repo = ConstructRepository(test_db_session)

    session_id = str(uuid.uuid4())
    scenario_id = "SCENARIO_PROD"

    # Test Construct Evaluation
    eval_item = ConstructEvaluation(
        evaluation_id=str(uuid.uuid4()),
        construct_name="DECISION_MAKING",
        construct_description="Prioritization metric",
        behavioral_summary="Observed high speed prioritization",
        supporting_evidence_ids=["ev-1"],
        evaluation_narrative="Detailed breakdown",
        evaluation_confidence=0.98,
        prompt_version="1.0",
        model_version="gemini-1.5-pro",
    )
    await con_repo.save_evaluation(session_id, eval_item)
    evals = await con_repo.get_evaluations_by_session_id(session_id)
    assert len(evals) == 1
    assert evals[0].construct_name == "DECISION_MAKING"

    # Test Scoring Persistence
    score_set = AssessmentScoreSet(
        score_set_id=str(uuid.uuid4()),
        session_id=session_id,
        scenario_id=scenario_id,
        construct_scores={
            "DECISION_MAKING": ConstructScore(
                construct="DECISION_MAKING",
                raw_score=4.5,
                normalized_score=90.0,
                weight=1.0,
                confidence=0.95,
                calibration_version="1.0",
                norm_version="1.0",
            )
        },
        composite_scores={},
        reliability_summary=None,
        assessment_decision=None,
        scoring_metadata={},
        pipeline_version="1.0.0",
    )
    await sc_repo.save_score_set(score_set)
    loaded_scores = await sc_repo.get_score_set_by_session_id(session_id)
    assert loaded_scores is not None
    assert loaded_scores.construct_scores["DECISION_MAKING"].normalized_score == 90.0
