"""RegistryService — Model Registry and Configuration Snapshot Management."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.entities.model_registry import RegisteredModel
from app.domain.governance.entities.configuration_snapshot import ConfigurationSnapshot
from app.domain.governance.value_objects.model_version import ModelVersion
from app.domain.governance.value_objects.configuration_hash import ConfigurationHash
from app.infrastructure.governance.repositories import (
    ModelRegistryRepository,
    ConfigurationSnapshotRepository,
)


class RegistryService:
    """Application service for Model Governance Registry & Snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._model_repo = ModelRegistryRepository(session)
        self._snapshot_repo = ConfigurationSnapshotRepository(session)

    async def register_model(
        self,
        name: str,
        category: str,
        version_str: str,
        owner: str,
        description: str = "",
        configuration: Optional[Dict[str, Any]] = None,
    ) -> RegisteredModel:
        config = configuration or {}
        checksum = self._compute_checksum(name, category, version_str, config)
        version = ModelVersion(value=version_str)

        model = RegisteredModel(
            name=name,
            category=category.upper(),
            version=version,
            owner=owner,
            description=description,
            checksum=checksum,
            configuration=config,
            status="ACTIVE",
        )

        await self._model_repo.save(model)
        return model

    async def get_model_by_id(self, model_id: str) -> Optional[RegisteredModel]:
        return await self._model_repo.get_by_id(model_id)

    async def list_models(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[RegisteredModel]:
        return await self._model_repo.list_all(category=category, status=status, limit=limit)

    async def create_snapshot(
        self,
        snapshot_name: str,
        created_by: str,
        speech_model_id: Optional[str] = None,
        prompt_template_id: Optional[str] = None,
        llm_model_id: Optional[str] = None,
        behavior_extractor_id: Optional[str] = None,
        construct_policy_id: Optional[str] = None,
        scoring_policy_id: Optional[str] = None,
        full_config: Optional[Dict[str, Any]] = None,
    ) -> ConfigurationSnapshot:
        snapshot = ConfigurationSnapshot(
            snapshot_name=snapshot_name,
            created_by=created_by,
            speech_model_id=speech_model_id,
            prompt_template_id=prompt_template_id,
            llm_model_id=llm_model_id,
            behavior_extractor_id=behavior_extractor_id,
            construct_policy_id=construct_policy_id,
            scoring_policy_id=scoring_policy_id,
            full_config=full_config or {},
        )
        await self._snapshot_repo.save(snapshot)
        return snapshot

    async def get_snapshot_by_id(self, snapshot_id: str) -> Optional[ConfigurationSnapshot]:
        return await self._snapshot_repo.get_by_id(snapshot_id)

    def _compute_checksum(
        self, name: str, category: str, version: str, config: Dict[str, Any]
    ) -> str:
        payload = f"{name}:{category}:{version}:{json.dumps(config, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
