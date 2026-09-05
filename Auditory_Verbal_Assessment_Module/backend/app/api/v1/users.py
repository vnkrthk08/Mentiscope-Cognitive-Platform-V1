from fastapi import APIRouter, Depends, HTTPException, status
from app.application.identity.dto import UserDetailResponse, UserProfileUpdateRequest
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get Logged-in User Profile",
    description="Returns verified details, active roles, and authorization permissions mapping for the caller.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserDetailResponse:
    return UserDetailResponse(
        id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        roles=[r.name for r in current_user.roles],
        permissions=current_user.permissions,
    )


@router.put(
    "/me",
    response_model=UserDetailResponse,
    summary="Update User Profile",
    description="Updates caller profile username and email address metadata.",
)
async def update_me(
    req: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> UserDetailResponse:
    async with UnitOfWork() as uow:
        # Check unique username
        if req.username and req.username != current_user.username:
            existing = await uow.users.get_by_username(req.username)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken.",
                )
            current_user.username = req.username

        # Check unique email
        if req.email and req.email != current_user.email:
            existing = await uow.users.get_by_email(req.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken.",
                )
            current_user.email = req.email

        saved = await uow.users.save(current_user)
        await uow.commit()

        return UserDetailResponse(
            id=saved.user_id,
            username=saved.username,
            email=saved.email,
            is_active=saved.is_active,
            is_verified=saved.is_verified,
            roles=[r.name for r in saved.roles],
            permissions=saved.permissions,
        )
