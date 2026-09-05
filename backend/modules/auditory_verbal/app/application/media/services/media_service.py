import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.media.entities.audio_asset import AudioAsset
from app.domain.media.value_objects.processing_status import ProcessingStatus
from app.domain.media.value_objects.storage_location import StorageLocation
from app.domain.media.value_objects.audio_metadata import AudioMetadata
from app.domain.media.value_objects.provenance import ValidationResult, AudioProvenance
from app.infrastructure.media.storage.provider_registry import storage_registry
from app.infrastructure.media.storage.validators.media_validator import MediaValidator
from app.infrastructure.media.orm_models import UploadAuditORM
from app.application.media.events import audio_events


class MalwareScanner:
    """Extension point for future antivirus integration checks."""

    @staticmethod
    async def scan_file(content: bytes) -> Tuple[bool, str]:
        # Simulates non-blocking scan, returning (is_clean, failure_reason)
        return True, ""


class MediaService:
    """Application service orchestrating presigned upload URL requests and ingestion completions."""

    @staticmethod
    async def get_presigned_upload_url(
        session_id: str,
        assessment_id: str,
        candidate_id: str,
        content_type: str,
        expected_file_size: int,
        ip_address: str,
        user_agent: str,
    ) -> Tuple[str, str, str]:
        # 1. Resolve storage provider from configuration registry
        provider = storage_registry.get_default_provider()
        provider_name = os.getenv("STORAGE_PROVIDER", "minio")
        bucket_name = os.getenv("STORAGE_BUCKET_NAME", "mentiscope-audio")

        asset_id = str(uuid.uuid4())

        # 2. Standardized key structure layout
        # audio/candidate_id/assessment_id/session_id/asset_id.wav
        ext = "wav" if "wav" in content_type.lower() else "mp3"
        object_key = f"audio/{candidate_id}/{assessment_id}/{session_id}/{asset_id}.{ext}"

        # 3. Generate presigned PUT upload URL
        upload_url = await provider.generate_upload_url(bucket_name, object_key)
        download_endpoint = await provider.generate_download_url(bucket_name, object_key)

        # 4. Instantiate and save initial AudioAsset record in UPLOADING status
        loc = StorageLocation(
            provider_name=provider_name,
            bucket_name=bucket_name,
            object_key=object_key,
            download_endpoint=download_endpoint,
        )

        asset = AudioAsset(
            asset_id=asset_id,
            session_id=session_id,
            assessment_id=assessment_id,
            candidate_id=candidate_id,
            storage_location=loc,
            processing_status=ProcessingStatus.UPLOADING,
        )

        async with UnitOfWork() as uow:
            await uow.audio_assets.save(asset)

            # Log initial upload audit
            audit = UploadAuditORM(
                id=uuid.uuid4(),
                asset_id=uuid.UUID(asset_id),
                actor_id=candidate_id,
                ip_address=ip_address,
                user_agent=user_agent,
                action="UPLOAD_REQUEST",
            )
            await uow.audio_assets.log_audit(audit)
            await uow.commit()

        return asset_id, upload_url, provider_name

    @staticmethod
    async def complete_audio_upload(
        asset_id: str,
        file_bytes: bytes,
        checksum_sha256: str,
        content_type: str,
        actor_id: str,
        ip_address: str,
        user_agent: str,
    ) -> Tuple[bool, bool, str]:
        # 1. Fetch the AudioAsset ORM record
        async with UnitOfWork() as uow:
            asset = await uow.audio_assets.get_by_id(asset_id)
            if not asset:
                raise HTTPException(status_code=404, detail="Audio asset registration not found.")

            # Validate ownership
            if asset.candidate_id != actor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate asset ownership.",
                )

            # Transition state through lifecycle: UPLOADING -> UPLOADED -> VALIDATING
            asset.transition_to(ProcessingStatus.UPLOADED)
            asset.transition_to(ProcessingStatus.VALIDATING)
            await uow.audio_assets.save(asset)
            await uow.commit()

        # 2. Trigger Malware Antivirus Scan simulation
        scan_ok, scan_reason = await MalwareScanner.scan_file(file_bytes)
        if not scan_ok:
            async with UnitOfWork() as uow:
                asset = await uow.audio_assets.get_by_id(asset_id)
                asset.transition_to(ProcessingStatus.QUARANTINED)
                asset.validation_result = ValidationResult(
                    is_valid=False,
                    validation_timestamp=datetime.now(timezone.utc),
                    failure_reason=f"Malware detection: {scan_reason}",
                )
                await uow.audio_assets.save(asset)
                await uow.commit()
            return False, True, f"Malware scan failure: {scan_reason}"

        # 3. Trigger structural format validation checks
        try:
            extracted = MediaValidator.validate_and_extract(
                content=file_bytes,
                expected_checksum=checksum_sha256,
                content_type=content_type,
            )
        except ValueError as val_err:
            reason = str(val_err)
            async with UnitOfWork() as uow:
                asset = await uow.audio_assets.get_by_id(asset_id)
                asset.transition_to(ProcessingStatus.QUARANTINED)
                asset.validation_result = ValidationResult(
                    is_valid=False,
                    validation_timestamp=datetime.now(timezone.utc),
                    failure_reason=reason,
                )
                await uow.audio_assets.save(asset)
                await uow.commit()
            return False, True, reason

        # 4. Success state mapping & final save
        async with UnitOfWork() as uow:
            asset = await uow.audio_assets.get_by_id(asset_id)
            
            # Transition to VALIDATED
            asset.transition_to(ProcessingStatus.VALIDATED)
            
            # Hydrate Value Objects
            asset.audio_metadata = AudioMetadata(
                content_type=content_type,
                duration_seconds=extracted["duration_seconds"],
                sample_rate=extracted["sample_rate"],
                channels=extracted["channels"],
                bit_depth=extracted["bit_depth"],
                codec=extracted["codec"],
                file_size_bytes=extracted["file_size_bytes"],
                checksum_sha256=checksum_sha256,
            )
            asset.validation_result = ValidationResult(
                is_valid=True,
                validation_timestamp=datetime.now(timezone.utc),
            )
            asset.provenance = AudioProvenance(
                uploaded_by=actor_id,
                upload_method="PRESIGNED_PUT",
                storage_provider=asset.storage_location.provider_name,
                provider_version="1.0.0",
                pipeline_version="1.0.0",
                checksum_algorithm="SHA-256",
                upload_timestamp=datetime.now(timezone.utc),
            )

            # Move to QUEUED (Ready for downstream STT processing)
            asset.transition_to(ProcessingStatus.QUEUED)

            await uow.audio_assets.save(asset)

            # Log audit logs
            audit = UploadAuditORM(
                id=uuid.uuid4(),
                asset_id=uuid.UUID(asset_id),
                actor_id=actor_id,
                ip_address=ip_address,
                user_agent=user_agent,
                action="UPLOAD_COMPLETE_SUCCESS",
            )
            await uow.audio_assets.log_audit(audit)
            await uow.commit()

        # 5. Simulate publishing background events
        # In production this would emit to a queue/event-bus
        return True, False, "Audio validated and queued for transcription."


import os
