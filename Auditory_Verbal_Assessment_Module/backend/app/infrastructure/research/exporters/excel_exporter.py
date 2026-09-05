"""
Excel Exporter for PVCSF research datasets.

Writes datasets to a multi-sheet Excel workbook using pandas + openpyxl:
  - Sheet 1: Datasets (one row per record, flat)
  - Sheet 2: Construct Scores (one row per construct per dataset)
  - Sheet 3: Behavior Evidence (one row per observation per dataset)
  - Sheet 4: Expert Reviews (one row per review per dataset)
  - Sheet 5: Export Metadata

This multi-sheet structure is optimised for use in statistical
analysis tools (SPSS, R, Python) by researchers.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from app.domain.research.entities.validation_dataset import ValidationDataset


class ExcelExporter:
    """Exports ValidationDatasets to a multi-sheet Excel workbook."""

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)

    async def write(
        self,
        export_id: str,
        datasets: List[ValidationDataset],
        include_evidence: bool = True,
        include_transcripts: bool = True,
        include_expert_reviews: bool = True,
        include_construct_mappings: bool = True,
    ) -> Tuple[Path, int, Optional[str]]:
        """Write datasets to an Excel workbook."""

        file_path = self._base_dir / f"research_export_{export_id}.xlsx"

        with pd.ExcelWriter(str(file_path), engine="openpyxl") as writer:
            # ── Sheet 1: Datasets ────────────────────────────────────────────
            dataset_rows = []
            for ds in datasets:
                row = ds.to_flat_dict()
                if not include_transcripts:
                    row["transcript_text"] = "[EXCLUDED]"
                if not include_evidence:
                    row["behavior_evidence_json"] = "[]"
                if not include_expert_reviews:
                    row["expert_ratings_json"] = "{}"
                    row["reviewer_notes"] = ""
                if not include_construct_mappings:
                    row["construct_evaluations_json"] = "[]"
                dataset_rows.append(row)
            pd.DataFrame(dataset_rows).to_excel(
                writer, sheet_name="Datasets", index=False
            )

            # ── Sheet 2: Construct Scores ────────────────────────────────────
            if include_construct_mappings:
                construct_rows = []
                for ds in datasets:
                    for construct, score in ds.ai_framework_scores.items():
                        expert_score = ds.expert_ratings.get(construct, None)
                        construct_rows.append({
                            "dataset_id": ds.dataset_id,
                            "candidate_id": ds.candidate_id,
                            "construct": construct,
                            "ai_score": score,
                            "expert_score": expert_score,
                            "delta": round(score - expert_score, 4) if expert_score is not None else None,
                            "confidence": ds.construct_confidence_scores.get(construct, 0.0),
                        })
                if construct_rows:
                    pd.DataFrame(construct_rows).to_excel(
                        writer, sheet_name="ConstructScores", index=False
                    )

            # ── Sheet 3: Behavior Evidence ───────────────────────────────────
            if include_evidence:
                evidence_rows = []
                for ds in datasets:
                    for obs in ds.behavior_evidence:
                        evidence_rows.append({
                            "dataset_id": ds.dataset_id,
                            "candidate_id": ds.candidate_id,
                            "construct": obs.get("construct", ""),
                            "quote": obs.get("quote", ""),
                            "indicator": obs.get("indicator", ""),
                            "confidence": obs.get("confidence", 0.0),
                            "polarity": obs.get("polarity", ""),
                            "evidence_type": obs.get("evidence_type", ""),
                        })
                if evidence_rows:
                    pd.DataFrame(evidence_rows).to_excel(
                        writer, sheet_name="BehaviorEvidence", index=False
                    )

            # ── Sheet 4: Expert Reviews ──────────────────────────────────────
            if include_expert_reviews:
                review_rows = []
                for ds in datasets:
                    if ds.expert_ratings:
                        review_rows.append({
                            "dataset_id": ds.dataset_id,
                            "candidate_id": ds.candidate_id,
                            "review_status": ds.review_status,
                            "reviewer_notes": ds.reviewer_notes,
                            "expert_ratings_json": json.dumps(ds.expert_ratings),
                        })
                if review_rows:
                    pd.DataFrame(review_rows).to_excel(
                        writer, sheet_name="ExpertReviews", index=False
                    )

            # ── Sheet 5: Export Metadata ─────────────────────────────────────
            meta_rows = [{
                "export_id": export_id,
                "record_count": len(datasets),
                "include_evidence": include_evidence,
                "include_transcripts": include_transcripts,
                "include_expert_reviews": include_expert_reviews,
                "include_construct_mappings": include_construct_mappings,
                "pvcsf_version": "1.0.0",
                "note": (
                    "Statistical analysis (ICC, Cronbach Alpha, Factor Analysis) "
                    "must be performed externally by qualified psychologists."
                ),
            }]
            pd.DataFrame(meta_rows).to_excel(
                writer, sheet_name="ExportMetadata", index=False
            )

        file_size = os.path.getsize(file_path)
        checksum = self._compute_checksum(file_path)

        return file_path, file_size, checksum

    def _compute_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
