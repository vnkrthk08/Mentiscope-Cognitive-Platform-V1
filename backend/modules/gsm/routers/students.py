"""
ASAT â€“ Student Routes

Translated from: backend/routes/students.js
Same CRUD operations, same SQL logic, same response shapes.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from modules.gsm.database import get_db
from modules.gsm.schemas import Student, Score
from modules.gsm.models import StudentCreateRequest, StudentCreateResponse

logger = logging.getLogger("asat.students")
router = APIRouter(prefix="/api/students", tags=["Students"])


@router.post("", response_model=StudentCreateResponse, status_code=201)
async def create_student(
    payload: StudentCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create student on registration.
    Translated from: POST /api/students in students.js
    """
    if not payload.fullName or not payload.studentId:
        raise HTTPException(status_code=400, detail="Full name and student ID are required.")

    # Check duplicate â€” same logic as original
    result = await db.execute(
        select(Student).where(Student.student_id_number == payload.studentId)
    )
    existing = result.scalar_one_or_none()
    if existing:
        # Return existing (allow retakes) â€” same behavior as original
        return StudentCreateResponse(
            studentId=existing.student_id,
            message="Student already registered.",
        )

    faculty_id = request.session.get("faculty_id")

    student = Student(
        faculty_id=faculty_id,
        full_name=payload.fullName,
        student_id_number=payload.studentId,
        age=payload.age,
        grade=payload.grade,
        school=payload.school,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)

    logger.info(
        f'[students/create] Registered student_id={student.student_id} '
        f'name="{payload.fullName}" enrollment={payload.studentId}'
    )
    return StudentCreateResponse(studentId=student.student_id, message="Student registered.")


@router.get("")
async def list_students(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    List all students with latest scores (faculty only).
    Translated from: GET /api/students in students.js
    """
    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    # Same logic: get all students, LEFT JOIN latest score
    result = await db.execute(
        select(Student).order_by(desc(Student.created_at))
    )
    students = result.scalars().all()

    student_list = []
    for s in students:
        # Get latest score for this student
        score_result = await db.execute(
            select(Score)
            .where(Score.student_id == s.student_id)
            .order_by(desc(Score.created_at))
            .limit(1)
        )
        score = score_result.scalar_one_or_none()

        student_list.append({
            "studentId": s.student_id,
            "fullName": s.full_name,
            "studentIdNumber": s.student_id_number,
            "grade": s.grade,
            "age": s.age,
            "school": s.school,
            "createdAt": s.created_at.isoformat() if s.created_at else None,
            "overall": score.overall_score if score else None,
            "completedAt": score.created_at.isoformat() if score and score.created_at else None,
        })

    logger.info(f"[students/list] Returning {len(student_list)} students to faculty {faculty_id}")
    return {"students": student_list}


@router.get("/{student_id}")
async def get_student(
    student_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get single student with scores and module results.
    Translated from: GET /api/students/:id in students.js
    """
    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    result = await db.execute(
        select(Student).where(Student.student_id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Get latest score â€” same query as original
    score_result = await db.execute(
        select(Score)
        .where(Score.student_id == student_id)
        .order_by(desc(Score.created_at))
        .limit(1)
    )
    score = score_result.scalar_one_or_none()

    # Build response â€” same shape as original
    student_data = {
        "studentId": student.student_id,
        "fullName": student.full_name,
        "studentIdNumber": student.student_id_number,
        "age": student.age,
        "grade": student.grade,
        "school": student.school,
        "createdAt": student.created_at.isoformat() if student.created_at else None,
    }

    scores_data = {}
    module_results = {}

    if score:
        scores_data = {
            "sustainedScore": score.sustained_score,
            "selectiveScore": score.selective_score,
            "dividedScore": score.divided_score,
            "executiveScore": score.executive_score,
            "overallScore": score.overall_score,
            "percentile": score.percentile,
            "completedAt": score.created_at.isoformat() if score.created_at else None,
        }
        # module_results is already a dict from JSONB â€” no JSON.parse needed
        # (Unlike the MySQL version which needed typeof check)
        module_results = score.module_results or {}

    return {"student": student_data, "scores": scores_data, "moduleResults": module_results}
