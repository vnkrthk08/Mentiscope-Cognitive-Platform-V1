from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.schemas.requests import ListeningSubmitRequest
from app.api.v1.schemas.responses import ListeningQuestionResponse
from app.domain.entities.candidate_response import ListeningResponse
from app.application.listening_engine import ListeningAssessmentEngine
from app.domain.value_objects.enums import AssessmentStage

router = APIRouter(prefix="/sessions", tags=["Listening Assessment"])


def get_listening_engine(request: Request) -> ListeningAssessmentEngine:
    return request.app.state.platform_manager.registry.get_subsystem("ListeningAssessmentEngine")


@router.get(
    "/{id}/listening",
    response_model=list[ListeningQuestionResponse],
    summary="Get Listening Questions",
    description="Loads all listening multiple-choice questions for the active session's scenario.",
)
async def get_listening_questions(id: str) -> list[ListeningQuestionResponse]:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        scenario = await uow.scenarios.get_by_id(session.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario definition not found")

        return [
            ListeningQuestionResponse(
                question_id=q.question_id,
                prompt=q.prompt,
                options=q.options,
                correct_option_index=q.correct_option_index,
                target_construct=q.target_construct.value,
                difficulty=q.difficulty.value,
                points=q.points,
                max_replays=q.max_replays,
            )
            for q in scenario.listening_questions
        ]


@router.post(
    "/{id}/listening/submit",
    status_code=status.HTTP_200_OK,
    summary="Submit Listening Answer",
    description="Records a candidate multiple choice response for a listening question.",
)
async def submit_listening_answer(
    id: str,
    req: ListeningSubmitRequest,
    engine: ListeningAssessmentEngine = Depends(get_listening_engine),
) -> dict:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        scenario = await uow.scenarios.get_by_id(session.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario definition not found")

        # Instantiate & Append ListeningResponse
        response = ListeningResponse(
            session_id=session.session_id,
            prompt_id=req.question_id,
            selected_option_index=req.selected_option_index,
            response_time_ms=req.response_time_ms,
        )
        session.add_response(response)

        # Transition FSM stage and execute engine if all questions are answered
        answered_q_ids = {r.prompt_id for r in session.responses if isinstance(r, ListeningResponse)}
        all_q_ids = {q.question_id for q in scenario.listening_questions}
        is_complete = all_q_ids.issubset(answered_q_ids)

        if is_complete:
            session.metadata["current_fsm_state"] = "SPEAKING_ASSESSMENT"
            session.progress.current_stage = AssessmentStage.SPEAKING_ASSESSMENT
            if AssessmentStage.LISTENING_ASSESSMENT not in session.progress.completed_stages:
                session.progress.completed_stages.append(AssessmentStage.LISTENING_ASSESSMENT)

            # Execute canonical listening engine to evaluate responses and accuracy
            results = await engine.execute(session, scenario)
            session.metadata["listening_results"] = results
            session.metadata["overall_listening_score"] = results.get("raw_accuracy_percentage", 0.0)
        else:
            results = {
                "session_id": session.session_id,
                "scenario_id": scenario.scenario_id,
                "answered_count": len(answered_q_ids),
                "total_questions": len(all_q_ids),
            }

        # Save session context
        await uow.assessments.save(session)
        await uow.commit()

        return {
            "status": "SUCCESS",
            "message": "Listening response recorded successfully.",
            "stage_results": results,
        }

