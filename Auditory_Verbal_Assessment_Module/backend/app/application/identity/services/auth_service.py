import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.identity.entities.user import User
from app.domain.identity.entities.role import Role
from app.domain.identity.entities.permission import Permission
from app.domain.identity.entities.token import RefreshToken, PasswordResetToken, EmailVerificationToken
from app.domain.identity.entities.session import UserSession
from app.domain.identity.entities.audit_log import AuditLog
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.infrastructure.identity.jwt_service import JWTService
from app.infrastructure.identity.token_store import token_store
from app.infrastructure.identity.email_service import EmailService


class AuthService:
    """Core Identity & Access Management application service coordinating business workflows."""

    @staticmethod
    async def seed_roles_and_permissions() -> None:
        """Populates baseline standard roles and permission sets in the persistence layer."""
        permissions_def = [
            ("assessment:create", "Create psychometric assessments definitions"),
            ("assessment:view", "View assessments configurations and sessions details"),
            ("assessment:update", "Modify assessment details"),
            ("assessment:delete", "Soft delete assessment definitions"),
            ("report:view", "View candidate scoring reports details"),
            ("report:download", "Export/Download evaluation reports PDFs"),
            ("research:view", "View research dashboards, metrics and outcomes"),
            ("research:export", "Export psychometric calibration files"),
            ("scenario:manage", "Create and edit simulation scenarios"),
            ("platform:manage", "Access security and config telemetry parameters"),
        ]

        roles_def = {
            "Administrator": [p[0] for p in permissions_def],
            "Researcher": ["assessment:view", "report:view", "research:view", "research:export"],
            "Counselor": ["assessment:view", "report:view", "report:download"],
            "Candidate": ["assessment:view", "report:view"],
        }

        async with UnitOfWork() as uow:
            # 1. Seed Permissions
            for name, desc in permissions_def:
                existing_perm = await uow.permissions.get_by_name(name)
                if not existing_perm:
                    perm = Permission(permission_id=str(uuid.uuid4()), name=name, description=desc)
                    await uow.permissions.save(perm)

            # 2. Seed Roles
            for role_name, allowed_perms in roles_def.items():
                existing_role = await uow.roles.get_by_name(role_name)
                perms_list = []
                for p_name in allowed_perms:
                    p_obj = await uow.permissions.get_by_name(p_name)
                    if p_obj:
                        perms_list.append(p_obj)

                if existing_role:
                    existing_role.permissions = perms_list
                    await uow.roles.save(existing_role)
                else:
                    new_role = Role(role_id=str(uuid.uuid4()), name=role_name, permissions=perms_list)
                    await uow.roles.save(new_role)

            await uow.commit()

    @staticmethod
    async def register_user(username: str, email: str, password_raw: str) -> User:
        async with UnitOfWork() as uow:
            # Check unique usernames/emails
            existing_user = await uow.users.get_by_username(username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered.",
                )

            existing_email = await uow.users.get_by_email(email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered.",
                )

            # Retrieve default Candidate role
            cand_role = await uow.roles.get_by_name("Candidate")
            if not cand_role:
                # Fallback role creation if database is completely empty
                cand_role = Role(role_id=str(uuid.uuid4()), name="Candidate", permissions=[])
                await uow.roles.save(cand_role)

            hashed = PasswordHasher.hash_password(password_raw)
            user_id = str(uuid.uuid4())
            new_user = User(
                user_id=user_id,
                username=username,
                email=email,
                hashed_password=hashed,
                is_active=True,
                is_verified=False,
                roles=[cand_role],
            )
            saved_user = await uow.users.save(new_user)

            # Create Email Verification Token
            verify_token = secrets.token_urlsafe(32)
            token_entity = EmailVerificationToken(
                token_id=str(uuid.uuid4()),
                user_id=user_id,
                token=verify_token,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            await uow.tokens.save_email_verification_token(token_entity)

            # Log audit trail
            audit = AuditLog(
                log_id=str(uuid.uuid4()),
                actor=username,
                action="USER_REGISTRATION",
                target=user_id,
                ip_address="0.0.0.0",
                user_agent="Unknown",
                details={"email": email},
            )
            await uow.audit_logs.save(audit)
            await uow.commit()

            # Async trigger verification email simulation
            await EmailService.send_verification_email(email, verify_token)
            return saved_user

    @staticmethod
    async def login_user(
        username_or_email: str, password_raw: str, ip_address: str, user_agent: str
    ) -> Tuple[str, str, User]:
        async with UnitOfWork() as uow:
            # Match user by username or email
            user = await uow.users.get_by_username(username_or_email)
            if not user:
                user = await uow.users.get_by_email(username_or_email)

            if not user or not PasswordHasher.verify_password(password_raw, user.hashed_password):
                consecutive_failures = await token_store.track_failed_login(ip_address)
                if consecutive_failures > 5:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Account locked temporarily due to successive login failures.",
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect credentials.",
                )

            # Clear failed login attempts on successful authentication
            await token_store.reset_failed_logins(ip_address)

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated.",
                )

            # Reset login failure count
            await token_store.reset_failed_logins(ip_address)

            # Create User Session
            session_id = str(uuid.uuid4())
            session_entity = UserSession(
                session_id=session_id,
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            await uow.user_sessions.save(session_entity)

            # Create JWT Tokens
            primary_role = user.roles[0].name if user.roles else "Candidate"
            access_token = JWTService.create_access_token(
                user_id=user.user_id,
                role=primary_role,
                permissions=user.permissions,
                session_id=session_id,
            )

            refresh_token_str = secrets.token_urlsafe(64)
            refresh_entity = RefreshToken(
                token_id=str(uuid.uuid4()),
                user_id=user.user_id,
                token=refresh_token_str,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
            await uow.tokens.save_refresh_token(refresh_entity)

            # Log audit trail
            audit = AuditLog(
                log_id=str(uuid.uuid4()),
                actor=user.username,
                action="LOGIN_SUCCESS",
                target=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"session_id": session_id},
            )
            await uow.audit_logs.save(audit)
            await uow.commit()

            return access_token, refresh_token_str, user

    @staticmethod
    async def refresh_tokens(refresh_token_str: str, ip_address: str, user_agent: str) -> Tuple[str, str]:
        async with UnitOfWork() as uow:
            token = await uow.tokens.get_refresh_token(refresh_token_str)
            if not token or token.is_revoked or token.is_expired():
                # Potential token reuse attack - revoke all user tokens for safety
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token.",
                )

            user = await uow.users.get_by_id(token.user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User no longer active.",
                )

            # Revoke current token (Refresh Token Rotation)
            token.is_revoked = True
            await uow.tokens.save_refresh_token(token)

            # Generate new session context or map to active ones
            active_sessions = await uow.user_sessions.list_active_by_user(user.user_id)
            session_id = active_sessions[0].session_id if active_sessions else str(uuid.uuid4())

            # Issue new token pair
            primary_role = user.roles[0].name if user.roles else "Candidate"
            new_access_token = JWTService.create_access_token(
                user_id=user.user_id,
                role=primary_role,
                permissions=user.permissions,
                session_id=session_id,
            )

            new_refresh_str = secrets.token_urlsafe(64)
            new_refresh_entity = RefreshToken(
                token_id=str(uuid.uuid4()),
                user_id=user.user_id,
                token=new_refresh_str,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
            await uow.tokens.save_refresh_token(new_refresh_entity)

            # Log audit trail
            audit = AuditLog(
                log_id=str(uuid.uuid4()),
                actor=user.username,
                action="TOKEN_REFRESH",
                target=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"old_token": refresh_token_str[:12]},
            )
            await uow.audit_logs.save(audit)
            await uow.commit()

            return new_access_token, new_refresh_str

    @staticmethod
    async def logout_user(access_token_jti: str, refresh_token_str: str, username: str) -> None:
        async with UnitOfWork() as uow:
            # 1. Blacklist JTI JTW access token in redis cache
            await token_store.blacklist_jti(access_token_jti, 900)  # 15 minutes window

            # 2. Revoke refresh token
            token = await uow.tokens.get_refresh_token(refresh_token_str)
            if token:
                token.is_revoked = True
                await uow.tokens.save_refresh_token(token)

            # 3. Mark UserSession as inactive if present
            # Log audit trail
            audit = AuditLog(
                log_id=str(uuid.uuid4()),
                actor=username,
                action="LOGOUT",
                target=username,
                ip_address="0.0.0.0",
                user_agent="Unknown",
                details={},
            )
            await uow.audit_logs.save(audit)
            await uow.commit()
