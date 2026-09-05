from typing import Any, Dict, List, Set
from app.domain.entities.scenario import Scenario
from app.domain.value_objects.enums import ConstructType
from app.domain.exceptions.scenario_exceptions import MissingConstructMapping


class ScenarioConstructMapper:
    """Manages construct mappings and validates coverage completeness across listening and speaking items."""

    def validate_construct_coverage(self, scenario: Scenario) -> Dict[str, Any]:
        mapped_constructs: Set[ConstructType] = set()

        for q in scenario.listening_questions:
            if not q.target_construct:
                raise MissingConstructMapping(scenario.scenario_id, q.question_id, "ListeningQuestion")
            mapped_constructs.add(q.target_construct)

        for p in scenario.speaking_prompts:
            if not p.target_constructs:
                raise MissingConstructMapping(scenario.scenario_id, p.prompt_id, "SpeakingPrompt")
            for c in p.target_constructs:
                mapped_constructs.add(c)

        for f in scenario.follow_up_definitions:
            if f.target_construct:
                mapped_constructs.add(f.target_construct)

        return {
            "scenario_id": scenario.scenario_id,
            "total_constructs_covered": len(mapped_constructs),
            "constructs": [c.value for c in mapped_constructs],
        }
