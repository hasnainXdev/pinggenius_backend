from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # Database settings
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongodb_database: str = "test"

    # API settings
    api_key: Optional[str] = None
    apify_api_key: Optional[str] = os.getenv("APIFY_API_KEY")

    # AI service settings
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "sk-...")

    # Rate limiting
    requests_per_minute: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))

    # Application settings
    app_name: str = "PingGenius LinkedIn Outreach"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Additional settings from .env
    serpapi_api_key: Optional[str] = os.getenv("SERPAPI_API_KEY")
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    resend_api_key: Optional[str] = os.getenv("RESEND_API_KEY")
    smtp_email: Optional[str] = os.getenv("SMTP_EMAIL")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")

    class Config:
        env_file = ".env"


settings = Settings()
