from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled exceptions across all API endpoints and formats a clean JSON error response."""
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred within the assessment engine.",
            "path": request.url.path,
        },
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Formats validation / value error responses."""
    logger.warning(f"Validation Error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "BadRequest",
            "message": str(exc),
            "path": request.url.path,
        },
    )
