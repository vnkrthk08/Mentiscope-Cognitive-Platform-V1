from typing import Optional
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.exceptions.listening_exceptions import AudioNotLoaded, AudioPlaybackFailure
from app.core.logging import logger


class ListeningPlayer:
    """Manages audio playback lifecycle, position tracking, and replay status."""

    def __init__(self, audio_asset: Optional[AudioAsset] = None):
        self.audio_asset = audio_asset
        self.playback_status: str = "STOPPED"
        self.current_position_seconds: float = 0.0

    def load_audio(self, audio_asset: AudioAsset):
        self.audio_asset = audio_asset
        self.playback_status = "LOADED"
        self.current_position_seconds = 0.0
        logger.info(f"[LAE PLAYER] Loaded audio asset '{audio_asset.url}' ({audio_asset.duration_seconds}s)")

    def start(self):
        if not self.audio_asset:
            raise AudioNotLoaded("UNKNOWN")
        self.playback_status = "PLAYING"

    def pause(self):
        if self.playback_status == "PLAYING":
            self.playback_status = "PAUSED"

    def resume(self):
        if self.playback_status == "PAUSED":
            self.playback_status = "PLAYING"

    def stop(self):
        self.playback_status = "STOPPED"
        self.current_position_seconds = 0.0
