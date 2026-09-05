"""
CSV Exporter for PVCSF research datasets.

Writes one row per ValidationDataset to a CSV file using pandas.
All nested JSON structures are serialised as string columns to
preserve full traceability in spreadsheet tools.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from app.domain.research.entities.validation_dataset import ValidationDataset


class CSVExporter:
    """Exports ValidationDatasets to CSV format using pandas."""

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
        """
        Write datasets to a CSV file.

        Returns: (file_path, file_size_bytes, sha256_checksum)
        """
        rows = []
        for ds in datasets:
            row = ds.to_flat_dict()
            # Optionally strip large columns based on export options
            if not include_transcripts:
                row["transcript_text"] = "[EXCLUDED]"
            if not include_evidence:
                row["behavior_evidence_json"] = "[]"
            if not include_expert_reviews:
                row["expert_ratings_json"] = "{}"
                row["reviewer_notes"] = ""
            if not include_construct_mappings:
                row["construct_evaluations_json"] = "[]"
            rows.append(row)

        df = pd.DataFrame(rows)

        # Ensure column order is consistent
        priority_cols = [
            "dataset_id", "candidate_id", "assessment_id", "scenario_id",
            "session_id", "dataset_status", "review_status",
            "ai_composite_score", "score_confidence",
        ]
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]

        file_path = self._base_dir / f"research_export_{export_id}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

        file_size = os.path.getsize(file_path)
        checksum = self._compute_checksum(file_path)

        return file_path, file_size, checksum

    def _compute_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
