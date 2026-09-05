import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.persistence.models.orm_models import AssessmentORM
from app.api.v1.schemas.requests import AssessmentCreateRequest
from app.api.v1.schemas.responses import AssessmentResponse, ProblemDetails

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Assessment Definition",
    description="Registers a new psychometric assessment metadata definition.",
)
async def create_assessment(req: AssessmentCreateRequest) -> AssessmentResponse:
    async with UnitOfWork() as uow:
        orm = AssessmentORM(
            name=req.name,
            description=req.description,
        )
        uow.session.add(orm)
        await uow.commit()

        # Refresh to get ID and dates
        await uow.session.refresh(orm)
        return AssessmentResponse(
            id=str(orm.id),
            name=orm.name,
            description=orm.description,
            version=orm.version,
            created_at=orm.created_at,
        )


@router.get(
    "/{id}",
    response_model=AssessmentResponse,
    summary="Get Assessment Definition",
    description="Retrieves a specific assessment metadata definition by UUID.",
)
async def get_assessment(id: str) -> AssessmentResponse:
    try:
        uid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format")

    async with UnitOfWork() as uow:
        orm = await uow.session.get(AssessmentORM, uid)
        if not orm or orm.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment with ID '{id}' not found.",
            )
        return AssessmentResponse(
            id=str(orm.id),
            name=orm.name,
            description=orm.description,
            version=orm.version,
            created_at=orm.created_at,
        )


@router.get(
    "",
    response_model=List[AssessmentResponse],
    summary="List Assessment Definitions",
    description="Lists all active assessment definitions.",
)
async def list_assessments() -> List[AssessmentResponse]:
    from sqlalchemy import select

    async with UnitOfWork() as uow:
        result = await uow.session.execute(
            select(AssessmentORM).where(AssessmentORM.is_deleted == False)
        )
        return [
            AssessmentResponse(
                id=str(orm.id),
                name=orm.name,
                description=orm.description,
                version=orm.version,
                created_at=orm.created_at,
            )
            for orm in result.scalars().all()
        ]


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Assessment Definition",
    description="Performs soft delete on an assessment definition.",
)
async def delete_assessment(id: str):
    try:
        uid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format")

    async with UnitOfWork() as uow:
        orm = await uow.session.get(AssessmentORM, uid)
        if not orm or orm.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment with ID '{id}' not found.",
            )
        orm.is_deleted = True
        await uow.commit()
