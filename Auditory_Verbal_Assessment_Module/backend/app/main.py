import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.constants import (
    HEADER_REQUEST_ID,
    HEADER_CORRELATION_ID,
    HEADER_PROCESS_TIME,
)
from app.core.lifespan import lifespan
from app.core.exceptions import (
    APIException,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.api.v1.router import api_v1_router


def create_application() -> FastAPI:
    """FastAPI Application Factory."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production API backend for MentiScope Cognitive & Psychological Assessment Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Request ID, Correlation ID & Process Time Middleware
    @app.middleware("http")
    async def add_telemetry_headers(request: Request, call_next):
        start_time = time.time()

        request_id = request.headers.get(HEADER_REQUEST_ID) or str(uuid.uuid4())
        correlation_id = request.headers.get(HEADER_CORRELATION_ID) or request_id

        # Attach request_id to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000.0
        response.headers[HEADER_REQUEST_ID] = request_id
        response.headers[HEADER_CORRELATION_ID] = correlation_id
        response.headers[HEADER_PROCESS_TIME] = f"{process_time:.2f}ms"

        return response

    # 3. Global Exception Handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # 4. Include API v1 Router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
