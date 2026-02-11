from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """
    The result of analyzing a LinkedIn profile, including the selected anchor point,
    anchor type, context depth score, generation mode, and analysis details.
    """
    profile_id: str  # Reference to the LinkedInProfile
    selected_anchor: str  # The anchor point selected for outreach
    anchor_type: str  # Type of anchor selected (pain_point, recent_activity, role_based)
    context_depth_score: int  # Calculated context depth score (0-4)
    generation_mode: str  # Mode selected based on context depth (Precision, Safe Personalization, Exploratory)
    analysis_details: Optional[Dict[str, Any]] = {}  # Additional details about the analysis
    analysis_timestamp: datetime = datetime.now()  # When the analysis was performed

    def __init__(self, **data):
        super().__init__(**data)
        # Validate context_depth_score is between 0 and 4 inclusive
        if not 0 <= data.get('context_depth_score', 0) <= 4:
            raise ValueError("context_depth_score must be between 0 and 4 inclusive")
        
        # Validate generation_mode is one of the allowed values
        allowed_modes = ["Precision", "Safe Personalization", "Exploratory"]
        if data.get('generation_mode') not in allowed_modes:
            raise ValueError(f"generation_mode must be one of {allowed_modes}")
        
        # Validate anchor_type is one of the allowed values
        allowed_anchor_types = ["pain_point", "recent_activity", "role_based"]
        if data.get('anchor_type') not in allowed_anchor_types:
            raise ValueError(f"anchor_type must be one of {allowed_anchor_types}")