"""
Main API entry point for PingGenius LinkedIn Outreach
Structured for easy Next.js integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import api_v1_router
from config.settings import settings
from utils.logging import setup_logging, add_error_handlers, add_middleware
from utils.rate_limiting import add_rate_limiting_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0",
        description="LinkedIn Outreach Automation API - Designed for Next.js integration"
    )

    # Setup logging
    setup_logging()

    # Add CORS middleware for Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with your Next.js app URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add middleware
    add_middleware(app)

    # Add rate limiting middleware
    add_rate_limiting_middleware(app)

    # Add error handlers
    add_error_handlers(app)

    # Include API v1 routers with consistent response format
    app.include_router(api_v1_router, prefix="/api/v1", tags=["api-v1"])

    @app.get("/")
    def read_root():
        return {
            "success": True,
            "data": {
                "message": "PingGenius LinkedIn Outreach API",
                "version": "1.0.0",
                "description": "API for generating personalized LinkedIn outreach sequences",
                "endpoints": {
                    "api_v1": {
                        "profile_analyze": "/api/v1/profile/analyze",
                        "get_profile": "/api/v1/profile/{profile_id}",
                        "outreach_generate": "/api/v1/outreach/generate",
                        "outreach_refine": "/api/v1/outreach/refine",
                        "get_sequence": "/api/v1/outreach/{sequence_id}"
                    },
                    "documentation": {
                        "swagger": "/docs",
                        "redoc": "/redoc"
                    },
                    "health": "/health"
                }
            }
        }

    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "service": "PingGenius API",
                "version": "1.0.0"
            }
        }

    return app


app = create_app()