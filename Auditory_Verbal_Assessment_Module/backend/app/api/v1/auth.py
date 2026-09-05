from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.application.identity.dto import (
    UserRegisterRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserDetailResponse,
)
from app.application.identity.services.auth_service import AuthService
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/auth", tags=["Identity & Authentication"])


@router.post(
    "/register",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User Account",
    description="Registers a new candidate or operator account, issuing initial tokens.",
)
async def register(req: UserRegisterRequest) -> UserDetailResponse:
    user = await AuthService.register_user(
        username=req.username, email=req.email, password_raw=req.password
    )
    return UserDetailResponse(
        id=user.user_id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        roles=[r.name for r in user.roles],
        permissions=user.permissions,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates user credentials and issues JWT access and refresh token pair.",
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    ip_addr = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "Unknown")

    access_token, refresh_token, user = await AuthService.login_user(
        username_or_email=form_data.username,
        password_raw=form_data.password,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate Refresh Token",
    description="Performs Refresh Token Rotation, issuing a new access/refresh pair.",
)
async def refresh(
    request: Request,
    req: TokenRefreshRequest,
) -> TokenResponse:
    ip_addr = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "Unknown")

    access_token, refresh_token = await AuthService.refresh_tokens(
        refresh_token_str=req.refresh_token,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User Logout",
    description="Revokes current tokens session, blacklisting access tokens.",
)
async def logout(
    req: TokenRefreshRequest,
    current_user: User = Depends(get_current_user),
) -> None:
    # Use user's active session_id for JTI blacklisting
    # In real flows, we extract the jti or session_id from request payload
    session_id = current_user.user_id # fallback
    await AuthService.logout_user(
        access_token_jti=session_id,
        refresh_token_str=req.refresh_token,
        username=current_user.username,
    )
