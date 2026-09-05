import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.schemas.requests import SessionCreateRequest
from app.api.v1.schemas.responses import SessionResponse
from app.application.orchestrator import AssessmentOrchestrator
from app.domain.value_objects.enums import SessionStatus

from app.application.scenario_subsystem.planning_engine import AssessmentPlanningEngine
from app.application.scenario_subsystem.pool_manager import ScenarioPoolManager
from app.domain.entities.assessment_blueprint import ScenarioBlueprint
from app.domain.value_objects.enums import DifficultyLevel, ConstructType
from app.application.scenario_subsystem.scenario_dto import ScenarioDTO

router = APIRouter(prefix="/sessions", tags=["Sessions"])


def get_orchestrator(request: Request) -> AssessmentOrchestrator:
    return request.app.state.platform_manager.registry.get_subsystem("AssessmentOrchestrator")


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Assessment Session",
    description="Initializes a new candidate assessment session in INITIALIZED status.",
)
async def create_session(
    req: SessionCreateRequest,
    orch: AssessmentOrchestrator = Depends(get_orchestrator),
) -> SessionResponse:
    session_id = str(uuid.uuid4())

    async with UnitOfWork() as uow:
        # Determine if we need to plan the assessment
        if req.scenario_id in ("PLAN", "AUTO", ""):
            # First create a domain session with a placeholder scenario_id
            domain_session = orch.create_assessment_session(
                candidate_id=req.candidate_id,
                scenario_id="PLAN",
                session_id=session_id,
            )
            # Plan master blueprint
            planner = AssessmentPlanningEngine()
            mb = planner.plan_assessment(candidate_id=req.candidate_id, session_id=session_id)
            
            # Serialize master blueprint to metadata
            mb_dict = {
                "assessment_id": mb.assessment_id,
                "assessment_policy_version": mb.assessment_policy_version,
                "total_scenario_count": mb.total_scenario_count,
                "overall_construct_coverage_plan": mb.overall_construct_coverage_plan,
                "overall_difficulty_progression": [d.value for d in mb.overall_difficulty_progression],
                "overall_domain_diversity_strategy": mb.overall_domain_diversity_strategy,
                "scenario_blueprints": [
                    {
                        "scenario_number": sb.scenario_number,
                        "domain": sb.domain,
                        "difficulty": sb.difficulty.value,
                        "listening_difficulty": sb.listening_difficulty.value,
                        "speaking_focus": sb.speaking_focus,
                        "primary_constructs": [c.value for c in sb.primary_constructs],
                        "secondary_constructs": [c.value for c in sb.secondary_constructs],
                        "narration_length_min": sb.narration_length_min,
                        "narration_length_max": sb.narration_length_max,
                        "expected_speaking_duration_seconds": sb.expected_speaking_duration_seconds,
                        "language_level": sb.language_level,
                        "diversity_constraints": sb.diversity_constraints,
                    }
                    for sb in mb.scenario_blueprints
                ]
            }
            if not domain_session.metadata:
                domain_session.metadata = {}
            domain_session.metadata["master_blueprint"] = mb_dict
            domain_session.metadata["scenarios"] = []
            
            # Reconstruct blueprint for Scenario 1
            sb_dict = mb_dict["scenario_blueprints"][0]
            blueprint = ScenarioBlueprint(
                scenario_number=sb_dict["scenario_number"],
                domain=sb_dict["domain"],
                difficulty=DifficultyLevel(sb_dict["difficulty"]),
                listening_difficulty=DifficultyLevel(sb_dict["listening_difficulty"]),
                speaking_focus=sb_dict["speaking_focus"],
                primary_constructs=[ConstructType(c) for c in sb_dict["primary_constructs"]],
                secondary_constructs=[ConstructType(c) for c in sb_dict["secondary_constructs"]],
                narration_length_min=sb_dict["narration_length_min"],
                narration_length_max=sb_dict["narration_length_max"],
                expected_speaking_duration_seconds=sb_dict["expected_speaking_duration_seconds"],
                language_level=sb_dict["language_level"],
                diversity_constraints=sb_dict.get("diversity_constraints", {})
            )
            
            # Fetch or generate Scenario 1
            pool_manager = ScenarioPoolManager()
            scenario = await pool_manager.get_or_generate_scenario(blueprint, uow.scenarios)
            domain_session.scenario_id = scenario.scenario_id
            domain_session.metadata["scenarios"].append(scenario.scenario_id)
        else:
            domain_session = orch.create_assessment_session(
                candidate_id=req.candidate_id,
                scenario_id=req.scenario_id,
                session_id=session_id,
            )
            scenario = await uow.scenarios.get_by_id(req.scenario_id)
            if not scenario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scenario configuration '{req.scenario_id}' not found.",
                )
            if not domain_session.metadata:
                domain_session.metadata = {}
            domain_session.metadata["scenarios"] = [scenario.scenario_id]
            domain_session.metadata["master_blueprint"] = {
                "assessment_id": f"AST-{session_id}",
                "assessment_policy_version": "1.0",
                "total_scenario_count": 1,
                "overall_construct_coverage_plan": {},
                "overall_difficulty_progression": [scenario.difficulty.value if hasattr(scenario.difficulty, 'value') else str(scenario.difficulty)],
                "overall_domain_diversity_strategy": {},
                "scenario_blueprints": [
                    {
                        "scenario_number": 1,
                        "domain": scenario.title,
                        "difficulty": scenario.difficulty.value if hasattr(scenario.difficulty, 'value') else str(scenario.difficulty),
                        "listening_difficulty": scenario.difficulty.value if hasattr(scenario.difficulty, 'value') else str(scenario.difficulty),
                        "speaking_focus": "Decision",
                        "primary_constructs": [q.target_construct.value if hasattr(q.target_construct, 'value') else str(q.target_construct) for q in scenario.listening_questions],
                        "secondary_constructs": [],
                        "narration_length_min": 60,
                        "narration_length_max": 180,
                        "expected_speaking_duration_seconds": 120,
                        "language_level": "B2",
                        "diversity_constraints": {}
                    }
                ]
            }

        saved = await uow.assessments.save(domain_session)
        return SessionResponse(
            session_id=saved.session_id,
            candidate_id=saved.candidate_id,
            scenario_id=saved.scenario_id,
            status=saved.status.value,
            current_stage=saved.progress.current_stage.value,
            completed_stages=[s.value for s in saved.progress.completed_stages],
            metadata=saved.metadata,
        )


@router.get(
    "/{id}",
    response_model=SessionResponse,
    summary="Get Assessment Session",
    description="Retrieves active session details and current state/stage.",
)
async def get_session(id: str) -> SessionResponse:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{id}' not found.",
            )
        return SessionResponse(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            scenario_id=session.scenario_id,
            status=session.status.value,
            current_stage=session.progress.current_stage.value,
            completed_stages=[s.value for s in session.progress.completed_stages],
            metadata=session.metadata,
        )


@router.post(
    "/{id}/start",
    response_model=SessionResponse,
    summary="Start Session",
    description="Transitions the FSM state of the session from CREATED to DEVICE_CHECK.",
)
async def start_session(
    id: str,
    orch: AssessmentOrchestrator = Depends(get_orchestrator),
) -> SessionResponse:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Synchronize FSM status tracker state
        orch.record_heartbeat(session.session_id)
        await orch.start_assessment(session)
        saved = await uow.assessments.save(session)
        return SessionResponse(
            session_id=saved.session_id,
            candidate_id=saved.candidate_id,
            scenario_id=saved.scenario_id,
            status=saved.status.value,
            current_stage=saved.progress.current_stage.value,
            completed_stages=[s.value for s in saved.progress.completed_stages],
            metadata=saved.metadata,
        )


@router.post(
    "/{id}/pause",
    response_model=SessionResponse,
    summary="Pause Session",
    description="Pauses the active assessment session.",
)
async def pause_session(
    id: str,
    orch: AssessmentOrchestrator = Depends(get_orchestrator),
) -> SessionResponse:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Record heartbeat and transition
        orch.record_heartbeat(session.session_id)
        # Store current active stage to restore on resume
        current_active = session.metadata.get("current_fsm_state", "DEVICE_CHECK")
        session.metadata["last_active_stage"] = current_active

        await orch.pause_assessment(session, reason="User Paused Execution")
        saved = await uow.assessments.save(session)
        return SessionResponse(
            session_id=saved.session_id,
            candidate_id=saved.candidate_id,
            scenario_id=saved.scenario_id,
            status=saved.status.value,
            current_stage=saved.progress.current_stage.value,
            completed_stages=[s.value for s in saved.progress.completed_stages],
            metadata=saved.metadata,
        )


@router.post(
    "/{id}/resume",
    response_model=SessionResponse,
    summary="Resume Session",
    description="Resumes a paused assessment session and restores candidate stage.",
)
async def resume_session(
    id: str,
    orch: AssessmentOrchestrator = Depends(get_orchestrator),
) -> SessionResponse:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Ensure last heartbeat is recorded to prevent instant timeout
        orch.record_heartbeat(session.session_id)
        await orch.resume_assessment(session)
        saved = await uow.assessments.save(session)
        return SessionResponse(
            session_id=saved.session_id,
            candidate_id=saved.candidate_id,
            scenario_id=saved.scenario_id,
            status=saved.status.value,
            current_stage=saved.progress.current_stage.value,
            completed_stages=[s.value for s in saved.progress.completed_stages],
            metadata=saved.metadata,
        )


@router.post(
    "/{id}/complete",
    response_model=SessionResponse,
    summary="Complete Session",
    description="Performs final stage complete of the assessment session lifecycle.",
)
async def complete_session(
    id: str,
    orch: AssessmentOrchestrator = Depends(get_orchestrator),
) -> SessionResponse:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Transition directly to COMPLETED
        session.metadata["current_fsm_state"] = "REPORT_GENERATION"
        await orch.transition_to(session, "COMPLETED", reason="Client requested complete")
        saved = await uow.assessments.save(session)
        return SessionResponse(
            session_id=saved.session_id,
            candidate_id=saved.candidate_id,
            scenario_id=saved.scenario_id,
            status=saved.status.value,
            current_stage=saved.progress.current_stage.value,
            completed_stages=[s.value for s in saved.progress.completed_stages],
            metadata=saved.metadata,
        )


@router.post(
    "/{id}/next-scenario",
    response_model=ScenarioDTO,
    summary="Get or Generate Next Scenario",
    description="Extracts the next planned Scenario Blueprint from the Master Blueprint and returns the materialized Scenario.",
)
async def next_scenario(
    id: str,
) -> ScenarioDTO:
    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if not session.metadata:
            session.metadata = {}

        mb_dict = session.metadata.get("master_blueprint")
        if not mb_dict:
            # Fallback/On-demand plan if session started without planning
            planner = AssessmentPlanningEngine()
            mb = planner.plan_assessment(candidate_id=session.candidate_id, session_id=session.session_id)
            mb_dict = {
                "assessment_id": mb.assessment_id,
                "assessment_policy_version": mb.assessment_policy_version,
                "total_scenario_count": mb.total_scenario_count,
                "overall_construct_coverage_plan": mb.overall_construct_coverage_plan,
                "overall_difficulty_progression": [d.value for d in mb.overall_difficulty_progression],
                "overall_domain_diversity_strategy": mb.overall_domain_diversity_strategy,
                "scenario_blueprints": [
                    {
                        "scenario_number": sb.scenario_number,
                        "domain": sb.domain,
                        "difficulty": sb.difficulty.value,
                        "listening_difficulty": sb.listening_difficulty.value,
                        "speaking_focus": sb.speaking_focus,
                        "primary_constructs": [c.value for c in sb.primary_constructs],
                        "secondary_constructs": [c.value for c in sb.secondary_constructs],
                        "narration_length_min": sb.narration_length_min,
                        "narration_length_max": sb.narration_length_max,
                        "expected_speaking_duration_seconds": sb.expected_speaking_duration_seconds,
                        "language_level": sb.language_level,
                        "diversity_constraints": sb.diversity_constraints,
                    }
                    for sb in mb.scenario_blueprints
                ]
            }
            session.metadata["master_blueprint"] = mb_dict

        from app.domain.entities.candidate_response import SpeakingResponse

        scenarios_played = session.metadata.get("scenarios", [])
        completed_scenarios = session.metadata.get("completed_scenarios", [])
        
        # Advance completed_scenarios when moving from active scenario to next scenario
        if session.scenario_id and session.scenario_id not in ("PLAN", "AUTO", ""):
            if session.metadata.get("has_fetched_first") and session.scenario_id not in completed_scenarios:
                completed_scenarios.append(session.scenario_id)
                session.metadata["completed_scenarios"] = completed_scenarios
            else:
                session.metadata["has_fetched_first"] = True

        # Determine the next scenario index by checking how many scenarios have already been completed
        next_index = len(completed_scenarios)

        if next_index >= mb_dict["total_scenario_count"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All planned scenarios for this assessment session have already been completed."
            )

        if next_index < len(scenarios_played):
            # The scenario for this step was already generated, retrieve and return it
            scenario_id = scenarios_played[next_index]
            scenario = await uow.scenarios.get_by_id(scenario_id)
            if not scenario:
                raise HTTPException(status_code=500, detail="Planned scenario not found in repository")
            
            # Update session scenario_id to match this active scenario
            session.scenario_id = scenario.scenario_id
            await uow.assessments.save(session)
            return ScenarioDTO.from_domain(scenario)

        # Reconstruct blueprint
        sb_dict = mb_dict["scenario_blueprints"][next_index]

        blueprint = ScenarioBlueprint(
            scenario_number=sb_dict["scenario_number"],
            domain=sb_dict["domain"],
            difficulty=DifficultyLevel(sb_dict["difficulty"]),
            listening_difficulty=DifficultyLevel(sb_dict["listening_difficulty"]),
            speaking_focus=sb_dict["speaking_focus"],
            primary_constructs=[ConstructType(c) for c in sb_dict["primary_constructs"]],
            secondary_constructs=[ConstructType(c) for c in sb_dict["secondary_constructs"]],
            narration_length_min=sb_dict["narration_length_min"],
            narration_length_max=sb_dict["narration_length_max"],
            expected_speaking_duration_seconds=sb_dict["expected_speaking_duration_seconds"],
            language_level=sb_dict["language_level"],
            diversity_constraints=sb_dict.get("diversity_constraints", {})
        )

        pool_manager = ScenarioPoolManager()
        scenario = await pool_manager.get_or_generate_scenario(blueprint, uow.scenarios, exclude_ids=scenarios_played)

        # Update active scenario
        session.scenario_id = scenario.scenario_id
        if scenario.scenario_id not in scenarios_played:
            scenarios_played.append(scenario.scenario_id)
        session.metadata["scenarios"] = scenarios_played

        await uow.assessments.save(session)
        
        return ScenarioDTO.from_domain(scenario)

