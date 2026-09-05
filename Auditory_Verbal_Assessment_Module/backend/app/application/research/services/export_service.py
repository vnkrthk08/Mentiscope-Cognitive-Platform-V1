"""
ExportService — Application Service.

Coordinates research dataset export jobs.
Delegates actual file writing to the format-specific exporters
(CSV, JSON, Excel) in the infrastructure layer.

Each export preserves full traceability including evidence
references, construct mappings, and framework scores.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.research.entities.research_export import ResearchExport
from app.domain.research.entities.validation_dataset import ValidationDataset


class ExportService:
    """
    Application service orchestrating dataset export jobs.

    Supports CSV, JSON, and Excel output formats.
    All exports preserve complete pipeline traceability.
    """

    # Exports are written under this base directory (can be overridden in config)
    EXPORT_BASE_DIR: str = "exports/research"

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def create_export_job(
        self,
        export_name: str,
        export_format: str,
        dataset_ids: List[str],
        requested_by: str,
        calibration_batch_id: Optional[str] = None,
        include_evidence: bool = True,
        include_transcripts: bool = True,
        include_expert_reviews: bool = True,
        include_construct_mappings: bool = True,
    ) -> ResearchExport:
        """Factory: create a ResearchExport tracking entity (not yet written)."""
        return ResearchExport(
            export_id=str(uuid.uuid4()),
            export_name=export_name,
            dataset_ids=list(dataset_ids),
            calibration_batch_id=calibration_batch_id,
            export_format=export_format.upper(),
            include_evidence=include_evidence,
            include_transcripts=include_transcripts,
            include_expert_reviews=include_expert_reviews,
            include_construct_mappings=include_construct_mappings,
            requested_by=requested_by,
        )

    async def execute_export(
        self,
        export: ResearchExport,
        datasets: List[ValidationDataset],
    ) -> ResearchExport:
        """
        Execute the export job: write files and update the export entity.

        The actual byte-level writing is delegated to format exporters.
        """
        export.mark_in_progress()

        try:
            Path(self.EXPORT_BASE_DIR).mkdir(parents=True, exist_ok=True)

            if export.export_format == "CSV":
                from app.infrastructure.research.exporters.csv_exporter import CSVExporter
                exporter = CSVExporter(self.EXPORT_BASE_DIR)
            elif export.export_format == "JSON":
                from app.infrastructure.research.exporters.json_exporter import JSONExporter
                exporter = JSONExporter(self.EXPORT_BASE_DIR)
            elif export.export_format == "EXCEL":
                from app.infrastructure.research.exporters.excel_exporter import ExcelExporter
                exporter = ExcelExporter(self.EXPORT_BASE_DIR)
            else:
                raise ValueError(f"Unsupported export format: {export.export_format}")

            file_path, file_size, checksum = await exporter.write(
                export_id=export.export_id,
                datasets=datasets,
                include_evidence=export.include_evidence,
                include_transcripts=export.include_transcripts,
                include_expert_reviews=export.include_expert_reviews,
                include_construct_mappings=export.include_construct_mappings,
            )

            export.mark_completed(
                file_path=str(file_path),
                file_size_bytes=file_size,
                record_count=len(datasets),
                checksum=checksum,
            )

            # Mark each dataset as exported
            for ds in datasets:
                if ds.status == "READY":
                    ds.mark_exported()

            logger.info(
                "[PVCSF ExportService] Export completed",
                export_id=export.export_id,
                format=export.export_format,
                records=len(datasets),
                size_bytes=file_size,
            )

        except Exception as exc:
            export.mark_failed(str(exc))
            logger.error(
                "[PVCSF ExportService] Export failed",
                export_id=export.export_id,
                error=str(exc),
            )
            raise

        return export
