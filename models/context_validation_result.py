from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ContextValidationResult(BaseModel):
    """
    Stores the results of context validation for a LinkedIn profile.
    """
    profile_id: str  # Reference to the LinkedInProfile
    context_depth_score: int  # Calculated context depth score (0-4)
    validation_passed: bool  # Whether the profile passed context validation
    missing_fields: List[str]  # List of required fields that are missing
    anchor_point: Optional[str] = None  # Selected anchor point for outreach
    generation_mode: str  # Mode selected based on context depth (Precision, Safe Personalization, Exploratory)
    validation_timestamp: datetime = datetime.now()  # When the validation was performed

    def __init__(self, **data):
        super().__init__(**data)
        # Validate context_depth_score is between 0 and 4 inclusive
        if not 0 <= data.get('context_depth_score', 0) <= 4:
            raise ValueError("context_depth_score must be between 0 and 4 inclusive")
        
        # Validate generation_mode is one of the allowed values
        allowed_modes = ["Precision", "Safe Personalization", "Exploratory"]
        if data.get('generation_mode') not in allowed_modes:
            raise ValueError(f"generation_mode must be one of {allowed_modes}")