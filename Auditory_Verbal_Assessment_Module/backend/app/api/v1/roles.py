from typing import List
from fastapi import APIRouter, Depends
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.security_middleware import RequiresPermission
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/roles", tags=["Roles Configuration"])


@router.get(
    "",
    summary="List Roles",
    description="Lists all security roles and associated permissions mapping.",
    dependencies=[Depends(RequiresPermission("platform:manage"))],
)
async def list_roles():
    async with UnitOfWork() as uow:
        roles = await uow.roles.list_all()
        return [
            {
                "role_id": r.role_id,
                "name": r.name,
                "permissions": [p.name for p in r.permissions],
            }
            for r in roles
        ]
