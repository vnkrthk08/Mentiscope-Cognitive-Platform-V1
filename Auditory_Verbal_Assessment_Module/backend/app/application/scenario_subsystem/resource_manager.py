from typing import Dict, Any, List
from app.domain.entities.scenario import Scenario
from app.domain.exceptions.scenario_exceptions import MissingAudioAsset


class ScenarioResourceManager:
    """Manages audio assets, images, videos, and media resource path resolutions for scenarios."""

    def __init__(self, base_asset_path: str = "./public/audio"):
        self.base_asset_path = base_asset_path

    def validate_scenario_resources(self, scenario: Scenario) -> List[str]:
        missing_assets: List[str] = []

        if not scenario.audio_asset.url:
            missing_assets.append("Scenario narrative audio URL is empty.")

        if missing_assets:
            raise MissingAudioAsset(", ".join(missing_assets))

        return missing_assets

    def resolve_asset_url(self, relative_url: str) -> str:
        if relative_url.startswith("http://") or relative_url.startswith("https://"):
            return relative_url
        return f"{self.base_asset_path.rstrip('/')}/{relative_url.lstrip('/')}"
