from typing import List
from fastapi import APIRouter, Depends
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.security_middleware import RequiresPermission

router = APIRouter(prefix="/permissions", tags=["Permissions Telemetry"])


@router.get(
    "",
    summary="List Permissions",
    description="Lists all security permissions registered on the platform.",
    dependencies=[Depends(RequiresPermission("platform:manage"))],
)
async def list_permissions():
    async with UnitOfWork() as uow:
        perms = await uow.permissions.list_all()
        return [
            {
                "permission_id": p.permission_id,
                "name": p.name,
                "description": p.description,
            }
            for p in perms
        ]
