"""ComparisonService — Granular Diffs for Experiment Runs & Snapshots."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.entities.comparison_report import ComparisonReport
from app.domain.governance.entities.experiment_run import ExperimentRun
from app.infrastructure.governance.repositories import (
    ComparisonReportRepository,
    ExperimentRunRepository,
)


class ComparisonService:
    """Computes comparison diffs across prompts, evidence, scores, latencies, tokens, and costs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._run_repo = ExperimentRunRepository(session)
        self._report_repo = ComparisonReportRepository(session)

    async def compare_runs(
        self,
        experiment_id: str,
        baseline_run_id: Optional[str] = None,
        candidate_run_id: Optional[str] = None,
    ) -> ComparisonReport:
        runs = await self._run_repo.list_by_experiment(experiment_id)

        baseline_run: Optional[ExperimentRun] = None
        candidate_run: Optional[ExperimentRun] = None

        if baseline_run_id and candidate_run_id:
            for r in runs:
                if r.run_id == baseline_run_id:
                    baseline_run = r
                elif r.run_id == candidate_run_id:
                    candidate_run = r
        else:
            # Auto select first BASELINE and CANDIDATE run
            for r in runs:
                if r.run_type == "BASELINE" and not baseline_run:
                    baseline_run = r
                elif r.run_type == "CANDIDATE" and not candidate_run:
                    candidate_run = r

        if not baseline_run or not candidate_run:
            raise ValueError(
                f"Cannot compare experiment '{experiment_id}': requires both BASELINE and CANDIDATE runs."
            )

        report = self.generate_comparison_report(experiment_id, baseline_run, candidate_run)
        await self._report_repo.save(report)
        return report

    def generate_comparison_report(
        self,
        experiment_id: str,
        baseline: ExperimentRun,
        candidate: ExperimentRun,
    ) -> ComparisonReport:
        # 1. Prompt / Transcript diff summary
        transcript_match = baseline.transcript_output == candidate.transcript_output
        prompt_diff = {
            "transcript_match": transcript_match,
            "baseline_len": len(baseline.transcript_output),
            "candidate_len": len(candidate.transcript_output),
            "char_delta": len(candidate.transcript_output) - len(baseline.transcript_output),
        }

        # 2. Evidence diff summary
        b_ev = baseline.behavior_evidence_output or {}
        c_ev = candidate.behavior_evidence_output or {}
        evidence_diff = {
            "baseline_evidence_count": b_ev.get("observations_count", 0),
            "candidate_evidence_count": c_ev.get("observations_count", 0),
            "common_constructs": list(set(b_ev.keys()).intersection(set(c_ev.keys()))),
        }

        # 3. Construct evaluation diff summary
        b_eval = baseline.construct_evaluation_output or {}
        c_eval = candidate.construct_evaluation_output or {}
        eval_diff = {
            "baseline_constructs": list(b_eval.keys()),
            "candidate_constructs": list(c_eval.keys()),
        }

        # 4. Score deltas (candidate - baseline)
        b_scores = baseline.assessment_scores_output or {}
        c_scores = candidate.assessment_scores_output or {}
        score_deltas: Dict[str, float] = {}

        all_keys = set(b_scores.keys()).union(set(c_scores.keys()))
        for k in all_keys:
            b_val = b_scores.get(k, 0.0)
            c_val = c_scores.get(k, 0.0)
            score_deltas[k] = round(c_val - b_val, 4)

        # 5. Latency & Cost deltas
        latency_delta = round(candidate.processing_latency_ms - baseline.processing_latency_ms, 2)
        cost_delta = round(candidate.estimated_cost_usd - baseline.estimated_cost_usd, 6)

        # Overall recommendation logic (advisory tag)
        if any(abs(v) > 5.0 for v in score_deltas.values()):
            recommendation = "SIGNIFICANT_SCORE_CHANGE_REQUIRES_HUMAN_REVIEW"
        elif latency_delta > 500.0:
            recommendation = "PERFORMANCE_REGRESSION_HIGHER_LATENCY"
        else:
            recommendation = "STABLE_IMPROVEMENT"

        return ComparisonReport(
            experiment_id=experiment_id,
            baseline_run_id=baseline.run_id,
            candidate_run_id=candidate.run_id,
            prompt_diff_summary=prompt_diff,
            evidence_diff_summary=evidence_diff,
            evaluation_diff_summary=eval_diff,
            score_deltas=score_deltas,
            latency_delta_ms=latency_delta,
            cost_delta_usd=cost_delta,
            overall_recommendation=recommendation,
        )
