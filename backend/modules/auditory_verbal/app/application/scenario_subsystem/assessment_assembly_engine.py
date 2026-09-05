"""
Module: Assessment Assembly Engine (v1.0).
Master orchestrator assembling complete, constraint-validated, 5-scenario psychometric assessments.
"""

import random
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
from datetime import datetime, timezone

from app.application.scenario_subsystem.scenario_repository import ScenarioRepository
from app.application.scenario_subsystem.scenario_metadata import ScenarioMetadata
from app.application.scenario_subsystem.assessment_blueprint import AssessmentBlueprintGenerator, AssessmentBlueprint
from app.application.scenario_subsystem.constraint_validator import ConstraintValidator, ValidationResult
from app.application.scenario_subsystem.coverage_optimizer import CoverageOptimizer
from app.application.scenario_subsystem.difficulty_optimizer import DifficultyOptimizer
from app.application.scenario_subsystem.assessment_audit import AssessmentAuditReport
from app.application.scenario_subsystem.assessment_builder import Assessment, AssessmentBuilder
from app.domain.entities.scenario import Scenario


class AssessmentAssemblyEngine:
    """Constraint-based 5-scenario assessment assembly engine."""

    def __init__(self, repo: Optional[ScenarioRepository] = None):
        self.repo = repo or ScenarioRepository()
        self.blueprint_gen = AssessmentBlueprintGenerator()
        self.validator = ConstraintValidator()
        self.coverage_opt = CoverageOptimizer()
        self.diff_opt = DifficultyOptimizer()
        self.builder = AssessmentBuilder()

    def assemble_assessment(
        self,
        candidate_id: str,
        seed: Optional[int] = None,
        assessment_id: Optional[str] = None,
    ) -> Assessment:

        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        ass_id = assessment_id or f"ASS-{uuid.uuid4().hex[:8].upper()}"
        blueprint = self.blueprint_gen.generate_blueprint(f"BP-{ass_id}", candidate_id)

        all_metadata = self.repo.list_all_metadata()
        all_scenarios = {s.scenario_id: s for s in self.repo.list_all_scenarios()}

        selected_meta: List[ScenarioMetadata] = []
        selected_scenarios: List[Scenario] = []

        used_families = set()
        used_categories = set()

        for slot in blueprint.slots:
            candidates = [
                m for m in all_metadata
                if m.family_id not in used_families
                and m.category not in used_categories
            ]

            if not candidates:
                candidates = [m for m in all_metadata if m.scenario_id not in [sm.scenario_id for sm in selected_meta]]

            # Filter candidates by slot target difficulty if available
            diff_matches = [m for m in candidates if m.listening_difficulty == slot.target_difficulty]
            if diff_matches:
                chosen = rng.choice(diff_matches)
            else:
                chosen = rng.choice(candidates)

            selected_meta.append(chosen)
            selected_scenarios.append(all_scenarios[chosen.scenario_id])

            used_families.add(chosen.family_id)
            used_categories.add(chosen.category)

        # Optimize difficulty progression order (EASY -> MEDIUM -> HARD)
        sorted_scenarios, sorted_meta = self.diff_opt.optimize_difficulty_order(selected_scenarios, selected_meta)

        # Validate Constraints
        val_result = self.validator.validate_assessment(sorted_meta, blueprint)

        # Replacement Loop if validation fails
        rep_attempts = 0
        while not val_result.is_valid and rep_attempts < 10:
            rep_attempts += 1
            idx = val_result.offending_slot_index if val_result.offending_slot_index is not None else (rep_attempts % 5)
            existing_ids = set(m.scenario_id for m in sorted_meta)
            existing_fams = set(m.family_id for i, m in enumerate(sorted_meta) if i != idx)
            existing_cats = set(m.category for i, m in enumerate(sorted_meta) if i != idx)

            target_diff = blueprint.slots[idx].target_difficulty if idx < len(blueprint.slots) else "MEDIUM"
            replacements = [
                m for m in all_metadata
                if m.scenario_id not in existing_ids
                and m.family_id not in existing_fams
                and m.category not in existing_cats
            ]
            diff_replacements = [m for m in replacements if m.listening_difficulty == target_diff]
            candidates_to_pick = diff_replacements if diff_replacements else replacements

            if candidates_to_pick:
                rep_choice = rng.choice(candidates_to_pick)
                sorted_meta[idx] = rep_choice
                sorted_scenarios[idx] = all_scenarios[rep_choice.scenario_id]

                sorted_scenarios, sorted_meta = self.diff_opt.optimize_difficulty_order(sorted_scenarios, sorted_meta)
                val_result = self.validator.validate_assessment(sorted_meta, blueprint)
            else:
                break

        # Compute Distributions & Coverage
        coverage_matrix = self.coverage_opt.compute_coverage_matrix(sorted_meta)
        cat_dist = self.coverage_opt.compute_distribution([m.category for m in sorted_meta])
        stk_dist = self.coverage_opt.compute_distribution([m.stakeholder_type.value for m in sorted_meta])
        dec_dist = self.coverage_opt.compute_distribution([m.decision_type.value for m in sorted_meta])
        inter_dist = self.coverage_opt.compute_distribution([m.interaction_type.value for m in sorted_meta])

        logger.info(f"[ASSESSMENT ASSEMBLY ENGINE] Assessment ID: {ass_id} for Candidate: {candidate_id}")
        logger.info(f"  - Total Candidate Pool Size: {len(all_metadata)} scenarios")
        logger.info(f"  - Final Selected Scenarios: {[m.scenario_id for m in sorted_meta]}")
        logger.info(f"  - Selected Scenario Titles: {[m.variant_id for m in sorted_meta]}")
        logger.info(f"  - Constraint Validation Status: {'VALIDATED' if val_result.is_valid else 'WARNING'}")
        comm_dist = self.coverage_opt.compute_distribution([m.communication_style.value for m in sorted_meta])

        diff_curve = [m.listening_difficulty for m in sorted_meta]

        # Audit Report Generation
        timestamp = datetime.now(timezone.utc).isoformat()
        audit_report = AssessmentAuditReport(
            assessment_id=ass_id,
            candidate_id=candidate_id,
            scenario_ids=[m.scenario_id for m in sorted_meta],
            family_ids=[m.family_id for m in sorted_meta],
            construct_coverage_matrix=coverage_matrix,
            category_distribution=cat_dist,
            difficulty_curve=diff_curve,
            stakeholder_distribution=stk_dist,
            decision_type_distribution=dec_dist,
            interaction_distribution=inter_dist,
            communication_distribution=comm_dist,
            constraint_validation_report=val_result.rule_results,
            assembly_timestamp=timestamp,
            assembly_version="1.0.0",
            random_seed=seed,
        )

        return self.builder.build_assessment(
            assessment_id=ass_id,
            candidate_id=candidate_id,
            scenarios=sorted_scenarios,
            metadata_list=sorted_meta,
            coverage_matrix=coverage_matrix,
            audit_report=audit_report,
        )
