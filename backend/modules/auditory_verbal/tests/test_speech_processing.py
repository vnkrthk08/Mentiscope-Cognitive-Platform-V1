import pytest
import uuid
import asyncio
from datetime import datetime, timezone
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User
from app.domain.media.entities.audio_asset import AudioAsset
from app.domain.media.value_objects.processing_status import ProcessingStatus
from app.domain.media.value_objects.storage_location import StorageLocation
from app.domain.media.value_objects.audio_metadata import AudioMetadata
from app.infrastructure.speech.providers.provider_registry import speech_registry
from app.infrastructure.speech.strategies.provider_selection import ProviderSelectionStrategy
from app.infrastructure.speech.normalizer import TranscriptNormalizer
from app.infrastructure.speech.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from app.infrastructure.speech.retry_policy import execute_with_retry, TransientProviderError, FatalProviderError


@pytest.mark.asyncio
async def test_provider_registry_and_selection_strategy():
    # Registry checks
    assert "whisper" in speech_registry.list_providers()
    assert "azure" in speech_registry.list_providers()
    assert "deepgram" in speech_registry.list_providers()

    # Strategy checks
    name_default, _ = ProviderSelectionStrategy.resolve_provider("DEFAULT")
    assert name_default == "whisper"

    name_fastest, _ = ProviderSelectionStrategy.resolve_provider("FASTEST")
    assert name_fastest == "deepgram"

    name_cheapest, _ = ProviderSelectionStrategy.resolve_provider("LOWEST_COST", duration_seconds=600)
    # Whisper ($0.06) is cheaper than Deepgram ($0.125)
    assert name_cheapest == "whisper"


@pytest.mark.asyncio
async def test_transcript_normalizer():
    # Test whisper normalization
    whisper_raw = {
        "text": "Whisper Text",
        "language": "en",
        "segments": [
            {
                "words": [
                    {"word": "Whisper", "start": 0.0, "end": 1.0, "probability": 0.99},
                    {"word": "Text", "start": 1.0, "end": 2.0, "probability": 0.98},
                ]
            }
        ]
    }
    txt, words, score, lang = TranscriptNormalizer.normalize("whisper", whisper_raw)
    assert txt == "Whisper Text"
    assert len(words) == 2
    assert words[0].word == "Whisper"
    assert score.overall_score == 0.985
    assert lang.language_code == "en"


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    
    async def failing_call():
        raise Exception("Transient network timeout")

    # Record first failure
    with pytest.raises(Exception):
        await breaker.execute(failing_call)
    assert breaker.state == "CLOSED"

    # Record second failure -> trips to OPEN
    with pytest.raises(Exception):
        await breaker.execute(failing_call)
    assert breaker.state == "OPEN"

    # Attempt execute while OPEN raises CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException):
        await breaker.execute(failing_call)

    # Sleep to trigger cooldown recovery timeout
    await asyncio.sleep(0.15)
    assert breaker.attempt_execution() is True
    assert breaker.state == "HALF_OPEN"


@pytest.mark.asyncio
async def test_retry_policy_exponential_backoff():
    call_counts = 0

    async def transient_failing_call():
        nonlocal call_counts
        call_counts += 1
        if call_counts < 3:
            raise TransientProviderError("API limit exceeded")
        return "SUCCESS_VALUE"

    res = await execute_with_retry(
        transient_failing_call, max_retries=3, initial_delay=0.01, backoff_factor=1.5
    )
    assert res == "SUCCESS_VALUE"
    assert call_counts == 3


@pytest.mark.asyncio
async def test_speech_endpoints_integration(async_client: AsyncClient):
    # 1. Seed Candidate user
    candidate_username = "candidate_stt_test"
    async with UnitOfWork() as uow:
        hashed = PasswordHasher.hash_password("CandidatePass123")
        cand_role = await uow.roles.get_by_name("Candidate")
        user = User(
            user_id=str(uuid.uuid4()),
            username=candidate_username,
            email="stt_test@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(user)

        # 2. Seed pre-existing QUEUED AudioAsset record
        loc = StorageLocation(
            provider_name="minio",
            bucket_name="bucket",
            object_key="audio.wav",
            download_endpoint="endpoint",
        )
        meta = AudioMetadata(
            content_type="audio/wav",
            duration_seconds=5.2,
            sample_rate=16000,
            channels=1,
            bit_depth=16,
            codec="PCM",
            file_size_bytes=100000,
            checksum_sha256="checksum",
        )
        asset_id = "00000000-0000-0000-0000-000000000099"
        session_id = str(uuid.uuid4())
        assess_id = str(uuid.uuid4())
        asset = AudioAsset(
            asset_id=asset_id,
            session_id=session_id,
            assessment_id=assess_id,
            candidate_id=candidate_username,
            storage_location=loc,
            audio_metadata=meta,
            processing_status=ProcessingStatus.QUEUED,
        )
        await uow.audio_assets.save(asset)
        await uow.commit()

    # 3. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": candidate_username, "password": "CandidatePass123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 4. Trigger transcription request
    tx_payload = {
        "asset_id": asset_id,
        "selection_policy": "DEFAULT",
    }
    tx_res = await async_client.post(
        "/api/v1/speech/transcribe", json=tx_payload, headers=headers
    )
    assert tx_res.status_code == 202
    job_id = tx_res.json()["job_id"]
    assert job_id is not None

    # Wait briefly for background execution task to complete
    await asyncio.sleep(0.5)

    # 5. Fetch job progress
    job_res = await async_client.get(f"/api/v1/speech/jobs/{job_id}", headers=headers)
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["status"] == "COMPLETED"

    # 6. Retrieve final normalized Transcript
    # We query the DB directly to get the transcript ID associated with this asset ID
    async with UnitOfWork() as uow:
        db_tx = await uow.speech_transcripts.get_by_asset_id(asset_id)
        assert db_tx is not None
        transcript_id = db_tx.transcript_id

    tx_get_res = await async_client.get(
        f"/api/v1/speech/transcripts/{transcript_id}", headers=headers
    )
    assert tx_get_res.status_code == 200
    tx_data = tx_get_res.json()
    assert "MentiScope" in tx_data["transcript_text"]
    assert len(tx_data["word_timestamps"]) == 6
