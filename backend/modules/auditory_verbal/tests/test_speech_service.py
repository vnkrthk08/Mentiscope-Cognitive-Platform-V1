import pytest
from app.infrastructure.speech_service import (
    SpeechProcessingService,
    AudioLoader,
    AudioValidator,
    AudioPreprocessor,
    ProviderRouter,
    MockSpeechProvider,
    TranscriptBuilder,
)
from app.domain.exceptions.speech_exceptions import (
    UnsupportedAudioFormat,
    AudioValidationFailure,
    ProviderUnavailable,
    SpeechProcessingFailure,
)


def test_audio_loader_and_validator():
    loader = AudioLoader()
    validator = AudioValidator()

    meta = {"file_url": "/storage/audio/S_P1_rec.webm", "duration_seconds": 15.0, "format": "audio/webm"}
    assert validator.validate(meta) is True

    audio_bytes, file_size = loader.load_audio(meta["file_url"])
    assert len(audio_bytes) > 0
    assert file_size == len(audio_bytes)

    # Test unsupported format exception
    invalid_meta = {"file_url": "/storage/audio/S_P1_rec.txt", "duration_seconds": 15.0, "format": "text/plain"}
    with pytest.raises(UnsupportedAudioFormat):
        validator.validate(invalid_meta)


def test_audio_preprocessor():
    preprocessor = AudioPreprocessor()
    meta = {"file_url": "/audio/rec.webm", "format": "audio/webm"}
    raw_bytes = b"MOCK_BYTES"

    proc_bytes, proc_meta = preprocessor.preprocess(raw_bytes, meta)
    assert proc_bytes == raw_bytes
    assert proc_meta["preprocessed"] is True
    assert proc_meta["sample_rate"] == 16000
    assert proc_meta["channels"] == 1


@pytest.mark.asyncio
async def test_mock_speech_provider():
    provider = MockSpeechProvider()
    assert provider.health() is True
    assert "en-US" in provider.supported_languages()

    raw_res = await provider.transcribe(b"MOCK_BYTES", {"prompt_id": "S_P1"})
    assert "safety protocols" in raw_res["text"]
    assert len(raw_res["word_timestamps"]) > 0
    assert raw_res["overall_confidence"] == 0.96


def test_provider_router():
    router = ProviderRouter([MockSpeechProvider()])
    selected = router.select_provider("audio/webm")
    assert selected.provider_name == "WHISPER"

    # Test unavailable format
    with pytest.raises(ProviderUnavailable):
        router.select_provider("audio/unsupported_format")


def test_transcript_builder():
    builder = TranscriptBuilder()
    raw_data = {
        "text": "Hello world test",
        "language": "en-US",
        "overall_confidence": 0.98,
        "provider_name": "MockWhisper",
        "word_timestamps": [
            {"word": "Hello", "start_time": 0.0, "end_time": 0.5, "confidence": 0.99},
            {"word": "world", "start_time": 0.5, "end_time": 1.0, "confidence": 0.98},
        ],
        "segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "Hello world test", "confidence": 0.98}],
    }

    res = builder.build_result("SESS-01", "S_P1", "/audio/rec.webm", raw_data, 0.45)
    assert res.session_id == "SESS-01"
    assert res.prompt_id == "S_P1"
    assert res.transcript.full_text == "Hello world test"
    assert len(res.transcript.word_timestamps) == 2
    assert res.metadata.provider_name == "MockWhisper"


@pytest.mark.asyncio
async def test_sps_facade_end_to_end_processing():
    sps = SpeechProcessingService()
    meta = {
        "file_url": "/storage/audio/S_P1_rec.webm",
        "duration_seconds": 12.0,
        "format": "audio/webm",
        "file_size_bytes": 1024,
    }

    result = await sps.process_recording(
        session_id="SESS-SPS-001",
        prompt_id="S_P1",
        recording_metadata=meta,
    )

    assert result.session_id == "SESS-SPS-001"
    assert result.prompt_id == "S_P1"
    assert result.transcript.full_text != ""
    assert len(result.transcript.word_timestamps) > 0
    assert result.metadata.overall_confidence > 0.90
