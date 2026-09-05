"""ConfigurationManagerService — Manages versioned environment configuration profiles."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.operations.entities.configuration_profile import ConfigurationProfile


class ConfigurationManagerService:
    """Manages environment profiles, versioning, runtime validation, and history."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_profile(self, profile_name: str = "production") -> ConfigurationProfile:
        """Fetches active configuration profile or constructs default if none stored."""
        from app.infrastructure.operations.repositories import ConfigurationProfileRepository
        repo = ConfigurationProfileRepository(self._session)
        profile = await repo.get_active_profile(profile_name)
        if profile:
            return profile

        # Default fallback profile
        default_profile = ConfigurationProfile(
            profile_name=profile_name,
            created_by="system",
            config_data={
                "environment": profile_name,
                "log_level": "INFO",
                "max_connections": 20,
                "feature_flags": {
                    "enable_adaptive_followup": True,
                    "enable_llm_evaluation": True,
                    "enable_research_analytics": True,
                },
            },
            version=1,
            description="Default system configuration profile",
        )
        await repo.save(default_profile)
        return default_profile

    async def create_profile(
        self, profile_name: str, created_by: str, config_data: Dict[str, Any], description: str = ""
    ) -> ConfigurationProfile:
        """Creates a new versioned configuration profile and deactivates prior active versions."""
        from app.infrastructure.operations.repositories import ConfigurationProfileRepository
        repo = ConfigurationProfileRepository(self._session)
        
        current_active = await repo.get_active_profile(profile_name)
        next_version = (current_active.version + 1) if current_active else 1

        if current_active:
            current_active.is_active = False
            await repo.save(current_active)

        profile = ConfigurationProfile(
            profile_name=profile_name,
            created_by=created_by,
            config_data=config_data,
            version=next_version,
            is_active=True,
            description=description,
        )
        await repo.save(profile)
        return profile

    async def list_profiles(self, profile_name: Optional[str] = None) -> List[ConfigurationProfile]:
        """Lists configuration profiles."""
        from app.infrastructure.operations.repositories import ConfigurationProfileRepository
        repo = ConfigurationProfileRepository(self._session)
        return await repo.list_profiles(profile_name)
