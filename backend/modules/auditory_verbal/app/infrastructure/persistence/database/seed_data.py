"""
Academic Seed Generator for Mentiscope Auditory & Audio Personality Construct.

Populates PostgreSQL database with realistic sample accounts, assessment scenarios,
sessions, transcripts, evidence, construct evaluations, reports, research datasets, and calibration batches.
"""
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import SecurityUtils
from app.infrastructure.persistence.models.orm_models import (
    AssessmentORM,
    AssessmentSessionORM,
    ScenarioORM,
    TranscriptORM,
    BehavioralEvidenceORM,
    ConstructEvaluationORM,
    AssessmentScoreORM,
    AssessmentReportORM,
    ResearchSnapshotORM,
)

logger = logging.getLogger(__name__)


async def seed_academic_dataset(db: AsyncSession) -> None:
    """Executes full academic database seed routine."""
    logger.info("Starting database seed routine...")

    # 1. Seed Scenarios from Expert 50-Scenario Repository
    from app.application.scenario_subsystem.scenario_repository import ScenarioRepository as ExpertScenarioRepository
    expert_repo = ExpertScenarioRepository()
    all_expert_scenarios = expert_repo.list_all_scenarios()

    for domain_sc in all_expert_scenarios:
        existing_res = await db.execute(select(ScenarioORM).where(ScenarioORM.id == domain_sc.scenario_id))
        existing_orm = existing_res.scalar_one_or_none()

        lq_dict_list = [
            {
                "question_id": q.question_id,
                "prompt": q.prompt,
                "question_text": q.prompt,
                "options": q.options,
                "correct_option_index": q.correct_option_index,
                "target_construct": q.target_construct.value if hasattr(q.target_construct, 'value') else str(q.target_construct),
                "secondary_constructs": [c.value if hasattr(c, 'value') else str(c) for c in getattr(q, 'secondary_constructs', [])],
                "question_type": getattr(q, 'question_type', 'Detail'),
                "cognitive_objective": getattr(q, 'cognitive_objective', ''),
                "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                "expected_evidence": getattr(q, 'expected_evidence', {}),
                "weight": getattr(q, 'weight', 1.0),
                "points": q.points,
                "max_replays": q.max_replays,
            }
            for q in domain_sc.listening_questions
        ]

        if existing_orm:
            existing_orm.listening_questions = lq_dict_list
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(existing_orm, "listening_questions")
            db.add(existing_orm)
        else:
            sc_dict = {
                "id": domain_sc.scenario_id,
                "title": domain_sc.title,
                "narrative": domain_sc.narrative,
                "audio_asset": {
                    "asset_id": f"AUD-{domain_sc.scenario_id}",
                    "file_name": f"{domain_sc.scenario_id}.mp3",
                    "duration_seconds": domain_sc.audio_asset.duration_seconds,
                    "url": domain_sc.audio_asset.url,
                },
                "listening_questions": lq_dict_list,
                "speaking_prompts": [
                    {
                        "prompt_id": p.prompt_id,
                        "prompt_text": p.instructions,
                        "target_constructs": [c.value for c in p.target_constructs],
                        "min_duration_seconds": getattr(p.time_limit, 'min_seconds', 30),
                        "max_duration_seconds": p.time_limit.max_seconds,
                    }
                    for p in domain_sc.speaking_prompts
                ],
                "construct_mappings": [c.value for c in domain_sc.construct_mappings],
            }
            scenario_orm = ScenarioORM(**sc_dict)
            db.add(scenario_orm)

    await db.commit()
    logger.info("50 Class 10 scenarios seeded successfully.")

    # 2. Seed Assessment Catalog
    existing_assessment = await db.execute(select(AssessmentORM).where(AssessmentORM.name == "Auditory & Audio Personality Construct"))
    if not existing_assessment.scalar_one_or_none():
        assessment_orm = AssessmentORM(
            name="Auditory & Audio Personality Construct",
            description="Production assessment evaluating cognitive and psychological constructs through listening comprehension and spoken responses.",
        )
        db.add(assessment_orm)
        await db.commit()

    # 3. Seed Sample Session & Downstream Artifacts
    sample_session_id = "SESS-SEED-0001"
    existing_session = await db.execute(
        select(AssessmentSessionORM).where(AssessmentSessionORM.candidate_id == "CAND-2026-8841")
    )
    if not existing_session.scalar_one_or_none():
        session_orm = AssessmentSessionORM(
            id=uuid.uuid4(),
            candidate_id="CAND-2026-8841",
            scenario_id="SCEN-AUD-001",
            status="COMPLETED",
            current_stage="COMPLETED",
            completed_stages=[
                "DEVICE_CHECK", "INSTRUCTIONS", "PRACTICE",
                "SCENARIO_PRESENTATION", "LISTENING", "SPEAKING",
                "EVIDENCE_PROCESSING", "SCORING", "REPORT_GENERATION", "COMPLETED"
            ],
            metadata_json={"current_fsm_state": "COMPLETED", "completion_percentage": 100.0},
        )
        db.add(session_orm)
        await db.commit()

        # Transcript
        transcript_orm = TranscriptORM(
            session_id=sample_session_id,
            prompt_id="P1",
            transcript_text="I observed that habitat fragmentation caused local bird species to decline. Creating green corridors between parks would restore migration routes and improve biodiversity.",
            confidence_score=0.96,
            is_final=True,
        )
        db.add(transcript_orm)

        # Evidence
        evidence_1 = BehavioralEvidenceORM(
            session_id=sample_session_id,
            prompt_id="P1",
            construct="Investigative (RIASEC)",
            quote="Creating green corridors between parks would restore migration routes.",
            indicator_description="Proposes systematic structural interventions based on observed ecological evidence.",
            confidence=0.95,
            polarity="POSITIVE",
            evidence_type="VERBATIM_QUOTE",
        )
        evidence_2 = BehavioralEvidenceORM(
            session_id=sample_session_id,
            prompt_id="P1",
            construct="Auditory Processing (Ga)",
            quote="I observed that habitat fragmentation caused local bird species to decline.",
            indicator_description="Accurately recalled key ecological mechanisms presented in the audio passage.",
            confidence=0.94,
            polarity="POSITIVE",
            evidence_type="VERBATIM_QUOTE",
        )
        db.add_all([evidence_1, evidence_2])

        # Construct Evaluation
        evaluation_orm = ConstructEvaluationORM(
            session_id=sample_session_id,
            construct_name="Investigative (RIASEC)",
            construct_description="Preference for analytical, scientific, and evidence-driven problem solving.",
            behavioral_summary="Candidate demonstrated strong analytical reasoning and evidence synthesis in verbal response.",
            supporting_evidence_ids=[],
            evaluation_narrative="Candidate articulated clear causal relationships between urban expansion and habitat loss, proposing green corridors as an evidence-backed intervention.",
            evaluation_confidence=0.95,
            prompt_version="1.0.0",
            model_version="gemini-1.5-pro",
        )
        db.add(evaluation_orm)

        # Score
        score_orm = AssessmentScoreORM(
            session_id=sample_session_id,
            scenario_id="SCEN-AUD-001",
            construct_scores={
                "Auditory Processing (Ga)": 8.5,
                "Comprehension-Knowledge (Gc)": 8.2,
                "Fluid Reasoning (Gf)": 8.0,
                "Investigative (RIASEC)": 8.8,
                "Openness (OCEAN)": 8.6,
                "Emotional Resilience": 8.3,
            },
            composite_scores={
                "CHC Cognitive Index": 8.23,
                "RIASEC Dominant": "Investigative",
                "OCEAN High Dimension": "Openness",
            },
            reliability_summary={"overall_reliability": 0.92, "confidence_interval": "[7.9, 8.6]"},
            assessment_decision={"category": "HIGH_COMPETENCY", "summary": "Recommended for advanced analytical stream."},
            scoring_metadata={"version": "1.0.0"},
            pipeline_version="1.0.0",
        )
        db.add(score_orm)

        # Report
        report_orm = AssessmentReportORM(
            session_id=sample_session_id,
            candidate_id="CAND-2026-8841",
            scenario_id="SCEN-AUD-001",
            overall_cognitive_index=8.45,
            listening_metrics=[{"question_id": "Q1", "score": 1.0}, {"question_id": "Q2", "score": 1.0}],
            speaking_metrics=[{"prompt_id": "P1", "fluency": 8.5, "coherence": 8.6}],
            construct_scores={"Auditory Processing": 8.5, "Investigative": 8.8, "Openness": 8.6},
            evidence_summary=[{"construct": "Investigative", "quote": "Creating green corridors..."}],
            recommendations=[
                "Demonstrates strong analytical listening and evidence-based verbal reasoning.",
                "Well-suited for scientific research and structured problem-solving roles.",
            ],
            generated_at=datetime.now(timezone.utc),
        )
        db.add(report_orm)

        # Research Snapshot
        snapshot_orm = ResearchSnapshotORM(
            research_metrics={"total_datasets": 3, "total_reviews": 12},
            analytics_metrics={"total_assessments": 45, "completion_rate": 95.5},
            validation_metrics={"inter_rater_rmse": 0.35, "expert_agreement_rate": 0.91},
            monitoring_metrics={"system_uptime": 99.9, "avg_latency_ms": 120},
            experiment_results=[{"experiment": "v1_vs_v2_prompt", "winner": "v2"}],
            platform_metadata={"version": "1.0.0", "environment": "academic_production"},
        )
        db.add(snapshot_orm)

        await db.commit()
        logger.info("Sample session and research artifacts seeded successfully.")

    logger.info("Database seed routine complete!")
