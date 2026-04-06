from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, Union, Dict, Any
from services.profile_scraper import ProfileService
from services.context_extractor import ContextExtractor
from models.profile import LinkedInProfile
from database.mongo import get_db
from bson import ObjectId
import logging
import time
import re

# Import validation components
from services.profile_validation import ProfileValidationService
from api.v1.validators import validate_profile_for_analysis
from utils.validation import create_standard_error_response
from utils.logging import log_validation_failure, log_fallback_message_returned
from services.sequence_generator import TONE_FRIENDLY
from utils.user_friendly_errors import get_user_friendly_error


router = APIRouter()
# profile_service = ProfileService()
context_extractor = ContextExtractor()
profile_validation_service = ProfileValidationService()


class ProfileAnalysisRequest(BaseModel):
    user_id: str  # ID of the user performing the analysis
    url: str
    role: str  # Now required
    company: Optional[str] = None
    industry: Optional[str] = None
    recent_activity: Optional[str] = None
    tone: str = "friendly"
    
    @validator('tone', pre=True)
    def validate_and_convert_profile_tone(cls, v):
        from services.sequence_generator import TONE_DIRECT, TONE_AUTHORITY, TONE_CASUAL
        if isinstance(v, str):
            # Handle different input formats
            if v.lower() == 'friendly':
                return TONE_FRIENDLY
            elif v.lower() == 'direct':
                return TONE_DIRECT
            elif v.lower() == 'authority':
                return TONE_AUTHORITY
            elif v.lower() == 'casual':
                return TONE_CASUAL
            else:
                raise ValueError(f"Tone must be one of ['friendly', 'direct', 'authority', 'casual']")
        return v


class ProfileAnalysisResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    actionable_alternative: Optional[str] = None


@router.post("/analyze", 
             response_model=Union[ProfileAnalysisResponse, ErrorResponse],
             responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_linkedin_profile(request: ProfileAnalysisRequest):
    start_time = time.time()

    try:
        # Convert request to dict for validation and processing
        profile_data = request.dict()

        # Validate profile for analysis to ensure it meets minimum requirements
        profile, error_response = validate_profile_for_analysis(profile_data)

        # If validation fails, return a standard error response
        if error_response:
            # Measure response time for error case
            response_time = time.time() - start_time
            if response_time > 1.0:
                logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for validation error")

            return ErrorResponse(
                error="Validation failed",
                message=error_response.get("message", "Profile validation failed"),
                actionable_alternative=error_response.get("actionable_alternative")
            )

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
            "user_id": request.user_id,  # Store the user ID with the profile
            "context": context,
        })

        profile.id = str(result.inserted_id)

        # Measure response time for success case
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for successful analysis")

        return ProfileAnalysisResponse(
            data={
                "id": profile.id,
                "url": profile.url,
                "role": profile.role,
                "company": profile.company,
                "industry": profile.industry,
                "recent_activity": profile.recent_activity,
            }
        )

    except HTTPException as e:
        # Handle HTTP exceptions (like our validation errors)
        # Measure response time for HTTP exceptions
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for HTTP exception")

        return ErrorResponse(
            error="HTTP Exception",
            message=str(e.detail) if hasattr(e, 'detail') else "An HTTP error occurred",
            actionable_alternative="Please check your request and try again"
        )
        
    except Exception as e:
        # Measure response time for general exceptions
        response_time = time.time() - start_time
        if response_time > 1.0:
            logging.warning(f"Response time exceeded 1 second: {response_time:.2f}s for general exception")

        # Get user-friendly error message
        error_msg = str(e)
        friendly_msg, actionable_tip = get_user_friendly_error(error_msg)
        
        # Log the original error for debugging purposes
        logging.error(f"Analyze failed: {e}")
        
        return ErrorResponse(
            error="Error occurred",
            message=friendly_msg,
            actionable_alternative=actionable_tip
        )


@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    """
    Retrieve a profile by ID
    """
    try:
        db = get_db()
        profile_data = db.profiles.find_one({"_id": ObjectId(profile_id)})
        
        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Profile not found",
                    "message": f"Profile with ID {profile_id} does not exist in the system",
                    "actionable_alternative": "Please analyze the LinkedIn profile first using the /profile/analyze endpoint",
                },
            )
        
        # Format the response
        profile_data["id"] = str(profile_data["_id"])
        profile_data.pop("_id")
        
        return ProfileAnalysisResponse(data=profile_data)
        
    except HTTPException as e:
        return ErrorResponse(
            error="Not Found",
            message=str(e.detail) if hasattr(e, 'detail') else "Profile not found",
            actionable_alternative="Please check the profile ID and try again"
        )
    except Exception as e:
        logging.error(f"Error retrieving profile {profile_id}: {e}")
        return ErrorResponse(
            error="Internal server error",
            message="Failed to retrieve profile",
            actionable_alternative="Please try again later or contact support if the issue persists"
        )