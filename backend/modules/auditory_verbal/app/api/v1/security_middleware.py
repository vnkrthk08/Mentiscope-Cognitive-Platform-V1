from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.identity.entities.user import User
from app.infrastructure.identity.jwt_service import JWTService
from app.infrastructure.identity.token_store import token_store

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency retrieving authenticated user using claims validation and blacklist verification."""
    payload = JWTService.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub", "")
    session_id: str = payload.get("session_id", "")

    # Check if session / access token is revoked/blacklisted
    if await token_store.is_jti_blacklisted(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been terminated.",
        )

    async with UnitOfWork() as uow:
        user = await uow.users.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or deleted.",
            )
        return user


oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_optional_current_user(token: str = Depends(oauth2_scheme_optional)) -> Optional[User]:
    """Dependency retrieving authenticated user if token present, otherwise None for guest requests."""
    if not token:
        return None
    try:
        return await get_current_user(token)
    except Exception:
        return None


class RequiresPermission:
    """RBAC validation middleware enforcing specific permission requirements on FastAPI routes."""

    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(self.permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.permission_name}",
            )
        return current_user
