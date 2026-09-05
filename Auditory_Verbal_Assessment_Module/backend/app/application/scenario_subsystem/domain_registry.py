"""
Hierarchical Taxonomy Domain Registry & Combinatorial 4-Tier Scenario Diversity Engine.
Dynamically loads externalized YAML taxonomies from app/domain/taxonomy/*.yaml.
"""

import os
import random
import yaml
from typing import Dict, List, Tuple, Optional, Any

from app.application.scenario_subsystem.assessment_skeleton import AssessmentSkeleton
from app.application.scenario_subsystem.scenario_skeleton import ScenarioSkeleton
from app.application.scenario_subsystem.scenario_grammar import ScenarioGrammarEngine, ScenarioGrammar
from app.application.scenario_subsystem.interaction_model import InteractionModelEngine, InteractionModel
from app.application.scenario_subsystem.assessment_specification import AssessmentSpecification
from app.application.scenario_subsystem.assessment_compiler import AssessmentCompiler
from app.application.scenario_subsystem.structural_filter import StructuralDiversityGuard


class DomainRegistry:
    """Hierarchical Taxonomy Domain Registry supporting millions of 4-tier assessment experiences."""

    def __init__(self, taxonomy_dir: Optional[str] = None):
        if taxonomy_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            taxonomy_dir = os.path.join(base_dir, "domain", "taxonomy")

        self.taxonomy_dir = taxonomy_dir
        self.taxonomies: Dict[str, Any] = {}
        self.compiler = AssessmentCompiler()
        self.structural_guard = StructuralDiversityGuard(similarity_threshold=0.60)
        self.load_yaml_taxonomies()

    def load_yaml_taxonomies(self):
        """Loads all .yaml files in app/domain/taxonomy."""
        if not os.path.exists(self.taxonomy_dir):
            return

        for fname in os.listdir(self.taxonomy_dir):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                fpath = os.path.join(self.taxonomy_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and "category" in data:
                            self.taxonomies[data["category"]] = data
                except Exception as e:
                    print(f"Warning: Failed to load taxonomy file '{fname}': {e}")

    def get_all_domains(self) -> List[str]:
        """Flattens taxonomies into domain context strings for backwards compatibility."""
        domains: List[str] = []
        for cat, data in self.taxonomies.items():
            subcats = data.get("subcategories", {})
            for subcat_name, sub_data in subcats.items():
                equip = sub_data.get("equipment", ["Equipment"])
                events = ["Operational Fault"]
                intents = sub_data.get("intents", {})
                if intents:
                    first_intent = list(intents.values())[0]
                    events = first_intent.get("events", events)
                domains.append(f"{cat} > {subcat_name}: {equip[0]} {events[0]}")
        return domains

    def get_hierarchical_sample(
        self,
        prng: Optional[random.Random] = None,
        excluded_categories: Optional[List[str]] = None,
        assessment_skeleton: Optional[AssessmentSkeleton] = None,
        session_history: Optional[List[Any]] = None,
    ) -> Tuple[str, str, str, str, Dict[str, Any]]:
        """Returns (category, subcategory, context_seed, domain_string, metadata_dict) incorporating 4-tier planning."""
        rnd = prng or random.Random()
        categories = list(self.taxonomies.keys())

        if not categories:
            # Fallback if YAMLs missing
            return (
                "Technology & STEM",
                "Robotics Club",
                "Autonomous rover battery power drop during trial run",
                "Technology & STEM - Robotics Club (Battery power drop)",
                {},
            )

        if excluded_categories:
            avail = [c for c in categories if c not in excluded_categories]
            if avail:
                categories = avail

        category = rnd.choice(categories)
        cat_data = self.taxonomies[category]
        subcats_dict = cat_data.get("subcategories", {})
        subcategories = list(subcats_dict.keys())
        subcategory = rnd.choice(subcategories)
        sub_data = subcats_dict[subcategory]

        # Max 5 attempts to pass StructuralDiversityGuard
        for _ in range(5):
            # 1. Sample Scenario Intent
            intents_dict = sub_data.get("intents", {})
            if intents_dict:
                intent_name = rnd.choice(list(intents_dict.keys()))
                intent_data = intents_dict[intent_name]
            else:
                intent_name = "Emergency Response"
                intent_data = {
                    "events": ["operational breakdown"],
                    "constraints": ["20 minutes remaining"],
                    "escalations": ["unforeseen delay"],
                }

            # 2. Sample 15-Dimension Components
            equipment = rnd.choice(sub_data.get("equipment", ["device"]))
            trigger_event = rnd.choice(intent_data.get("events", ["system fault"]))
            primary_stakeholder = rnd.choice(sub_data.get("stakeholders", ["faculty advisor"]))
            sec_stakeholders = [s for s in sub_data.get("stakeholders", ["evaluator"]) if s != primary_stakeholder]
            secondary_stakeholder = rnd.choice(sec_stakeholders) if sec_stakeholders else "evaluator"
            operational_constraint = rnd.choice(intent_data.get("constraints", ["15 minutes before trial"]))

            res_list = sub_data.get("resources", ["diagnostic workstation"])
            avail_res = rnd.sample(res_list, min(len(res_list), 2))
            missing_res = sub_data.get("missing_resources", ["replacement module"])
            missing_item = rnd.choice(missing_res)

            failure_risk = rnd.choice(sub_data.get("failure_risks", ["project disqualification"]))
            escalation_event = rnd.choice(intent_data.get("escalations", ["evaluator arrives early"]))
            reflection_theme = rnd.choice(sub_data.get("reflection_themes", ["balancing precision with time"]))

            # Synthesize natural language seed
            context_seed = (
                f"{equipment.capitalize()} {trigger_event} during {primary_stakeholder} inspection "
                f"with {operational_constraint}"
            )

            # 3. Create Layer 2 ScenarioSkeleton
            scenario_skel = ScenarioSkeleton(
                category=category,
                subcategory=subcategory,
                scenario_intent=intent_name,
                setting=f"{subcategory} Facility",
                primary_objective=f"Resolve {trigger_event} and validate {equipment}",
                primary_stakeholder=primary_stakeholder,
                secondary_stakeholder=secondary_stakeholder,
                trigger_event=trigger_event,
                operational_constraint=operational_constraint,
                available_resources=avail_res,
                missing_resources=[missing_item],
                time_pressure=operational_constraint,
                success_condition=f"Successfully demonstrate operational stability of {equipment}",
                failure_risk=failure_risk,
                expected_decision_type=assessment_skeleton.target_decision_type if assessment_skeleton else "Resource Trade-off Selection",
                social_dynamics=f"Tension between {primary_stakeholder} priority and {secondary_stakeholder} timeline",
                escalation_event=escalation_event,
                reflection_theme=reflection_theme,
            )

            # 4. Sample Layer 3 Grammar & Layer 4 Interaction Model
            grammar = ScenarioGrammarEngine.get_grammar(rnd.choice(ScenarioGrammarEngine.list_grammars()))
            interaction = InteractionModelEngine.get_model(rnd.choice(InteractionModelEngine.list_models()))

            # 5. Compile AssessmentSpecification
            dummy_as = assessment_skeleton or AssessmentSkeleton(
                primary_constructs=["DECISION_MAKING", "REASONING"],
                secondary_constructs=["ADAPTABILITY"],
                difficulty="INTERMEDIATE",
                listening_difficulty="INTERMEDIATE",
                speaking_difficulty="INTERMEDIATE",
                cognitive_load=3,
                target_decision_type="Resource Trade-off Selection",
                edapaf_mapping={"stage1": "Initial", "stage2": "Adaptive", "stage3": "Reflective"},
                assessment_objective="Evaluate candidate decision making",
            )

            spec = self.compiler.compile(dummy_as, scenario_skel, grammar, interaction)

            # 6. Check StructuralDiversityGuard
            history_fps = [h.fingerprint for h in (session_history or []) if hasattr(h, "fingerprint")]
            if not self.structural_guard.is_fingerprint_duplicate(spec.fingerprint, history_fps):
                domain_string = f"{category} - {subcategory} ({context_seed})"
                meta = {
                    "assessment_specification": spec.to_dict(),
                    "scenario_skeleton": scenario_skel.to_dict(),
                    "scenario_grammar": grammar.name,
                    "interaction_model": interaction.name,
                    "structural_fingerprint": spec.fingerprint.to_dict(),
                }
                return category, subcategory, context_seed, domain_string, meta

        # If guard loops exhaust, return last compiled spec
        domain_string = f"{category} - {subcategory} ({context_seed})"
        meta = {
            "assessment_specification": spec.to_dict(),
            "scenario_skeleton": scenario_skel.to_dict(),
            "scenario_grammar": grammar.name,
            "interaction_model": interaction.name,
            "structural_fingerprint": spec.fingerprint.to_dict(),
        }
        return category, subcategory, context_seed, domain_string, meta
