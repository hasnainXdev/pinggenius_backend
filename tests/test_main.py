from fastapi import FastAPI
from unittest.mock import MagicMock
from api.profile.router import router as profile_router
from api.outreach.router import router as outreach_router
from config.settings import settings
from utils.logging import setup_logging, add_error_handlers, add_middleware
from utils.rate_limiting import add_rate_limiting_middleware
from database.mongo import mongodb


def create_test_app() -> FastAPI:
    # Mock the MongoDB connection before creating the app
    mongodb.client = MagicMock()
    mongodb.database = MagicMock()

    # Mock the connect method to do nothing
    def mock_connect():
        pass

    mongodb.connect = mock_connect

    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Setup logging
    setup_logging()

    # Add middleware
    add_middleware(app)

    # Add rate limiting middleware
    add_rate_limiting_middleware(app)

    # Add error handlers
    add_error_handlers(app)

    # Include API routers
    app.include_router(profile_router, prefix="/profile", tags=["profile"])
    app.include_router(outreach_router, prefix="/outreach", tags=["outreach"])

    @app.get("/")
    def read_root():
        return {"message": "PingGenius LinkedIn Outreach API"}

    return app


# Create a test app instance
test_app = create_test_app()