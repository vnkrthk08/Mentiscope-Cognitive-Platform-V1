from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from modules.quantitative.database.database import get_db

from modules.quantitative.schemas.session import (
    SessionStartRequest,
    SessionStartResponse,
)

from modules.quantitative.services.session_service import SessionService

router = APIRouter(
    tags=["Assessment"],
)


GQ_QUESTIONS_LIST = [
    {
        "id": "gq-1",
        "question_id": "gq-1",
        "text": "If a train travels 360 km in 4 hours, and then increases its speed by 25% for the next 3 hours, what is the total distance covered?",
        "story": "Speed, Distance & Acceleration Rates: Compute composite kinematics across piecewise velocity stages.",
        "options": ["630 km", "675 km", "697.5 km", "720 km"],
        "correctAnswer": "697.5 km",
        "correct_answer": "697.5 km",
        "hint": "Initial speed = 360 / 4 = 90 km/h. Increased speed = 90 × 1.25 = 112.5 km/h. Distance in next 3 hours = 112.5 × 3 = 337.5 km. Total = 360 + 337.5 = 697.5 km.",
        "type": "choice",
        "difficulty": 1
    },
    {
        "id": "gq-2",
        "question_id": "gq-2",
        "text": "A merchant marks an item 40% above its cost price and subsequently offers a 20% discount on the marked price. What is the net profit percentage?",
        "story": "Proportional Calculus & Pricing Margins: Evaluate multi-stage percentage transformations.",
        "options": ["10%", "12%", "16%", "20%"],
        "correctAnswer": "12%",
        "correct_answer": "12%",
        "hint": "Assume cost is 100. Marked price = 140. Selling price = 140 × 0.80 = 112. Net gain = 12%.",
        "type": "choice",
        "difficulty": 2
    },
    {
        "id": "gq-3",
        "question_id": "gq-3",
        "text": "If 5 automated units take 5 minutes to manufacture 5 microchips, how many minutes will it take 100 automated units to manufacture 100 microchips?",
        "story": "Parallel Work Rate & Scaling: Deduce single-worker throughput invariant under parallel scale.",
        "options": ["100 minutes", "50 minutes", "5 minutes", "25 minutes"],
        "correctAnswer": "5 minutes",
        "correct_answer": "5 minutes",
        "hint": "Each unit independently produces 1 microchip every 5 minutes. 100 units operating simultaneously produce 100 chips in the exact same 5 minutes.",
        "type": "choice",
        "difficulty": 2
    },
    {
        "id": "gq-4",
        "question_id": "gq-4",
        "text": "A precision clock shows 3:15. What is the acute angle between the hour hand and the minute hand?",
        "story": "Rotational Kinematics & Angular Velocity: Track differential clock hand velocities.",
        "options": ["0 degrees", "7.5 degrees", "15 degrees", "22.5 degrees"],
        "correctAnswer": "7.5 degrees",
        "correct_answer": "7.5 degrees",
        "hint": "At 15 minutes, the minute hand points directly at 3 (90°). The hour hand advances 0.5° per minute, so at 15 min it is at 90° + (15 × 0.5°) = 97.5°. Angle = 97.5° - 90° = 7.5°.",
        "type": "choice",
        "difficulty": 3
    },
    {
        "id": "gq-5",
        "question_id": "gq-5",
        "text": "In a container of 24 components, the ratio of blue to green components is 3:5. How many blue components must be added so the ratio becomes 1:1?",
        "story": "Ratio Invariants & Mixture Adjustment: Balance discrete component ratios.",
        "options": ["4", "6", "8", "10"],
        "correctAnswer": "6",
        "correct_answer": "6",
        "hint": "8 parts = 24, so each part is 3. Blue = 9, Green = 15. To achieve parity (1:1), Blue must equal Green (15). Added blue = 15 - 9 = 6.",
        "type": "choice",
        "difficulty": 3
    }
]

@router.post(
    "/start",
    response_model=SessionStartResponse,
)
def start_assessment(
    request: SessionStartRequest,
    db: Session = Depends(get_db),
):
    session, question = SessionService.create_session(
        db,
        request,
    )

    return SessionStartResponse(
        status="success",
        assessment_id=session.id,
        student_id=session.student_id,
        session_id=session.session_id,
        started_at=session.started_at,
        totalQuestions=len(GQ_QUESTIONS_LIST),
        questions=GQ_QUESTIONS_LIST,
        question=None
    )