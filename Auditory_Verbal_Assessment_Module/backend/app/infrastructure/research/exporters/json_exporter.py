"""
JSON Exporter for PVCSF research datasets.

Writes datasets as a structured JSON document preserving full
nested traceability (behavior_evidence, construct_evaluations,
evidence_references, expert_ratings).

Format:
{
  "export_id": "...",
  "exported_at": "...",
  "record_count": N,
  "datasets": [ ... ValidationDataset dicts ... ]
}
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.domain.research.entities.validation_dataset import ValidationDataset


class JSONExporter:
    """Exports ValidationDatasets to structured JSON format."""

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
        """Write datasets to a JSON file."""

        records = []
        for ds in datasets:
            record: Dict[str, Any] = {
                "dataset_id": ds.dataset_id,
                "candidate_id": ds.candidate_id,
                "assessment_id": ds.assessment_id,
                "scenario_id": ds.scenario_id,
                "session_id": ds.session_id,
                "dataset_status": ds.status,
                "review_status": ds.review_status,
                "ai_composite_score": ds.ai_composite_score,
                "score_confidence": ds.score_confidence,
                "normalization_method": ds.normalization_method,
                "ai_framework_scores": ds.ai_framework_scores,
                "behavior_confidence": ds.behavior_confidence,
                "observation_count": ds.observation_count,
                "frameworks_evaluated": ds.frameworks_evaluated,
                "created_at": ds.created_at.isoformat(),
                "updated_at": ds.updated_at.isoformat(),
                "metadata": ds.metadata.to_dict() if ds.metadata else {},
            }

            if include_transcripts:
                record["transcript_text"] = ds.transcript_text
                record["transcript_confidence"] = ds.transcript_confidence
                record["audio_asset_id"] = ds.audio_asset_id
                record["audio_duration_seconds"] = ds.audio_duration_seconds

            if include_evidence:
                record["behavior_evidence"] = ds.behavior_evidence

            if include_construct_mappings:
                record["construct_evaluations"] = ds.construct_evaluations
                record["construct_confidence_scores"] = ds.construct_confidence_scores
                record["evidence_references"] = ds.evidence_references

            if include_expert_reviews:
                record["expert_ratings"] = ds.expert_ratings
                record["reviewer_notes"] = ds.reviewer_notes

            records.append(record)

        payload = {
            "export_id": export_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "record_count": len(records),
            "datasets": records,
        }

        file_path = self._base_dir / f"research_export_{export_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        file_size = os.path.getsize(file_path)
        checksum = self._compute_checksum(file_path)

        return file_path, file_size, checksum

    def _compute_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
