import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.identity.entities.user import User
from app.domain.identity.entities.role import Role
from app.domain.identity.entities.permission import Permission
from app.domain.identity.entities.token import RefreshToken, PasswordResetToken, EmailVerificationToken
from app.domain.identity.entities.session import UserSession
from app.domain.identity.entities.audit_log import AuditLog

from app.infrastructure.identity.orm_models import (
    UserORM,
    RoleORM,
    PermissionORM,
    RefreshTokenORM,
    UserSessionORM,
    PasswordResetTokenORM,
    EmailVerificationTokenORM,
    AuditLogORM,
)


class IdentityMapper:
    @staticmethod
    def permission_to_domain(orm: PermissionORM) -> Permission:
        return Permission(
            permission_id=str(orm.id),
            name=orm.name,
            description=orm.description,
        )

    @staticmethod
    def role_to_domain(orm: RoleORM) -> Role:
        return Role(
            role_id=str(orm.id),
            name=orm.name,
            permissions=[IdentityMapper.permission_to_domain(p) for p in orm.permissions],
        )

    @staticmethod
    def user_to_domain(orm: UserORM) -> User:
        return User(
            user_id=str(orm.id),
            username=orm.username,
            email=orm.email,
            hashed_password=orm.hashed_password,
            is_active=orm.is_active,
            is_verified=orm.is_verified,
            roles=[IdentityMapper.role_to_domain(r) for r in orm.roles],
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def refresh_token_to_domain(orm: RefreshTokenORM) -> RefreshToken:
        return RefreshToken(
            token_id=str(orm.id),
            user_id=str(orm.user_id),
            token=orm.token,
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            is_revoked=orm.is_revoked,
        )

    @staticmethod
    def user_session_to_domain(orm: UserSessionORM) -> UserSession:
        return UserSession(
            session_id=str(orm.id),
            user_id=str(orm.user_id),
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            created_at=orm.created_at,
            last_active_at=orm.last_active_at,
            is_active=orm.is_active,
        )

    @staticmethod
    def audit_log_to_domain(orm: AuditLogORM) -> AuditLog:
        return AuditLog(
            log_id=str(orm.id),
            actor=orm.actor,
            action=orm.action,
            target=orm.target,
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            details=orm.details,
            timestamp=orm.timestamp,
        )


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            return None
        orm = await self.session.get(UserORM, uid)
        return IdentityMapper.user_to_domain(orm) if orm else None

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserORM).where(UserORM.username == username)
        )
        orm = result.scalars().first()
        return IdentityMapper.user_to_domain(orm) if orm else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm = result.scalars().first()
        return IdentityMapper.user_to_domain(orm) if orm else None

    async def save(self, user: User) -> User:
        uid = uuid.UUID(user.user_id)
        existing = await self.session.get(UserORM, uid)

        # Retrieve roles
        role_ids = [uuid.UUID(r.role_id) for r in user.roles]
        role_orms = []
        if role_ids:
            res_roles = await self.session.execute(
                select(RoleORM).where(RoleORM.id.in_(role_ids))
            )
            role_orms = list(res_roles.scalars().all())

        if existing:
            existing.username = user.username
            existing.email = user.email
            existing.hashed_password = user.hashed_password
            existing.is_active = user.is_active
            existing.is_verified = user.is_verified
            existing.updated_at = datetime.now(timezone.utc)
            existing.roles = role_orms
            orm = existing
        else:
            orm = UserORM(
                id=uid,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=role_orms,
            )
            self.session.add(orm)

        await self.session.flush()
        return IdentityMapper.user_to_domain(orm)


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.session.execute(
            select(RoleORM).where(RoleORM.name == name)
        )
        orm = result.scalars().first()
        return IdentityMapper.role_to_domain(orm) if orm else None

    async def list_all(self) -> List[Role]:
        result = await self.session.execute(select(RoleORM))
        return [IdentityMapper.role_to_domain(orm) for orm in result.scalars().all()]

    async def save(self, role: Role) -> Role:
        rid = uuid.UUID(role.role_id)
        existing = await self.session.get(RoleORM, rid)

        # Retrieve permissions
        perm_names = [p.name for p in role.permissions]
        perm_orms = []
        if perm_names:
            res_perms = await self.session.execute(
                select(PermissionORM).where(PermissionORM.name.in_(perm_names))
            )
            perm_orms = list(res_perms.scalars().all())

        if existing:
            existing.name = role.name
            existing.permissions = perm_orms
            orm = existing
        else:
            orm = RoleORM(id=rid, name=role.name, permissions=perm_orms)
            self.session.add(orm)

        await self.session.flush()
        return IdentityMapper.role_to_domain(orm)


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Permission]:
        result = await self.session.execute(
            select(PermissionORM).where(PermissionORM.name == name)
        )
        orm = result.scalars().first()
        return IdentityMapper.permission_to_domain(orm) if orm else None

    async def list_all(self) -> List[Permission]:
        result = await self.session.execute(select(PermissionORM))
        return [IdentityMapper.permission_to_domain(orm) for orm in result.scalars().all()]

    async def save(self, permission: Permission) -> Permission:
        pid = uuid.UUID(permission.permission_id)
        existing = await self.session.get(PermissionORM, pid)

        if existing:
            existing.name = permission.name
            existing.description = permission.description
            orm = existing
        else:
            orm = PermissionORM(
                id=pid, name=permission.name, description=permission.description
            )
            self.session.add(orm)

        await self.session.flush()
        return IdentityMapper.permission_to_domain(orm)


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_refresh_token(self, token: RefreshToken) -> RefreshToken:
        tid = uuid.UUID(token.token_id)
        existing = await self.session.get(RefreshTokenORM, tid)
        if existing:
            existing.is_revoked = token.is_revoked
            orm = existing
        else:
            orm = RefreshTokenORM(
                id=tid,
                user_id=uuid.UUID(token.user_id),
                token=token.token,
                expires_at=token.expires_at,
                created_at=token.created_at,
                is_revoked=token.is_revoked,
            )
            self.session.add(orm)
        await self.session.flush()
        return IdentityMapper.refresh_token_to_domain(orm)

    async def get_refresh_token(self, token_str: str) -> Optional[RefreshToken]:
        result = await self.session.execute(
            select(RefreshTokenORM).where(RefreshTokenORM.token == token_str)
        )
        orm = result.scalars().first()
        return IdentityMapper.refresh_token_to_domain(orm) if orm else None

    async def save_password_reset_token(self, token: PasswordResetToken):
        orm = PasswordResetTokenORM(
            id=uuid.UUID(token.token_id),
            user_id=uuid.UUID(token.user_id),
            token=token.token,
            expires_at=token.expires_at,
            created_at=token.created_at,
            is_used=token.is_used,
        )
        self.session.add(orm)
        await self.session.flush()

    async def get_password_reset_token(self, token_str: str) -> Optional[PasswordResetToken]:
        result = await self.session.execute(
            select(PasswordResetTokenORM).where(PasswordResetTokenORM.token == token_str)
        )
        orm = result.scalars().first()
        if not orm:
            return None
        return PasswordResetToken(
            token_id=str(orm.id),
            user_id=str(orm.user_id),
            token=orm.token,
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            is_used=orm.is_used,
        )

    async def save_email_verification_token(self, token: EmailVerificationToken):
        orm = EmailVerificationTokenORM(
            id=uuid.UUID(token.token_id),
            user_id=uuid.UUID(token.user_id),
            token=token.token,
            expires_at=token.expires_at,
            created_at=token.created_at,
            is_used=token.is_used,
        )
        self.session.add(orm)
        await self.session.flush()

    async def get_email_verification_token(self, token_str: str) -> Optional[EmailVerificationToken]:
        result = await self.session.execute(
            select(EmailVerificationTokenORM).where(EmailVerificationTokenORM.token == token_str)
        )
        orm = result.scalars().first()
        if not orm:
            return None
        return EmailVerificationToken(
            token_id=str(orm.id),
            user_id=str(orm.user_id),
            token=orm.token,
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            is_used=orm.is_used,
        )


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user_session: UserSession) -> UserSession:
        sid = uuid.UUID(user_session.session_id)
        existing = await self.session.get(UserSessionORM, sid)
        if existing:
            existing.last_active_at = user_session.last_active_at
            existing.is_active = user_session.is_active
            orm = existing
        else:
            orm = UserSessionORM(
                id=sid,
                user_id=uuid.UUID(user_session.user_id),
                ip_address=user_session.ip_address,
                user_agent=user_session.user_agent,
                created_at=user_session.created_at,
                last_active_at=user_session.last_active_at,
                is_active=user_session.is_active,
            )
            self.session.add(orm)
        await self.session.flush()
        return IdentityMapper.user_session_to_domain(orm)

    async def get_by_id(self, session_id: str) -> Optional[UserSession]:
        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            return None
        orm = await self.session.get(UserSessionORM, sid)
        return IdentityMapper.user_session_to_domain(orm) if orm else None

    async def list_active_by_user(self, user_id: str) -> List[UserSession]:
        result = await self.session.execute(
            select(UserSessionORM).where(
                UserSessionORM.user_id == uuid.UUID(user_id), UserSessionORM.is_active == True
            )
        )
        return [IdentityMapper.user_session_to_domain(orm) for orm in result.scalars().all()]


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, log: AuditLog) -> AuditLog:
        orm = AuditLogORM(
            id=uuid.UUID(log.log_id),
            actor=log.actor,
            action=log.action,
            target=log.target,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            details=log.details,
            timestamp=log.timestamp,
        )
        self.session.add(orm)
        await self.session.flush()
        return IdentityMapper.audit_log_to_domain(orm)
