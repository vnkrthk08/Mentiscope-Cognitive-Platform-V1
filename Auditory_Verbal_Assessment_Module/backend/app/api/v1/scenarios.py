from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.entities.scenario import Scenario
from app.application.scenario_subsystem.scenario_dto import ScenarioDTO

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])



from app.application.scenario_subsystem.scenario_repository import ScenarioRepository as ExpertScenarioRepository
expert_repo = ExpertScenarioRepository()


@router.get(
    "/{id}",
    summary="Get Scenario Definition",
    description="Loads a scenario config definition details by ID.",
)
async def get_scenario(id: str):
    async with UnitOfWork() as uow:
        scenario = await uow.scenarios.get_by_id(id)
        if not scenario:
            scenario = expert_repo.get_by_id(id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with ID '{id}' not found.",
            )
        # Convert to serialized DTO response
        dto = ScenarioDTO.from_domain(scenario)
        return dto.model_dump()



@router.get(
    "",
    summary="List Scenarios",
    description="Retrieves a list of all scenario configurations.",
)
async def list_scenarios():
    async with UnitOfWork() as uow:
        scenarios = await uow.scenarios.list_all()
        if not scenarios:
            scenarios = expert_repo.list_all_scenarios()
        return [
            {
                "scenario_id": s.scenario_id,
                "title": s.title,
                "difficulty": s.difficulty.value,
                "construct_mappings": [c.value for c in s.construct_mappings],
            }
            for s in scenarios
        ]
