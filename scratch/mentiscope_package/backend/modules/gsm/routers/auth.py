"""
ASAT â€“ Auth Routes: Faculty Register / Login / Logout / Me

Translated from: backend/routes/auth.js
Same business logic: bcrypt hashing, session-based auth.

NOTE: We preserve the existing session-cookie authentication flow.
      No JWT is introduced unless required by the MentiScope platform.
      We use Starlette's SessionMiddleware (cookie-based) as the
      equivalent of Express express-session.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from modules.gsm.database import get_db
from modules.gsm.schemas import Faculty
from modules.gsm.models import (
    FacultyRegisterRequest, FacultyRegisterResponse,
    FacultyLoginRequest, FacultyLoginResponse,
    FacultyOut, MessageResponse,
)

logger = logging.getLogger("asat.auth")
router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=FacultyRegisterResponse, status_code=201)
async def register_faculty(
    payload: FacultyRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new faculty account.
    Translated from: POST /api/auth/register in auth.js
    """
    if not payload.username or not payload.password or not payload.email or not payload.fullName:
        raise HTTPException(status_code=400, detail="All fields are required.")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    # Check duplicate
    result = await db.execute(
        select(Faculty).where(
            (Faculty.username == payload.username) | (Faculty.email == payload.email)
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already exists.")

    # Hash password â€” same bcrypt logic as original
    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt(10))

    faculty = Faculty(
        username=payload.username,
        password_hash=hashed.decode("utf-8"),
        full_name=payload.fullName,
        email=payload.email,
    )
    db.add(faculty)
    await db.commit()
    await db.refresh(faculty)

    logger.info(f"[auth/register] Faculty created: id={faculty.faculty_id} username={payload.username}")
    return FacultyRegisterResponse(message="Faculty account created.", facultyId=faculty.faculty_id)


@router.post("/login", response_model=FacultyLoginResponse)
async def login_faculty(
    payload: FacultyLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Faculty login with bcrypt password verification.
    Translated from: POST /api/auth/login in auth.js
    """
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Username and password required.")

    result = await db.execute(select(Faculty).where(Faculty.username == payload.username))
    faculty = result.scalar_one_or_none()
    if not faculty:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    # Verify password â€” same bcrypt.compare logic
    if not bcrypt.checkpw(payload.password.encode("utf-8"), faculty.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    # Store in session (using Starlette SessionMiddleware)
    request.session["faculty_id"] = faculty.faculty_id
    request.session["faculty_name"] = faculty.full_name

    logger.info(f"[auth/login] Faculty logged in: id={faculty.faculty_id}")
    return FacultyLoginResponse(
        message="Login successful.",
        faculty=FacultyOut(
            facultyId=faculty.faculty_id,
            username=faculty.username,
            fullName=faculty.full_name,
            email=faculty.email,
        ),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout_faculty(request: Request):
    """
    Destroy session.
    Translated from: POST /api/auth/logout in auth.js
    """
    request.session.clear()
    return MessageResponse(message="Logged out.")


@router.get("/me")
async def get_current_faculty(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Return current logged-in faculty info.
    Translated from: GET /api/auth/me in auth.js
    """
    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    result = await db.execute(select(Faculty).where(Faculty.faculty_id == faculty_id))
    faculty = result.scalar_one_or_none()
    if not faculty:
        raise HTTPException(status_code=401, detail="Faculty not found.")

    return {
        "faculty": {
            "facultyId": faculty.faculty_id,
            "username": faculty.username,
            "fullName": faculty.full_name,
            "email": faculty.email,
        }
    }
