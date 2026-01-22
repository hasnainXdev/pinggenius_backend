from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from models.sequence import OutreachSequence
from models.validation import ValidationResult
from services.profile_validation import ProfileValidationService
from services.tone_validator import ToneValidatorService
from utils.validation import create_standard_error_response


class OutreachGenerationRequest(BaseModel):
    """
    Request model for outreach generation with validation guards.
    """
    profile_id: str
    tone: str = "FRIENDLY"
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class OutreachRefinementRequest(BaseModel):
    """
    Request model for outreach refinement with validation guards.
    """
    sequence_id: str
    message_position: int
    feedback: str
    tone: str = "FRIENDLY"
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


def validate_outreach_generation_request(request_data: Dict[str, Any]) -> tuple[Optional[OutreachGenerationRequest], Optional[Dict[str, Any]]]:
    """
    Validates outreach generation request data.
    
    Args:
        request_data: Dictionary containing request information
        
    Returns:
        Tuple of (OutreachGenerationRequest object if valid, error response if invalid)
    """
    try:
        # Create an OutreachGenerationRequest to validate basic fields
        request = OutreachGenerationRequest(**request_data)
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'unknown'
            msg = error['msg']
            error_details.append(f"{field}: {msg}")
        
        error_msg = f"Invalid input: {', '.join(error_details)}"
        return None, create_standard_error_response(
            error_msg,
            "Please provide a valid profile_id and ensure tone is one of: FRIENDLY, DIRECT, AUTHORITY, CASUAL"
        )
    
    # Validate tone
    valid_tones = ['FRIENDLY', 'DIRECT', 'AUTHORITY', 'CASUAL']
    if request.tone.upper() not in valid_tones:
        return None, create_standard_error_response(
            f"Invalid tone: {request.tone}. Must be one of {valid_tones}",
            "Please use one of the supported tones: FRIENDLY, DIRECT, AUTHORITY, CASUAL"
        )
    
    # Update tone to uppercase for consistency
    request.tone = request.tone.upper()
    
    return request, None


def validate_outreach_refinement_request(request_data: Dict[str, Any]) -> tuple[Optional[OutreachRefinementRequest], Optional[Dict[str, Any]]]:
    """
    Validates outreach refinement request data.
    
    Args:
        request_data: Dictionary containing request information
        
    Returns:
        Tuple of (OutreachRefinementRequest object if valid, error response if invalid)
    """
    try:
        # Create an OutreachRefinementRequest to validate basic fields
        request = OutreachRefinementRequest(**request_data)
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'unknown'
            msg = error['msg']
            error_details.append(f"{field}: {msg}")
        
        error_msg = f"Invalid input: {', '.join(error_details)}"
        return None, create_standard_error_response(
            error_msg,
            "Please provide a valid sequence_id, message_position, feedback, and tone"
        )
    
    # Validate tone
    valid_tones = ['FRIENDLY', 'DIRECT', 'AUTHORITY', 'CASUAL']
    if request.tone.upper() not in valid_tones:
        return None, create_standard_error_response(
            f"Invalid tone: {request.tone}. Must be one of {valid_tones}",
            "Please use one of the supported tones: FRIENDLY, DIRECT, AUTHORITY, CASUAL"
        )
    
    # Validate message position
    if request.message_position < 1 or request.message_position > 4:
        return None, create_standard_error_response(
            f"Invalid message position: {request.message_position}. Must be between 1 and 4",
            "Message position should be between 1 (connection note) and 4 (follow-up 2)"
        )
    
    # Update tone to uppercase for consistency
    request.tone = request.tone.upper()
    
    return request, None


def validate_tone_consistency(messages: Dict[str, str], tone: str) -> tuple[bool, list]:
    """
    Validates that all messages in a sequence adhere to the requested tone.
    
    Args:
        messages: Dictionary of message types and their content
        tone: The requested tone
        
    Returns:
        Tuple of (is_valid, list_of_violations)
    """
    tone_validator = ToneValidatorService()
    all_valid = True
    all_violations = []
    
    for msg_type, message in messages.items():
        is_valid, violations = tone_validator.validate_message_tone(message, tone)
        if not is_valid:
            all_valid = False
            for violation in violations:
                all_violations.append(f"{msg_type}: {violation}")
    
    return all_valid, all_violations


def validate_sequence_structure(sequence: OutreachSequence) -> ValidationResult:
    """
    Validates the structure and content of an outreach sequence.
    
    Args:
        sequence: The outreach sequence to validate
        
    Returns:
        ValidationResult indicating validity and any errors
    """
    errors = []
    warnings = []
    
    # Check required fields
    if not sequence.connection_note:
        errors.append("Connection note is required")
    if not sequence.dm_1:
        errors.append("First direct message is required")
    
    # Check tone consistency
    messages = {
        "connection_note": sequence.connection_note,
        "dm_1": sequence.dm_1,
        "follow_up_1": sequence.follow_up_1 or "",
        "follow_up_2": sequence.follow_up_2 or ""
    }
    
    tone_validator = ToneValidatorService()
    is_tone_valid, tone_violations = validate_tone_consistency(messages, sequence.tone)
    
    if not is_tone_valid:
        errors.extend(tone_violations)
    
    # Check for proper sanitization (no newlines, quotes removed)
    for msg_type, message in messages.items():
        if '\n' in message:
            errors.append(f"{msg_type} contains newline characters")
        if message.count('"') > 2 or message.count("'") > 2:  # Allow some quotes in content
            warnings.append(f"{msg_type} contains multiple quote characters")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )