import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime

try:
    from .database import get_db
    from .core_models import UserRecord
except (ImportError, ValueError):
    from database import get_db
    from core_models import UserRecord

router = APIRouter()


class StudentRegisterRequest(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    age: Optional[int] = 21
    gender: Optional[str] = "Male"
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = "Chennai"
    education: Optional[str] = "Undergraduate"
    course: Optional[str] = "Bachelor of Science"
    specialization: Optional[str] = "Cognitive Science"
    previousExamPercentage: Optional[float] = 88.0
    collegeType: Optional[str] = "Private"


class StudentLoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    rememberMe: Optional[bool] = True


class UpdateProfileRequest(BaseModel):
    id: str
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    education: Optional[str] = None
    course: Optional[str] = None
    specialization: Optional[str] = None
    previousExamPercentage: Optional[float] = None
    collegeType: Optional[str] = None


def ensure_default_users(db: Session):
    demo_email = "alex.mercer@candidate.edu"
    existing = db.query(UserRecord).filter(UserRecord.email == demo_email).first()
    if not existing:
        demo_user = UserRecord(
            id="stud_alex_mercer",
            email=demo_email,
            name="Alex Mercer",
            role="student",
            age=21,
            gender="Male",
            state="Tamil Nadu",
            district="Chennai",
            education="Undergraduate",
            course="Bachelor of Science",
            specialization="Psychology",
            previous_exam_percentage=88.0,
            college_type="Private",
            created_at=datetime.utcnow()
        )
        db.add(demo_user)
        db.commit()


@router.post("/register")
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    existing = db.query(UserRecord).filter(UserRecord.email == email_clean).first()
    if existing:
        # Update existing profile with newly registered details
        existing.name = payload.name.strip()
        existing.age = payload.age
        existing.gender = payload.gender
        existing.state = payload.state
        existing.district = payload.district
        existing.education = payload.education
        existing.course = payload.course
        existing.specialization = payload.specialization
        existing.previous_exam_percentage = payload.previousExamPercentage
        existing.college_type = payload.collegeType
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {
            "id": existing.id,
            "name": existing.name,
            "email": existing.email,
            "role": existing.role,
            "age": existing.age,
            "gender": existing.gender,
            "state": existing.state,
            "district": existing.district,
            "education": existing.education,
            "course": existing.course,
            "specialization": existing.specialization,
            "previousExamPercentage": existing.previous_exam_percentage,
            "collegeType": existing.college_type,
            "token": f"jwt_{existing.id}_active_session"
        }

    user_id = f"stud_{uuid.uuid4().hex[:8]}"
    new_user = UserRecord(
        id=user_id,
        email=email_clean,
        name=payload.name.strip(),
        role="student",
        age=payload.age,
        gender=payload.gender,
        state=payload.state,
        district=payload.district,
        education=payload.education,
        course=payload.course,
        specialization=payload.specialization,
        previous_exam_percentage=payload.previousExamPercentage,
        college_type=payload.collegeType,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "age": new_user.age,
        "gender": new_user.gender,
        "state": new_user.state,
        "district": new_user.district,
        "education": new_user.education,
        "course": new_user.course,
        "specialization": new_user.specialization,
        "previousExamPercentage": new_user.previous_exam_percentage,
        "collegeType": new_user.college_type,
        "token": f"jwt_{new_user.id}_active_session"
    }


@router.post("/login")
def login_student(payload: StudentLoginRequest, db: Session = Depends(get_db)):
    ensure_default_users(db)
    email_clean = payload.email.strip().lower()
    existing = db.query(UserRecord).filter(UserRecord.email == email_clean).first()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Account not found. Please enter your registered email or create a new account to take the test."
        )

    return {
        "id": existing.id,
        "name": existing.name,
        "email": existing.email,
        "role": existing.role,
        "age": existing.age,
        "gender": existing.gender,
        "state": existing.state,
        "district": existing.district,
        "education": existing.education,
        "course": existing.course,
        "specialization": existing.specialization,
        "previousExamPercentage": existing.previous_exam_percentage,
        "collegeType": existing.college_type,
        "token": f"jwt_{existing.id}_active_session"
    }


@router.post("/profile")
def update_profile(payload: UpdateProfileRequest, db: Session = Depends(get_db)):
    existing = db.query(UserRecord).filter(UserRecord.id == payload.id).first()
    if not existing:
        existing = db.query(UserRecord).filter(UserRecord.email == payload.email.strip().lower()).first()

    if not existing:
        raise HTTPException(status_code=404, detail="User account record not found.")

    existing.name = payload.name.strip()
    existing.age = payload.age
    existing.gender = payload.gender
    existing.state = payload.state
    existing.district = payload.district
    existing.education = payload.education
    existing.course = payload.course
    existing.specialization = payload.specialization
    existing.previous_exam_percentage = payload.previousExamPercentage
    existing.college_type = payload.collegeType
    existing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing)

    return {
        "id": existing.id,
        "name": existing.name,
        "email": existing.email,
        "role": existing.role,
        "age": existing.age,
        "gender": existing.gender,
        "state": existing.state,
        "district": existing.district,
        "education": existing.education,
        "course": existing.course,
        "specialization": existing.specialization,
        "previousExamPercentage": existing.previous_exam_percentage,
        "collegeType": existing.college_type,
        "token": f"jwt_{existing.id}_active_session"
    }
