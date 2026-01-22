from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.profile_scraper import ProfileService
from services.context_extractor import ContextExtractor
from models.profile import LinkedInProfile
from database.mongo import get_db
from typing import Optional
import logging

# Import validation components
from services.profile_validation import ProfileValidationService
from api.profile.validators import validate_profile_for_analysis
from utils.validation import create_standard_error_response
from utils.logging import log_validation_failure, log_fallback_message_returned

router = APIRouter()
profile_service = ProfileService()
context_extractor = ContextExtractor()
profile_validation_service = ProfileValidationService()


class ProfileAnalysisRequest(BaseModel):
    url: str
    role: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    recent_activity: Optional[str] = None
    tone: str = "FRIENDLY"


class ProfileAnalysisResponse(BaseModel):
    id: Optional[str] = None
    url: str
    role: str
    company: Optional[str] = None
    industry: Optional[str] = None
    recent_activity: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    error: str
    message: str
    actionable_alternative: Optional[str] = None


import time

@router.post("/analyze",
             response_model=ProfileAnalysisResponse,
             responses={422: {"model": ValidationErrorResponse}})
async def analyze_linkedin_profile(request: ProfileAnalysisRequest):
    start_time = time.time()

    try:
        # Convert request to dict for validation
        profile_data = request.dict()

        # Validate profile for analysis to ensure it meets minimum requirements
        profile, error_response = validate_profile_for_analysis(profile_data)

        # If validation fails, return a standard error response
        if error_response:
            # Measure response time for error case
            response_time = time.time() - start_time
            if response_time > 1.0:
                logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for validation error")

            raise HTTPException(status_code=422, detail=error_response)

        # At this point, the profile has passed validation
        # Check if we need to infer a pain point
        inferred_pain_point = profile_validation_service.infer_pain_point(profile)
        if inferred_pain_point:
            profile.pain_point = inferred_pain_point.description

        # Extract message context
        context = context_extractor.extract_context(
            profile=profile
        )

        if not context_extractor.validate_context(context):
            logging.warning("Insufficient context but proceeding")

        # Save the profile to the database
        db = get_db()
        result = db.profiles.insert_one({
            **profile.dict(),
            "context": context,
        })

        profile.id = str(result.inserted_id)

        # Measure response time for success case
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for successful analysis")

        return ProfileAnalysisResponse(
            id=profile.id,
            url=profile.url,
            role=profile.role,
            company=profile.company,
            industry=profile.industry,
            recent_activity=profile.recent_activity,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like our validation errors)
        # Measure response time for HTTP exceptions
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for HTTP exception")

        raise
    except Exception as e:
        # Measure response time for general exceptions
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for general exception")

        logging.error(f"Analyze failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
