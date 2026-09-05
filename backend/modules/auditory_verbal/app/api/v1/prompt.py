from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.application.prompt.dto import TranscribeRequest as PromptRequest, TranscribeResponse as PromptResponseDto
from app.application.prompt.services.prompt_orchestration_service import PromptOrchestrationService
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.prompt_service.facade import AIPromptOrchestrationService
from app.api.v1.security_middleware import get_current_user, get_optional_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/prompt", tags=["AI Prompt Orchestration APOS"])


class AdaptiveFollowupRequest(BaseModel):
    scenario_title: str
    transcript_text: str
    target_construct: str
    session_id: Optional[str] = None
    target_constructs: Optional[List[str]] = None


@router.post(
    "/adaptive-followup",
    summary="Generate Adaptive Follow-up Question",
    description="Uses APOS to generate a dynamic follow-up question based on candidate response transcript.",
)
async def generate_adaptive_followup(
    req: AdaptiveFollowupRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    import logging
    logger = logging.getLogger("mentiscope.api.prompt")

    # 1. Retrieve Candidate Session details for Context & Memory
    session_id_str = str(req.session_id) if req.session_id else "default_session"
    conversation_history = ""
    evidence_items = []
    current_assessment_state = "SPEAKING_ASSESSMENT"

    try:
        from sqlalchemy import select, desc
        from app.infrastructure.persistence.models.orm_models import AssessmentSessionORM, BehavioralEvidenceORM
        from app.infrastructure.persistence.mappers.session_mapper import SessionMapper
        from app.domain.entities.candidate_response import SpeakingResponse

        async with UnitOfWork() as uow:
            orm = None
            if req.session_id:
                try:
                    orm = await uow.sessions.get_by_id(req.session_id)
                except Exception:
                    pass
            if not orm and current_user:
                stmt = (
                    select(AssessmentSessionORM)
                    .where(AssessmentSessionORM.candidate_id == current_user.username)
                    .order_by(desc(AssessmentSessionORM.created_at))
                    .limit(1)
                )
                res = await uow.session.execute(stmt)
                orm = res.scalars().first()
            if orm:
                session = SessionMapper.to_domain(orm)
                session_id_str = str(orm.id)
                current_assessment_state = f"Stage: {session.progress.current_stage}, Status: {session.status.value}"
                
                # Retrieve dynamic questions metadata for interviewer turns mapping
                dynamic_questions = session.metadata.get("dynamic_questions", {})
                
                # Fetch scenario metadata to match static instructions
                scenario = await uow.scenarios.get_by_id(session.scenario_id)
                
                history_items = []
                for resp in session.responses:
                    if isinstance(resp, SpeakingResponse) and resp.transcript_text:
                        # Differentiate dynamic follow-up questions from initial static instructions
                        prompt_text = dynamic_questions.get(resp.prompt_id)
                        if not prompt_text and scenario:
                            for p in scenario.speaking_prompts:
                                if p.prompt_id == resp.prompt_id:
                                    prompt_text = p.instructions
                                    break
                        if not prompt_text:
                            prompt_text = f"Prompt ID {resp.prompt_id}"
                        
                        history_items.append(f"Interviewer: '{prompt_text}'")
                        history_items.append(f"Candidate: '{resp.transcript_text}'")
                
                if history_items:
                    conversation_history = "\n".join(history_items)

                # Fetch extracted behavioral evidence collected so far in this session
                stmt_ev = select(BehavioralEvidenceORM).where(BehavioralEvidenceORM.session_id == session_id_str)
                res_ev = await uow.session.execute(stmt_ev)
                evs = res_ev.scalars().all()
                for ev in evs:
                    evidence_items.append(f"- Construct '{ev.construct}': Quote '{ev.quote}' (Indicator: {ev.indicator_description})")
    except Exception as db_err:
        logger.warning(f"Could not retrieve conversation history from database: {db_err}")

    from app.application.followup_subsystem.facade import AdaptiveFollowUpSystem
    followup_sys = AdaptiveFollowUpSystem()

    response = await followup_sys.generate_followup_question(
        scenario_title=req.scenario_title,
        transcript_text=req.transcript_text,
        target_construct=req.target_construct,
        conversation_history=conversation_history,
        current_assessment_state=current_assessment_state,
        behavior_evidence="\n".join(evidence_items) if evidence_items else "[No behavior evidence collected yet]",
        session_id=session_id_str,
    )

    q_text = response.get("follow_up_question") or response.get("question_text", "")
    if response.get("needs_clarification") or response.get("answer_quality") == "INVALID":
        q_text = "I couldn't clearly understand how you would handle the situation. Could you explain your approach in a little more detail?"
    response["question_text"] = q_text

    # 3. Save generated question text to session metadata (using dynamic_questions) for conversational history mapping
    if session_id_str:
        try:
            import uuid
            uuid.UUID(session_id_str)  # Verify valid UUID format
            from app.infrastructure.persistence.mappers.session_mapper import SessionMapper
            async with UnitOfWork() as uow:
                session_orm = await uow.assessments.get_by_id(session_id_str)
                if session_orm:
                    meta = dict(session_orm.metadata_json or {})
                    dq = meta.setdefault("dynamic_questions", {})
                    speaking_responses = [r for r in session_orm.metadata_json.get("responses", []) if r.get("type") == "SPEAKING"]
                    response_count = len(speaking_responses)
                    next_prompt_id = f"S_P{response_count + 1}"
                    dq[next_prompt_id] = q_text
                    session_orm.metadata_json = meta
                    await uow.assessments.save(SessionMapper.to_domain(session_orm))
                    await uow.commit()
                    logger.info(f"[API PROMPT] Saved dynamic question text to session metadata key '{next_prompt_id}'")
        except Exception as meta_err:
            logger.warning(f"Could not save dynamic question to session metadata: {meta_err}")

    return response


@router.post(
    "/adaptive-followup-stream",
    summary="Stream Adaptive Follow-up Question via Server-Sent Events (SSE)",
    description="Emits immediate conversational backchannel bridge followed by deep follow-up question via SSE.",
)
async def generate_adaptive_followup_stream(
    req: AdaptiveFollowupRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    import json
    import logging
    from fastapi.responses import StreamingResponse
    from app.application.followup_subsystem.backchannel_registry import backchannel_registry
    from app.core.config import settings

    logger = logging.getLogger("mentiscope.api.prompt.stream")
    session_id_str = str(req.session_id) if req.session_id else "default_session"

    async def event_generator():
        nonlocal session_id_str
        try:
            # Phase 1: Select and emit immediate conversational backchannel bridge (< 50ms)
            backchannel_sel = backchannel_registry.select_backchannel(
                session_id=session_id_str,
                turn_number=1,
            )
            event_1_payload = {
                "type": "backchannel",
                "text": backchannel_sel.text,
                "category": backchannel_sel.category,
                "session_id": session_id_str,
            }
            yield f"event: backchannel\ndata: {json.dumps(event_1_payload)}\n\n"

            # Phase 2: Retrieve Conversation History & Extracted Evidence from Database
            conversation_history = ""
            evidence_items = []
            current_assessment_state = "SPEAKING_ASSESSMENT"

            try:
                from sqlalchemy import select, desc
                from app.infrastructure.persistence.models.orm_models import AssessmentSessionORM, BehavioralEvidenceORM
                from app.infrastructure.persistence.mappers.session_mapper import SessionMapper
                from app.domain.entities.candidate_response import SpeakingResponse

                async with UnitOfWork() as uow:
                    orm = None
                    if req.session_id:
                        try:
                            orm = await uow.sessions.get_by_id(req.session_id)
                        except Exception:
                            pass
                    if not orm and current_user:
                        stmt = (
                            select(AssessmentSessionORM)
                            .where(AssessmentSessionORM.candidate_id == current_user.username)
                            .order_by(desc(AssessmentSessionORM.created_at))
                            .limit(1)
                        )
                        res = await uow.session.execute(stmt)
                        orm = res.scalars().first()
                    if orm:
                        session = SessionMapper.to_domain(orm)
                        session_id_str = str(orm.id)
                        current_assessment_state = f"Stage: {session.progress.current_stage}, Status: {session.status.value}"
                        dynamic_questions = session.metadata.get("dynamic_questions", {})
                        scenario = await uow.scenarios.get_by_id(session.scenario_id)

                        history_items = []
                        for resp in session.responses:
                            if isinstance(resp, SpeakingResponse) and resp.transcript_text:
                                prompt_text = dynamic_questions.get(resp.prompt_id)
                                if not prompt_text and scenario:
                                    for p in scenario.speaking_prompts:
                                        if p.prompt_id == resp.prompt_id:
                                            prompt_text = p.instructions
                                            break
                                if not prompt_text:
                                    prompt_text = f"Prompt ID {resp.prompt_id}"
                                history_items.append(f"Interviewer: '{prompt_text}'")
                                history_items.append(f"Candidate: '{resp.transcript_text}'")

                        if history_items:
                            conversation_history = "\n".join(history_items)

                        stmt_ev = select(BehavioralEvidenceORM).where(BehavioralEvidenceORM.session_id == session_id_str)
                        res_ev = await uow.session.execute(stmt_ev)
                        evs = res_ev.scalars().all()
                        for ev in evs:
                            evidence_items.append(f"- Construct '{ev.construct}': Quote '{ev.quote}' (Indicator: {ev.indicator_description})")
            except Exception as db_err:
                logger.warning(f"Could not retrieve conversation history from DB for stream: {db_err}")

            # Phase 3: Execute AIIS Follow-Up Engine
            from app.application.followup_subsystem.facade import AdaptiveFollowUpSystem
            followup_sys = AdaptiveFollowUpSystem()

            response = await followup_sys.generate_followup_question(
                scenario_title=req.scenario_title,
                transcript_text=req.transcript_text,
                target_construct=req.target_construct,
                conversation_history=conversation_history,
                current_assessment_state=current_assessment_state,
                behavior_evidence="\n".join(evidence_items) if evidence_items else "[No behavior evidence collected yet]",
                session_id=session_id_str,
            )

            q_text = response.get("follow_up_question") or response.get("question_text", "")
            if response.get("needs_clarification") or response.get("answer_quality") == "INVALID":
                q_text = "I couldn't clearly understand how you would handle the situation. Could you explain your approach in a little more detail?"
            response["question_text"] = q_text

            # Phase 4: Save generated question to DB session metadata
            if session_id_str:
                try:
                    import uuid
                    uuid.UUID(session_id_str)
                    from app.infrastructure.persistence.mappers.session_mapper import SessionMapper
                    async with UnitOfWork() as uow:
                        session_orm = await uow.assessments.get_by_id(session_id_str)
                        if session_orm:
                            meta = dict(session_orm.metadata_json or {})
                            dq = meta.setdefault("dynamic_questions", {})
                            speaking_responses = [r for r in session_orm.metadata_json.get("responses", []) if r.get("type") == "SPEAKING"]
                            response_count = len(speaking_responses)
                            next_prompt_id = f"S_P{response_count + 1}"
                            dq[next_prompt_id] = q_text
                            session_orm.metadata_json = meta
                            await uow.assessments.save(SessionMapper.to_domain(session_orm))
                            await uow.commit()
                except Exception as meta_err:
                    logger.warning(f"Could not save dynamic question to session metadata from stream: {meta_err}")

            # Phase 5: Emit validated follow-up question event
            event_2_payload = {
                "type": "question_ready",
                **response,
            }
            yield f"event: question_ready\ndata: {json.dumps(event_2_payload)}\n\n"

        except Exception as stream_err:
            logger.error(f"[STREAM ERROR] Exception during follow-up stream: {stream_err}")
            error_payload = {
                "type": "error",
                "message": str(stream_err),
            }
            yield f"event: error\ndata: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/execute",
    response_model=PromptResponseDto,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger AI Prompt Execution",
    description="Starts prompt execution for a transcribed audio asset.",
)
async def trigger_prompt(
    req: PromptRequest,
    current_user: User = Depends(get_current_user),
) -> PromptResponseDto:
    exec_id = await PromptOrchestrationService.execute_prompt(
        transcript_id=req.asset_id,
        selection_policy=req.selection_policy,
        candidate_id=current_user.username,
    )
    return PromptResponseDto(job_id=exec_id, status="COMPLETED")


@router.get(
    "/executions/{execution_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Prompt Execution Record",
)
async def get_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        execution = await uow.llm_prompts.get_by_id(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Prompt execution not found.")

        # Ownership validation
        transcript = await uow.speech_transcripts.get_by_id(execution.transcript_id)
        if not transcript or transcript.candidate_id != current_user.username:
            raise HTTPException(status_code=403, detail="Unauthorized execution lookup access.")

        return execution


@router.get(
    "/templates",
    status_code=status.HTTP_200_OK,
    summary="List Registered Templates",
)
async def list_templates(
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        # Require admin privileges to query all registered templates
        return await uow.llm_prompts.list_templates()
