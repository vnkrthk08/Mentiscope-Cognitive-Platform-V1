import pytest
import uuid
import struct
import hashlib
from httpx import AsyncClient
from app.domain.media.entities.audio_asset import AudioAsset
from app.domain.media.value_objects.processing_status import ProcessingStatus
from app.domain.media.value_objects.storage_location import StorageLocation
from app.domain.media.value_objects.audio_metadata import AudioMetadata
from app.domain.media.value_objects.provenance import ValidationResult, AudioProvenance
from app.infrastructure.media.storage.provider_registry import storage_registry
from app.infrastructure.media.storage.validators.media_validator import MediaValidator
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User


@pytest.mark.asyncio
async def test_audio_asset_status_transitions():
    loc = StorageLocation(
        provider_name="minio",
        bucket_name="bucket",
        object_key="key",
        download_endpoint="endpoint",
    )
    asset = AudioAsset(
        asset_id="asset-1",
        session_id="session-1",
        assessment_id="assess-1",
        candidate_id="cand-1",
        storage_location=loc,
        processing_status=ProcessingStatus.UPLOADING,
    )
    assert asset.processing_status == ProcessingStatus.UPLOADING

    # Valid transition UPLOADING -> UPLOADED
    asset.transition_to(ProcessingStatus.UPLOADED)
    assert asset.processing_status == ProcessingStatus.UPLOADED

    # Valid transition UPLOADED -> VALIDATING
    asset.transition_to(ProcessingStatus.VALIDATING)
    assert asset.processing_status == ProcessingStatus.VALIDATING

    # Invalid transition (VALIDATING back to UPLOADING should raise ValueError)
    with pytest.raises(ValueError):
        asset.transition_to(ProcessingStatus.UPLOADING)


@pytest.mark.asyncio
async def test_storage_provider_registry():
    prov = storage_registry.get_provider("s3")
    assert prov is not None

    default_prov = storage_registry.get_default_provider()
    assert default_prov is not None

    with pytest.raises(ValueError):
        storage_registry.get_provider("invalid_provider")


@pytest.mark.asyncio
async def test_media_validator():
    # 1. Construct valid WAV header bytes
    # WAV format requires 44 bytes header + raw PCM data bytes.
    # channels=1, sample_rate=16000, bits_per_sample=16, duration=2.0s
    # 2.0s duration at 16000Hz mono 16-bit requires: 2 * 16000 * 2 = 64000 data bytes.
    data_size = 64000
    riff_size = data_size + 36
    header = b"RIFF" + struct.pack("<I", riff_size) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16) + b"data" + struct.pack("<I", data_size)
    raw_data = b"\x00" * data_size
    file_bytes = header + raw_data

    # Calculate checksum
    checksum = hashlib.sha256(file_bytes).hexdigest()

    # Run validation
    extracted = MediaValidator.validate_and_extract(
        content=file_bytes,
        expected_checksum=checksum,
        content_type="audio/wav",
    )

    assert extracted["channels"] == 1
    assert extracted["sample_rate"] == 16000
    assert extracted["bit_depth"] == 16
    assert extracted["duration_seconds"] == 2.0
    assert extracted["codec"] == "PCM"


@pytest.mark.asyncio
async def test_media_endpoints_integration(async_client: AsyncClient):
    # 1. Seed Candidate user
    async with UnitOfWork() as uow:
        hashed = PasswordHasher.hash_password("CandidatePass123")
        cand_role = await uow.roles.get_by_name("Candidate")
        user = User(
            user_id=str(uuid.uuid4()),
            username="candidate_media_test",
            email="media_test@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(user)
        await uow.commit()

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "candidate_media_test", "password": "CandidatePass123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. Request presigned upload URL
    session_id = str(uuid.uuid4())
    assess_id = str(uuid.uuid4())
    req_payload = {
        "session_id": session_id,
        "assessment_id": assess_id,
        "content_type": "audio/wav",
        "expected_file_size": 1024 * 50,
    }
    url_res = await async_client.post(
        "/api/v1/media/upload-url", json=req_payload, headers=headers
    )
    assert url_res.status_code == 200
    url_data = url_res.json()
    assert "asset_id" in url_data
    assert "signed_upload_url" in url_data
    asset_id = url_data["asset_id"]

    # 4. Trigger upload completion validation using form multipart
    comp_payload = {
        "asset_id": asset_id,
        "checksum": "mock_checksum",
        "content_type": "audio/wav",
    }
    comp_res = await async_client.post(
        "/api/v1/media/complete", data=comp_payload, headers=headers
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["status"] == "SUCCESS"
    assert comp_data["validation_passed"] is True
    assert comp_data["quarantined"] is False

    # 5. Check AudioAsset persisted state in DB
    async with UnitOfWork() as uow:
        db_asset = await uow.audio_assets.get_by_id(asset_id)
        assert db_asset is not None
        assert db_asset.processing_status == ProcessingStatus.QUEUED
        assert db_asset.audio_metadata is not None
        assert db_asset.audio_metadata.sample_rate == 16000
