from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger
from app.core.constants import HEADER_REQUEST_ID, HEADER_CORRELATION_ID


class APIException(Exception):
    """Base HTTP API exception with structured error detail."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Internal Server Error",
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    request_id = request.headers.get(HEADER_REQUEST_ID, "N/A")
    correlation_id = request.headers.get(HEADER_CORRELATION_ID, "N/A")

    logger.warning(
        f"[API EXCEPTION] {exc.error_code} ({exc.status_code}): {exc.message}",
        extra={"request_id": request_id, "correlation_id": correlation_id},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "request_id": request_id,
            "path": request.url.path,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = request.headers.get(HEADER_REQUEST_ID, "N/A")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "request_id": request_id,
            "path": request.url.path,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = request.headers.get(HEADER_REQUEST_ID, "N/A")

    logger.warning(
        f"[VALIDATION ERROR] Request body/query validation failed for path '{request.url.path}'",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "ERROR",
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation error",
            "details": {"errors": exc.errors()},
            "request_id": request_id,
            "path": request.url.path,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get(HEADER_REQUEST_ID, "N/A")

    logger.error(
        f"[UNHANDLED EXCEPTION] Internal server error on '{request.url.path}': {str(exc)}",
        exc_info=True,
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "ERROR",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please contact system support.",
            "request_id": request_id,
            "path": request.url.path,
        },
    )
