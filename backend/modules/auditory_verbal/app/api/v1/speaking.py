from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.schemas.requests import SpeakingUploadRequest, SpeakingScoreRequest
from app.api.v1.schemas.responses import SpeakingPromptResponse, BehaviouralIndicatorResponse
from app.domain.entities.candidate_response import SpeakingResponse

from app.application.speaking_engine import SpeakingAssessmentEngine
from app.domain.value_objects.enums import AssessmentStage

router = APIRouter(prefix="/sessions", tags=["Speaking Assessment"])


def get_speaking_engine(request: Request) -> SpeakingAssessmentEngine:
    return request.app.state.platform_manager.registry.get_subsystem("SpeakingAssessmentEngine")


@router.get(
    "/{id}/speaking",
    response_model=list[SpeakingPromptResponse],
    summary="Get Speaking Prompts",
    description="Loads all speaking prompts and instructions for the session's active scenario.",
)
async def get_speaking_prompts(id: str) -> list[SpeakingPromptResponse]:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        scenario = await uow.scenarios.get_by_id(session.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario definition not found")

        return [
            SpeakingPromptResponse(
                question_id=p.question_id,
                prompt_id=p.prompt_id,
                stage=p.stage,
                title=p.title,
                instructions=p.instructions,
                objective=p.objective,
                primary_constructs=[c.value for c in p.primary_constructs],
                secondary_constructs=[c.value for c in p.secondary_constructs],
                behavioural_indicators=[
                    BehaviouralIndicatorResponse(
                        indicator_id=ind.indicator_id,
                        name=ind.name,
                        weight=ind.weight,
                        scale=ind.scale,
                        anchors=ind.anchors,
                    )
                    for ind in p.behavioural_indicators
                ],
                max_seconds=float(p.time_limit.max_seconds),
                max_indicator_weighted_score=p.max_indicator_weighted_score,
                target_constructs=[c.value for c in p.target_constructs],
                followup_eligible=p.followup_eligible,
            )
            for p in scenario.speaking_prompts
        ]



@router.post(
    "/{id}/speaking/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload Speaking Response",
    description="Saves voice recording metadata and transcript results for the candidate speaking task.",
)
async def upload_speaking_response(
    id: str,
    req: SpeakingUploadRequest,
    engine: SpeakingAssessmentEngine = Depends(get_speaking_engine),
) -> dict:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        scenario = await uow.scenarios.get_by_id(session.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario definition not found")

        # Instantiate SpeakingResponse
        response = SpeakingResponse(
            session_id=session.session_id,
            prompt_id=req.prompt_id,
            audio_file_url=req.audio_file_url,
            duration_seconds=req.duration_seconds,
            transcript_text=req.transcript_text,
            acoustic_metadata={"format": "wav", "samplerate": 16000},
        )
        session.add_response(response)

        # Transition stage if all prompts submitted
        answered_p_ids = {r.prompt_id for r in session.responses if isinstance(r, SpeakingResponse)}
        all_p_ids = {p.prompt_id for p in scenario.speaking_prompts}

        if all_p_ids.issubset(answered_p_ids):
            session.metadata["current_fsm_state"] = "EVIDENCE_EXTRACTION"
            session.progress.current_stage = AssessmentStage.EVIDENCE_EXTRACTION
            if AssessmentStage.SPEAKING_ASSESSMENT not in session.progress.completed_stages:
                session.progress.completed_stages.append(AssessmentStage.SPEAKING_ASSESSMENT)

        # Save session context
        await uow.assessments.save(session)
        await uow.commit()

        # Execute Speaking Engine logic
        results = await engine.execute(session, scenario)
        return {
            "status": "SUCCESS",
            "message": "Speaking response audio uploaded successfully.",
            "stage_results": results,
        }


@router.post(
    "/{id}/speaking/score",
    status_code=status.HTTP_200_OK,
    summary="Score Speaking Assessment",
    description="Evaluates completed SQ1, SQ2, and SQ3 speaking responses, aggregates construct scores, and returns deterministic candidate report.",
)
async def score_speaking_assessment(
    id: str,
    req: Optional[SpeakingScoreRequest] = None,
    request: Request = None,
) -> dict:
    from app.application.scoring_engine.facade import PsychometricScoringDecisionEngine
    from app.domain.entities.assessment_report import AssessmentReport
    from app.domain.value_objects.enums import SessionStatus

    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Assessment session '{id}' not found")

        # 1. Idempotency Check: Return existing persisted report if already scored
        if session.metadata.get("speaking_assessment_scored") and "candidate_report" in session.metadata:
            return session.metadata["candidate_report"]

        scenario = await uow.scenarios.get_by_id(session.scenario_id)
        if not scenario:
            from app.application.scenario_subsystem.scenario_repository import ScenarioRepository
            repo = ScenarioRepository()
            scenario = repo.get_by_id(session.scenario_id)
            if not scenario:
                raise HTTPException(status_code=404, detail=f"Scenario '{session.scenario_id}' not found")

        # 2. Extract candidate responses from request body or session.responses
        candidate_responses_dict = {}
        if req and req.responses:
            for q_id, item in req.responses.items():
                item_dict = item.model_dump()
                candidate_responses_dict[q_id] = item_dict

                resp_exists = any(
                    isinstance(r, SpeakingResponse) and (r.prompt_id == q_id or r.prompt_id.startswith(f"{q_id}_"))
                    for r in session.responses
                )
                if not resp_exists:
                    audio_url = item.audio_file_url if (item.audio_file_url and item.audio_file_url.strip()) else f"urn:audio:{session.session_id}:{q_id}.webm"
                    session.add_response(
                        SpeakingResponse(
                            session_id=session.session_id,
                            prompt_id=q_id,
                            audio_file_url=audio_url,
                            duration_seconds=item.duration_seconds or 0.0,
                            transcript_text=item.transcript_text or "",
                            acoustic_metadata={"format": "webm", "pause_ratio": item.pause_ratio},
                        )
                    )

        else:
            for r in session.responses:
                if isinstance(r, SpeakingResponse):
                    for prompt in scenario.speaking_prompts:
                        if r.prompt_id in (prompt.prompt_id, prompt.question_id):
                            candidate_responses_dict[prompt.question_id] = {
                                "transcript_text": r.transcript_text,
                                "duration_seconds": r.duration_seconds,
                                "audio_file_url": r.audio_file_url,
                                "pause_ratio": r.acoustic_metadata.get("pause_ratio") if r.acoustic_metadata else None,
                                "words_per_second": r.acoustic_metadata.get("words_per_second") if r.acoustic_metadata else None,
                            }

        # 3. Resolve PSDE Facade
        try:
            psde = request.app.state.platform_manager.registry.get_subsystem("PsychometricScoringDecisionEngine")
        except Exception:
            psde = PsychometricScoringDecisionEngine()

        # 4. Compute Speaking Assessment Scores
        score_set, candidate_report = await psde.compute_speaking_assessment_scores(
            session=session,
            scenario=scenario,
            candidate_responses=candidate_responses_dict,
        )

        # 5. Persist Assessment Scores and Report
        session.metadata["candidate_report"] = candidate_report
        session.metadata["speaking_assessment_scored"] = True
        session.metadata["overall_speaking_score"] = candidate_report.get("overall_speaking_score", 0.0)
        session.metadata["speaking_construct_scores"] = {
            k: v["score"] for k, v in candidate_report.get("demonstrated_construct_scores", {}).items()
        }
        session.metadata["question_breakdown"] = candidate_report.get("question_breakdown", [])
        session.metadata["speaking_reliability_status"] = candidate_report.get("reliability_status", "VALIDATED_SEMANTIC")
        session.status = SessionStatus.COMPLETED

        await uow.assessments.save(session)
        if hasattr(uow, "scores"):
            try:
                await uow.scores.save_score_set(score_set)
            except Exception:
                pass

        report_entity = AssessmentReport(
            report_id=session.session_id,
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            scenario_id=session.scenario_id,
            overall_cognitive_index=candidate_report.get("overall_speaking_score", 0.0),
            listening_metrics=[],
            speaking_metrics=[],
            construct_scores={
                k: v["score"] for k, v in candidate_report.get("demonstrated_construct_scores", {}).items()
            },
            evidence_summary=[],
            recommendations=[candidate_report.get("primary_growth_area", "")],
        )
        await uow.reports.save(report_entity)
        await uow.commit()

        return candidate_report

