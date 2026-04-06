import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from config.settings import settings


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO if not settings.debug else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def add_error_handlers(app: FastAPI):
    """Add error handlers to the application"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        # Log the error with enhanced details
        logging.error(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        # Log the validation error with enhanced details
        logging.error(f"Validation Exception: {exc.errors()} - Path: {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": exc.errors(),
                "status_code": 422,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        # Log the general error with enhanced details
        logging.error(f"General Exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "status_code": 500},
        )


def add_middleware(app: FastAPI):
    """Add middleware to the application"""
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def log_validation_failure(profile_data: dict, validation_errors: list):
    """Log validation failures with enhanced details for monitoring"""
    logging.warning(
        f"Profile validation failed: "
        f"URL={profile_data.get('url', 'unknown')}, "
        f"Role={profile_data.get('role', 'missing')}, "
        f"Company={profile_data.get('company', 'missing')}, "
        f"Industry={profile_data.get('industry', 'missing')}, "
        f"Errors={validation_errors}"
    )


def log_fallback_message_returned(reason: str, profile_url: str):
    """Log when a fallback message is returned instead of generated content"""
    logging.info(
        f"Fallback message returned: "
        f"Reason={reason}, "
        f"Profile_URL={profile_url}, "
        f"Timestamp={datetime.now().isoformat()}"
    )


def log_pain_point_inference(role: str, industry: str, pain_point: str):
    """Log pain point inference for analytics"""
    logging.info(
        f"Pain point inferred: "
        f"Role={role}, "
        f"Industry={industry}, "
        f"Pain_Point={pain_point}, "
        f"Timestamp={datetime.now().isoformat()}"
    )


def log_tone_validation_result(original_message: str, tone: str, is_valid: bool, regenerated: bool = False):
    """Log tone validation results"""
    status = "VALID" if is_valid else "INVALID"
    action = "REGENERATED" if regenerated else "CHECKED"
    logging.info(
        f"Tone validation {status}: "
        f"Tone={tone}, "
        f"Action={action}, "
        f"Status={status}, "
        f"Timestamp={datetime.now().isoformat()}"
    )


def log_timeout_event(operation: str, duration: float, timeout_limit: int):
    """Log timeout events for monitoring"""
    logging.warning(
        f"Timeout event: "
        f"Operation={operation}, "
        f"Duration={duration}s, "
        f"Limit={timeout_limit}s, "
        f"Timestamp={datetime.now().isoformat()}"
    )


def log_idempotency_check(key: str, is_duplicate: bool):
    """Log idempotency checks"""
    status = "DUPLICATE" if is_duplicate else "NEW"
    logging.info(
        f"Idempotency check: "
        f"Key={key}, "
        f"Status={status}, "
        f"Timestamp={datetime.now().isoformat()}"
    )
