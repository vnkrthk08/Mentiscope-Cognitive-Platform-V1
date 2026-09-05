from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.infrastructure.speech_service.loader import AudioLoader
from app.infrastructure.speech_service.validator import AudioValidator
from app.infrastructure.speech_service.preprocessor import AudioPreprocessor
from app.infrastructure.speech_service.router import ProviderRouter
from app.infrastructure.speech_service.transcript_builder import TranscriptBuilder, SpeechProcessingResult
from app.infrastructure.speech_service.publisher import SpeechProcessingEventPublisher
from app.domain.exceptions.speech_exceptions import SpeechProcessingFailure


class SpeechProcessingService:
    """Facade for the Speech Processing Service (SPS).
    Validates recordings, normalizes audio, routes transcription requests to provider adapters with retries,
    packages transcripts and word timestamps, and produces immutable SpeechProcessingResult objects.
    DOES NOT EVALUATE COMMUNICATION OR CALL AI EVIDENCE EXTRACTION!
    """

    def __init__(
        self,
        loader: Optional[AudioLoader] = None,
        validator: Optional[AudioValidator] = None,
        preprocessor: Optional[AudioPreprocessor] = None,
        router: Optional[ProviderRouter] = None,
        builder: Optional[TranscriptBuilder] = None,
        publisher: Optional[SpeechProcessingEventPublisher] = None,
        max_retries: int = 2,
    ):
        self.loader = loader or AudioLoader()
        self.validator = validator or AudioValidator()
        self.preprocessor = preprocessor or AudioPreprocessor()
        self.router = router or ProviderRouter()
        self.builder = builder or TranscriptBuilder()
        self.publisher = publisher or SpeechProcessingEventPublisher()
        self.max_retries = max_retries

    async def process_recording(
        self,
        session_id: str,
        prompt_id: str,
        recording_metadata: Dict[str, Any],
    ) -> SpeechProcessingResult:
        """Processes a voice recording reference and returns a standardized SpeechProcessingResult."""
        audio_url = recording_metadata.get("file_url", "")
        logger.info(f"[SPS FACADE] Processing voice recording for session '{session_id}', prompt '{prompt_id}'")

        start_time = datetime.now(timezone.utc)
        await self.publisher.publish_started(session_id, prompt_id, audio_url)

        try:
            # 1. Validate Recording Metadata & Load Audio Payload
            self.validator.validate(recording_metadata)
            duration_sec = float(recording_metadata.get("duration_seconds", 0.0))
            await self.publisher.publish_audio_validated(session_id, audio_url, duration_sec)

            audio_bytes, _ = self.loader.load_audio(audio_url)

            # 2. Preprocess Audio Payload
            processed_bytes, processed_meta = self.preprocessor.preprocess(audio_bytes, recording_metadata)
            await self.publisher.publish_audio_preprocessed(
                session_id, audio_url, processed_meta["sample_rate"], processed_meta["channels"]
            )

            # 3. Route to Speech Provider with Retries
            provider = self.router.select_provider(processed_meta.get("format", "audio/webm"))
            await self.publisher.publish_provider_selected(session_id, provider.provider_name)

            raw_transcription: Dict[str, Any] = {}
            for attempt in range(1, self.max_retries + 1):
                try:
                    await self.publisher.publish_transcription_started(session_id, provider.provider_name)
                    raw_transcription = await provider.transcribe(processed_bytes, {"prompt_id": prompt_id})
                    await self.publisher.publish_transcription_completed(
                        session_id,
                        provider.provider_name,
                        raw_transcription.get("overall_confidence", 0.95),
                        len(raw_transcription.get("text", "")),
                    )
                    break
                except Exception as e:
                    logger.warning(f"[SPS RETRY] Provider '{provider.provider_name}' attempt {attempt} failed: {str(e)}")
                    await self.publisher.publish_retry_attempted(session_id, provider.provider_name, attempt, str(e))
                    if attempt == self.max_retries:
                        raise e

            # 4. Build Standardized SpeechProcessingResult
            proc_duration_sec = (datetime.now(timezone.utc) - start_time).total_seconds()
            result: SpeechProcessingResult = self.builder.build_result(
                session_id=session_id,
                prompt_id=prompt_id,
                audio_url=audio_url,
                raw_provider_data=raw_transcription,
                processing_duration_sec=proc_duration_sec,
            )

            await self.publisher.publish_completed(session_id, prompt_id, result.metadata.overall_confidence, proc_duration_sec)
            logger.info(f"[SPS FACADE] Completed speech processing for prompt '{prompt_id}'. Confidence: {result.metadata.overall_confidence}")

            return result

        except Exception as e:
            await self.publisher.publish_failed(session_id, str(e))
            logger.error(f"[SPS FACADE] Speech processing failed for session '{session_id}': {str(e)}")
            raise SpeechProcessingFailure(session_id, str(e))
