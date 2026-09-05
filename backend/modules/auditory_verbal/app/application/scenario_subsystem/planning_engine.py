import hashlib
import random
from typing import Dict, List, Any
import uuid

from app.domain.entities.assessment_blueprint import ScenarioBlueprint, AssessmentMasterBlueprint
from app.domain.entities.planning_policy import AssessmentPlanningPolicy
from app.domain.value_objects.enums import ConstructType, DifficultyLevel
from app.application.scenario_subsystem.domain_registry import DomainRegistry
from app.application.scenario_subsystem.assessment_skeleton import AssessmentSkeleton


class AssessmentPlanningEngine:
    """Orchestrates complete, deterministic construct-first assessment planning at session startup."""

    def __init__(self, domain_registry: DomainRegistry = None, policy: AssessmentPlanningPolicy = None):
        self.domain_registry = domain_registry or DomainRegistry()
        self.policy = policy or AssessmentPlanningPolicy()

    def plan_assessment(self, candidate_id: str, session_id: str) -> AssessmentMasterBlueprint:
        """Plans the entire 5-scenario blueprint deterministically based on session metadata."""
        # Instantiate a deterministic PRNG using the session ID to ensure repeatability within a session run
        hash_val = int(hashlib.sha256(session_id.encode()).hexdigest(), 16)
        prng = random.Random(hash_val)

        # Retrieve available domains and shuffle deterministically
        available_domains = self.domain_registry.get_all_domains()
        shuffled_domains = list(available_domains)
        prng.shuffle(shuffled_domains)

        # Ensure we have enough domains to cover the assessment size
        while len(shuffled_domains) < self.policy.assessment_size:
            shuffled_domains.extend(available_domains)

        scenario_blueprints: List[ScenarioBlueprint] = []
        coverage_seq = self.policy.construct_coverage_strategy.get("sequence", [])

        used_categories: List[str] = []
        used_domains: List[str] = []

        # Build Scenario Blueprints
        for i in range(self.policy.assessment_size):
            difficulty = self.policy.difficulty_progression[i]
            
            # Retrieve narration bounds based on difficulty level
            bounds = self.policy.narration_length_ranges.get(
                difficulty.value, {"min": 120, "max": 160}
            )

            # Get construct mappings for this step in progression
            step_strategy = coverage_seq[i] if i < len(coverage_seq) else coverage_seq[0]
            speaking_focus = step_strategy["speaking_focus"]
            
            prim_types = [ConstructType(c) for c in step_strategy["primary"]]
            sec_types = [ConstructType(c) for c in step_strategy["secondary"]]

            # Instantiate temporary blueprint for AssessmentSkeleton
            temp_blueprint = ScenarioBlueprint(
                scenario_number=i + 1,
                domain="",
                difficulty=difficulty,
                listening_difficulty=difficulty,
                speaking_focus=speaking_focus,
                primary_constructs=prim_types,
                secondary_constructs=sec_types,
                narration_length_min=bounds["min"],
                narration_length_max=bounds["max"],
                expected_speaking_duration_seconds=self.policy.speaking_duration,
                language_level=self.policy.language_level,
            )

            as_skel = AssessmentSkeleton.from_blueprint(temp_blueprint)

            cat, subcat, seed, domain_str, meta_dict = self.domain_registry.get_hierarchical_sample(
                prng=prng, excluded_categories=used_categories, assessment_skeleton=as_skel
            )
            used_categories.append(cat)
            used_domains.append(domain_str)

            div_constraints = {
                "category": cat,
                "subcategory": subcat,
                "context_seed": seed,
                "excluded_domains": used_domains[:i],
                "excluded_speaking_focus": [b.speaking_focus for b in scenario_blueprints]
            }
            if meta_dict:
                div_constraints.update(meta_dict)

            blueprint = ScenarioBlueprint(
                scenario_number=i + 1,
                domain=domain_str,
                difficulty=difficulty,
                listening_difficulty=difficulty,
                speaking_focus=speaking_focus,
                primary_constructs=prim_types,
                secondary_constructs=sec_types,
                narration_length_min=bounds["min"],
                narration_length_max=bounds["max"],
                expected_speaking_duration_seconds=self.policy.speaking_duration,
                language_level=self.policy.language_level,
                diversity_constraints=div_constraints
            )
            scenario_blueprints.append(blueprint)

        master_blueprint = AssessmentMasterBlueprint(
            assessment_id=f"AMB-{uuid.uuid4().hex[:8].upper()}",
            assessment_policy_version="1.0.0",
            total_scenario_count=self.policy.assessment_size,
            overall_construct_coverage_plan=[s["speaking_focus"] for s in coverage_seq],
            overall_difficulty_progression=self.policy.difficulty_progression,
            overall_domain_diversity_strategy=[b.domain for b in scenario_blueprints],
            scenario_blueprints=scenario_blueprints
        )

        return master_blueprint
