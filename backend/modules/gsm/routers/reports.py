"""
ASAT â€“ Reports Routes (CSV Export)

Translated from: backend/routes/reports.js
Same CSV export logic for faculty dashboard.
"""

import logging
import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from modules.gsm.database import get_db
from modules.gsm.schemas import Student, Score

logger = logging.getLogger("asat.reports")
router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/csv")
async def export_csv(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Export all students with scores as CSV.
    Translated from: GET /api/reports/csv in reports.js
    """
    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    # Same query logic as original
    result = await db.execute(
        select(Student).order_by(desc(Student.created_at))
    )
    students = result.scalars().all()

    headers = [
        "Full Name", "Student ID", "Grade", "Age", "School",
        "Sustained (25%)", "Selective (25%)", "Divided (20%)", "Executive (30%)",
        "Overall Score", "Percentile", "Completed At",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for s in students:
        # Get latest score
        score_result = await db.execute(
            select(Score)
            .where(Score.student_id == s.student_id)
            .order_by(desc(Score.created_at))
            .limit(1)
        )
        score = score_result.scalar_one_or_none()

        writer.writerow([
            s.full_name,
            s.student_id_number,
            s.grade,
            s.age,
            s.school,
            score.sustained_score if score else "",
            score.selective_score if score else "",
            score.divided_score if score else "",
            score.executive_score if score else "",
            score.overall_score if score else "",
            score.percentile if score else "",
            score.created_at.isoformat() if score and score.created_at else "",
        ])

    filename = f"ASAT_Students_{datetime.now().strftime('%Y-%m-%d')}.csv"
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
