from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.profile_scraper import ProfileService
from services.context_extractor import ContextExtractor
from models.profile import LinkedInProfile
from database.mongo import mongodb
from utils.retry import retry_with_backoff
from typing import Optional
import logging

router = APIRouter()
profile_service = ProfileService()
context_extractor = ContextExtractor()


class ProfileAnalysisRequest(BaseModel):
    url: str


class ProfileAnalysisResponse(BaseModel):
    id: Optional[str] = None
    url: str
    role: str
    company: str
    industry: str
    recent_activity: Optional[str] = None


@router.post("/analyze", response_model=ProfileAnalysisResponse)
async def analyze_linkedin_profile(request: ProfileAnalysisRequest):
    """
    Analyze a LinkedIn profile and extract context for message generation
    """
    try:
        # Validate the profile URL
        if not profile_service.validate_profile_url(request.url):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid LinkedIn profile URL",
                    "message": "The provided URL is not a valid LinkedIn profile URL",
                    "actionable_alternative": "Please ensure the URL follows the format: https://www.linkedin.com/in/username",
                },
            )

        # Analyze the profile
        profile: LinkedInProfile = await profile_service.analyze_profile(request.url)

        if (
            not profile
            or profile.role == "Unknown"
            and profile.company == "Unknown"
            and profile.industry == "Unknown"
        ):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Could not analyze the LinkedIn profile",
                    "message": "The profile may be private, inaccessible, or the service is temporarily unavailable",
                    "actionable_alternative": "Please verify the profile is public and accessible, or try again later",
                },
            )

        # Extract context for future message generation
        context = context_extractor.extract_context(profile)

        # Validate the extracted context
        if not context_extractor.validate_context(context):
            logging.warning(
                f"Profile {profile.id} has insufficient information for quality message generation"
            )

        # Store the profile in the database
        db = mongodb.get_database()
        result = db.profiles.insert_one(profile.dict())
        profile.id = str(result.inserted_id)

        # Prepare the response
        response = ProfileAnalysisResponse(
            id=profile.id,
            url=profile.url,
            role=profile.role,
            company=profile.company,
            industry=profile.industry,
            recent_activity=profile.recent_activity,
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Error analyzing profile {request.url}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while analyzing the profile",
                "actionable_alternative": "Please try again later or contact support if the issue persists",
            },
        )
