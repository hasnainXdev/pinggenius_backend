from typing import Dict, List, Any, Optional
from models.validation import ValidationResult, FallbackMessage
from models.profile import LinkedInProfile
from datetime import datetime


def validate_linkedin_profile(profile: LinkedInProfile) -> ValidationResult:
    """
    Validates a LinkedIn profile to ensure it has sufficient information for outreach generation.

    Args:
        profile: The LinkedIn profile to validate (can be object or dict)

    Returns:
        ValidationResult indicating whether the profile is valid and any errors/warnings
    """
    errors = []
    warnings = []
    required_fields_present = {}

    # Handle both object attributes and dictionary keys
    profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
    profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
    profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')

    # Check if role is present and not empty
    if not profile_role or not profile_role.strip():
        errors.append("Role is required for profile analysis")
        required_fields_present["role"] = False
    else:
        required_fields_present["role"] = True

    # Check if either company or industry is present and not empty
    company_present = bool(profile_company and profile_company.strip())
    industry_present = bool(profile_industry and profile_industry.strip())

    required_fields_present["company"] = company_present
    required_fields_present["industry"] = industry_present

    if not company_present and not industry_present:
        errors.append("Either company or industry is required for profile analysis")

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        required_fields_present=required_fields_present
    )


def generate_fallback_message(reason: str) -> FallbackMessage:
    """
    Generates a safe fallback message when profile validation fails to prevent AI hallucination.
    
    Args:
        reason: The reason for returning a fallback message
        
    Returns:
        FallbackMessage with appropriate content
    """
    message_content = ""
    
    if reason == "insufficient_context":
        message_content = (
            "Unable to generate outreach content due to insufficient profile information. "
            "Please provide a role and either company or industry information for better results."
        )
    elif reason == "missing_role":
        message_content = (
            "Role information is required to generate relevant outreach content. "
            "Please provide the person's role or job title."
        )
    elif reason == "missing_company_or_industry":
        message_content = (
            "Company or industry information is required to generate targeted outreach content. "
            "Please provide either company or industry information."
        )
    else:
        message_content = (
            "Unable to generate outreach content due to incomplete profile information. "
            "Please provide a role and either company or industry information."
        )
        
    return FallbackMessage(
        message=message_content,
        reason=reason
    )


def format_validation_errors(validation_result: ValidationResult) -> str:
    """
    Formats validation errors into a user-friendly message.
    
    Args:
        validation_result: The validation result to format
        
    Returns:
        Formatted error message
    """
    if not validation_result.errors:
        return ""
    
    error_list = ", ".join(validation_result.errors)
    return f"Profile validation failed: {error_list}"


def create_standard_error_response(message: str, actionable_alternative: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates a standardized error response for validation failures.

    Args:
        message: The error message
        actionable_alternative: Suggested action to resolve the issue

    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": "Validation failed",
        "message": message
    }

    if actionable_alternative:
        response["actionable_alternative"] = actionable_alternative

    return response


def create_enhanced_error_response(error_type: str, message: str, actionable_alternative: Optional[str] = None,
                                 details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Creates an enhanced standardized error response with additional metadata.

    Args:
        error_type: Type of error (e.g., "VALIDATION_ERROR", "BUSINESS_RULE_VIOLATION")
        message: The error message
        actionable_alternative: Suggested action to resolve the issue
        details: Additional details about the error

    Returns:
        Enhanced standardized error response dictionary
    """
    response = {
        "error_type": error_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

    if actionable_alternative:
        response["actionable_alternative"] = actionable_alternative

    if details:
        response["details"] = details

    return response


def format_validation_errors_detailed(validation_result: ValidationResult) -> Dict[str, Any]:
    """
    Formats validation errors into a detailed response with structured information.

    Args:
        validation_result: The validation result to format

    Returns:
        Dictionary with detailed error information
    """
    if not validation_result.errors:
        return {
            "is_valid": True,
            "errors": [],
            "warnings": validation_result.warnings or []
        }

    return {
        "is_valid": False,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings or [],
        "required_fields_present": validation_result.required_fields_present or {}
    }