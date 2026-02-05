from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError, validator
from models.profile import LinkedInProfile
from models.validation import ValidationResult
from services.profile_validation import ProfileValidationService
from utils.validation import create_standard_error_response
from utils.logging import log_validation_failure


class ProfileAnalysisRequest(BaseModel):
    """
    Request model for profile analysis with validation guards.
    """
    url: str
    role: str  # Now required
    company: Optional[str] = None
    industry: Optional[str] = None
    recent_activity: Optional[str] = None
    tone: str = "FRIENDLY"
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL is required')
        if not v.startswith('https://www.linkedin.com/in/'):
            raise ValueError('URL must be a valid LinkedIn profile URL')
        return v
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['FRIENDLY', 'DIRECT', 'AUTHORITY', 'CASUAL']
        if v.upper() not in valid_tones:
            raise ValueError(f'Tone must be one of {valid_tones}')
        return v.upper()


def validate_profile_for_analysis(profile_data: Dict[str, Any]) -> tuple[Optional[LinkedInProfile], Optional[Dict[str, Any]]]:
    """
    Validates profile data before analysis to ensure it meets minimum requirements.
    
    Args:
        profile_data: Dictionary containing profile information
        
    Returns:
        Tuple of (LinkedInProfile object if valid, error response if invalid)
    """
    try:
        # Create a ProfileAnalysisRequest to validate basic fields
        request = ProfileAnalysisRequest(**profile_data)
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append(f"{error['loc'][0]}: {error['msg']}")
        
        error_msg = f"Invalid input: {', '.join(error_details)}"
        return None, create_standard_error_response(
            error_msg,
            "Please provide a valid LinkedIn URL and ensure tone is one of: FRIENDLY, DIRECT, AUTHORITY, CASUAL"
        )
    
    # Create LinkedInProfile from validated data
    profile = LinkedInProfile(
        url=request.url,
        role=request.role,
        company=request.company,
        industry=request.industry,
        recent_activity=request.recent_activity,
        tone=request.tone
    )
    
    # Use ProfileValidationService to check for completeness
    validation_service = ProfileValidationService()
    validation_result: ValidationResult = validation_service.validate_profile_completeness(profile)
    
    if not validation_result.is_valid:
        # Log the validation failure
        # Handle both object attributes and dictionary keys
        profile_url = getattr(profile, 'url', None) or (profile.get('url') if isinstance(profile, dict) else '')
        profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
        profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
        profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

        profile_data_for_log = {
            "url": profile_url,
            "role": profile_role,
            "company": profile_company,
            "industry": profile_industry
        }
        log_validation_failure(profile_data_for_log, validation_result.errors)
        
        error_msg = f"Profile validation failed: {', '.join(validation_result.errors)}"
        actionable_alt = "Please provide role, and either company or industry information for better results"
        
        return None, create_standard_error_response(error_msg, actionable_alt)
    
    return profile, None