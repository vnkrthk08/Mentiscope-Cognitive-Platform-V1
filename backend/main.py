from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core_models import Base
from .database import engine
from .modules.processing_speed.api.router import router as processing_speed_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mentiscope API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(processing_speed_router, prefix="/api/modules/processing-speed", tags=["processing-speed"])


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
