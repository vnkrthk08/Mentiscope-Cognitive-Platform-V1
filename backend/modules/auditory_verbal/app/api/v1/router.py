from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.scenarios import router as scenarios_router
from app.api.v1.listening import router as listening_router
from app.api.v1.speaking import router as speaking_router
from app.api.v1.transcripts import router as transcripts_router
from app.api.v1.reports import router as reports_router
from app.api.v1.research import router as research_router

# S4 Identity Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router

# S5 Media Routers
from app.api.v1.media import router as media_router

# S6 Speech Routers
from app.api.v1.speech import router as speech_router

# S7 Prompt Routers
from app.api.v1.prompt import router as prompt_router

# S8 Behavior Routers
from app.api.v1.behavior import router as behavior_router

# S9 Construct Routers
from app.api.v1.construct import router as construct_router

# S10 Assessment Routers
from app.api.v1.assessment import router as assessment_router

# Phase 12 RAIP Analytics Router
from app.api.v1.analytics import router as analytics_router

# Phase 13 MGEP Governance Router
from app.api.v1.governance import router as governance_router

# Phase 14 ACTP Audit Router
from app.api.v1.audit import router as audit_router

# Phase 15 POSRP Operations Router
from app.api.v1.operations import router as operations_router

# Phase 18 Verification Router
from app.api.v1.verification import router as verification_router

api_v1_router = APIRouter()

# Register API v1 sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(assessments_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(scenarios_router)
api_v1_router.include_router(listening_router)
api_v1_router.include_router(speaking_router)
api_v1_router.include_router(transcripts_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(research_router)

# Register Identity S4 routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(roles_router)
api_v1_router.include_router(permissions_router)

# Register Media S5 routers
api_v1_router.include_router(media_router)

# Register Speech S6 routers
api_v1_router.include_router(speech_router)

# Register Prompt S7 routers
api_v1_router.include_router(prompt_router)

# Register Behavior S8 routers
api_v1_router.include_router(behavior_router)

# Register Construct S9 routers
api_v1_router.include_router(construct_router)

# Register Assessment S10 routers
api_v1_router.include_router(assessment_router)

# Register RAIP Phase 12 Analytics router
api_v1_router.include_router(analytics_router)

# Register MGEP Phase 13 Governance router
api_v1_router.include_router(governance_router)

# Register ACTP Phase 14 Audit router
api_v1_router.include_router(audit_router)

# Register POSRP Phase 15 Operations router
api_v1_router.include_router(operations_router)

# Register Phase 18 Verification router
api_v1_router.include_router(verification_router)




