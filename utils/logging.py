import logging
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
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
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
