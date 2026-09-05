import os
import pytest
from app.application.scenario_subsystem import (
    ScenarioManagementSystem,
    ScenarioRepository,
    ScenarioLoader,
    ScenarioValidator,
    ScenarioFactory,
    ScenarioCache,
    ScenarioVersionManager,
    ScenarioResourceManager,
    ScenarioConstructMapper,
    ScenarioAnalytics,
)
from app.domain.entities.scenario import Scenario
from app.domain.exceptions.scenario_exceptions import (
    ScenarioNotFound,
    ScenarioValidationError,
    ScenarioLoadFailure,
    VersionMismatch,
)


def _get_sample_yaml_path() -> str:
    repo = ScenarioRepository()
    return os.path.join(repo.config_dir, "scenario_001.yaml")


def test_scenario_loader_and_validator():
    loader = ScenarioLoader()
    validator = ScenarioValidator()

    # Load valid scenario
    yaml_path = _get_sample_yaml_path()
    raw_data = loader.load_from_file(yaml_path)
    assert raw_data["id"] == "SCENARIO_LOGISTICS_01"

    # Validate valid scenario (no errors raised)
    errors = validator.validate(raw_data)
    assert len(errors) == 0


def test_scenario_validator_invalid_scenario_raises_error():
    validator = ScenarioValidator()

    invalid_data = {
        "id": "INVALID_01",
        "title": "Invalid Scenario",
        "narrative": "Missing modules",
        "version": "1.0.0",
        "audio_asset": {"url": ""},  # Invalid empty URL
        "listening_module": {"questions": []},  # Empty questions
        "speaking_module": {"prompts": []},  # Empty prompts
    }

    with pytest.raises(ScenarioValidationError) as exc_info:
        validator.validate(invalid_data)

    assert len(exc_info.value.errors) > 0


def test_scenario_factory_hydration():
    loader = ScenarioLoader()
    factory = ScenarioFactory()

    yaml_path = _get_sample_yaml_path()
    raw_data = loader.load_from_file(yaml_path)
    scenario: Scenario = factory.create_from_dict(raw_data)

    assert scenario.scenario_id == "SCENARIO_LOGISTICS_01"
    assert scenario.title == "Supply Chain Crisis Management"
    assert str(scenario.version) == "1.0.0"
    assert scenario.audio_asset.url == "/audio/scenarios/logistics_crisis.mp3"
    assert len(scenario.listening_questions) == 4
    assert len(scenario.speaking_prompts) == 2
    assert len(scenario.follow_up_definitions) == 1
    assert len(scenario.construct_mappings) > 0


def test_scenario_cache():
    cache = ScenarioCache()
    loader = ScenarioLoader()
    factory = ScenarioFactory()

    yaml_path = _get_sample_yaml_path()
    raw_data = loader.load_from_file(yaml_path)
    scenario = factory.create_from_dict(raw_data)

    cache.put(scenario)
    cached_scenario = cache.get("SCENARIO_LOGISTICS_01")
    assert cached_scenario is not None
    assert cached_scenario.scenario_id == "SCENARIO_LOGISTICS_01"

    cache.invalidate("SCENARIO_LOGISTICS_01")
    assert cache.get("SCENARIO_LOGISTICS_01") is None


def test_scenario_version_manager():
    vm = ScenarioVersionManager()

    assert vm.compare_versions("1.1.0", "1.0.0") == 1
    assert vm.compare_versions("1.0.0", "1.0.0") == 0
    assert vm.compare_versions("1.0.0", "2.0.0") == -1

    vm.mark_deprecated("SCENARIO_LOGISTICS_01", "1.0.0")
    assert vm.is_deprecated("SCENARIO_LOGISTICS_01", "1.0.0") is True

    with pytest.raises(VersionMismatch):
        vm.assert_compatible("1.0.0", "2.0.0")


def test_scenario_construct_mapper_and_analytics():
    loader = ScenarioLoader()
    factory = ScenarioFactory()
    mapper = ScenarioConstructMapper()
    analytics = ScenarioAnalytics()

    yaml_path = _get_sample_yaml_path()
    raw_data = loader.load_from_file(yaml_path)
    scenario = factory.create_from_dict(raw_data)

    coverage = mapper.validate_construct_coverage(scenario)
    assert coverage["total_constructs_covered"] > 0

    stats = analytics.analyze_scenario(scenario)
    assert stats["listening_questions_count"] == 4
    assert stats["speaking_prompts_count"] == 2
    assert stats["total_audio_duration_seconds"] == 180.0
    assert stats["estimated_completion_time_minutes"] > 0


@pytest.mark.asyncio
async def test_sms_facade_integration():
    sms = ScenarioManagementSystem()
    scenario = await sms.load_scenario("SCENARIO_LOGISTICS_01")

    assert scenario.scenario_id == "SCENARIO_LOGISTICS_01"
    assert scenario.title == "Supply Chain Crisis Management"

    analytics_stats = sms.get_analytics(scenario)
    assert analytics_stats["scenario_id"] == "SCENARIO_LOGISTICS_01"
