import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.media.entities.audio_asset import AudioAsset
from app.domain.media.value_objects.processing_status import ProcessingStatus
from app.domain.media.value_objects.storage_location import StorageLocation
from app.domain.media.value_objects.audio_metadata import AudioMetadata
from app.domain.media.value_objects.provenance import ValidationResult, AudioProvenance
from app.infrastructure.media.orm_models import AudioAssetORM, UploadAuditORM


class MediaMapper:
    @staticmethod
    def to_domain(orm: AudioAssetORM) -> AudioAsset:
        loc = orm.storage_location
        loc_vo = StorageLocation(
            provider_name=loc["provider_name"],
            bucket_name=loc["bucket_name"],
            object_key=loc["object_key"],
            download_endpoint=loc["download_endpoint"],
        )

        meta_vo = None
        if orm.audio_metadata:
            m = orm.audio_metadata
            meta_vo = AudioMetadata(
                content_type=m["content_type"],
                duration_seconds=m["duration_seconds"],
                sample_rate=m["sample_rate"],
                channels=m["channels"],
                bit_depth=m["bit_depth"],
                codec=m["codec"],
                file_size_bytes=m["file_size_bytes"],
                checksum_sha256=m["checksum_sha256"],
            )

        val_vo = None
        if orm.validation_result:
            v = orm.validation_result
            ts = datetime.fromisoformat(v["validation_timestamp"]) if isinstance(v["validation_timestamp"], str) else v["validation_timestamp"]
            val_vo = ValidationResult(
                is_valid=v["is_valid"],
                validation_timestamp=ts,
                failure_reason=v.get("failure_reason"),
            )

        prov_vo = None
        if orm.provenance:
            p = orm.provenance
            ts = datetime.fromisoformat(p["upload_timestamp"]) if isinstance(p["upload_timestamp"], str) else p["upload_timestamp"]
            prov_vo = AudioProvenance(
                uploaded_by=p["uploaded_by"],
                upload_method=p["upload_method"],
                storage_provider=p["storage_provider"],
                provider_version=p["provider_version"],
                pipeline_version=p["pipeline_version"],
                checksum_algorithm=p["checksum_algorithm"],
                upload_timestamp=ts,
            )

        return AudioAsset(
            asset_id=str(orm.id),
            session_id=str(orm.session_id),
            assessment_id=str(orm.assessment_id),
            candidate_id=orm.candidate_id,
            storage_location=loc_vo,
            audio_metadata=meta_vo,
            processing_status=ProcessingStatus(orm.processing_status),
            validation_result=val_vo,
            provenance=prov_vo,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: AudioAsset) -> AudioAssetORM:
        loc_payload = {
            "provider_name": domain.storage_location.provider_name,
            "bucket_name": domain.storage_location.bucket_name,
            "object_key": domain.storage_location.object_key,
            "download_endpoint": domain.storage_location.download_endpoint,
        }

        meta_payload = None
        if domain.audio_metadata:
            meta_payload = {
                "content_type": domain.audio_metadata.content_type,
                "duration_seconds": domain.audio_metadata.duration_seconds,
                "sample_rate": domain.audio_metadata.sample_rate,
                "channels": domain.audio_metadata.channels,
                "bit_depth": domain.audio_metadata.bit_depth,
                "codec": domain.audio_metadata.codec,
                "file_size_bytes": domain.audio_metadata.file_size_bytes,
                "checksum_sha256": domain.audio_metadata.checksum_sha256,
            }

        val_payload = None
        if domain.validation_result:
            val_payload = {
                "is_valid": domain.validation_result.is_valid,
                "validation_timestamp": domain.validation_result.validation_timestamp.isoformat(),
                "failure_reason": domain.validation_result.failure_reason,
            }

        prov_payload = None
        if domain.provenance:
            prov_payload = {
                "uploaded_by": domain.provenance.uploaded_by,
                "upload_method": domain.provenance.upload_method,
                "storage_provider": domain.provenance.storage_provider,
                "provider_version": domain.provenance.provider_version,
                "pipeline_version": domain.provenance.pipeline_version,
                "checksum_algorithm": domain.provenance.checksum_algorithm,
                "upload_timestamp": domain.provenance.upload_timestamp.isoformat(),
            }

        return AudioAssetORM(
            id=uuid.UUID(domain.asset_id),
            session_id=uuid.UUID(domain.session_id),
            assessment_id=uuid.UUID(domain.assessment_id),
            candidate_id=domain.candidate_id,
            processing_status=domain.processing_status.value,
            storage_location=loc_payload,
            audio_metadata=meta_payload,
            validation_result=val_payload,
            provenance=prov_payload,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class AudioRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, asset_id: str) -> Optional[AudioAsset]:
        try:
            aid = uuid.UUID(asset_id)
        except ValueError:
            return None
        orm = await self.session.get(AudioAssetORM, aid)
        return MediaMapper.to_domain(orm) if orm else None

    async def save(self, asset: AudioAsset) -> AudioAsset:
        orm = MediaMapper.to_orm(asset)
        existing = await self.session.get(AudioAssetORM, orm.id)
        if existing:
            existing.processing_status = orm.processing_status
            existing.storage_location = orm.storage_location
            existing.audio_metadata = orm.audio_metadata
            existing.validation_result = orm.validation_result
            existing.provenance = orm.provenance
            existing.updated_at = datetime.now(timezone.utc)
            orm = existing
        else:
            self.session.add(orm)
        await self.session.flush()
        return MediaMapper.to_domain(orm)

    async def log_audit(self, audit_orm: UploadAuditORM) -> None:
        self.session.add(audit_orm)
        await self.session.flush()
        
    async def list_by_session(self, session_id: str) -> List[AudioAsset]:
        result = await self.session.execute(
            select(AudioAssetORM).where(AudioAssetORM.session_id == uuid.UUID(session_id))
        )
        return [MediaMapper.to_domain(orm) for orm in result.scalars().all()]
