from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ValidationResult(BaseModel):
    """
    Represents the outcome of profile validation, indicating whether the profile meets minimum requirements.
    """
    is_valid: bool = Field(..., description="Whether the profile passed validation")
    errors: List[str] = Field(default_factory=list, description="List of validation errors if any")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings if any")
    required_fields_present: Optional[Dict[str, bool]] = Field(
        default=None, 
        description="Map of required fields and their presence status"
    )


class FallbackMessage(BaseModel):
    """
    A safe, generic message returned when profile validation fails to prevent AI hallucination.
    """
    message: str = Field(..., description="The fallback message content")
    reason: str = Field(..., description="Reason for returning fallback (e.g., 'insufficient_context')")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the fallback was generated")


class PainPoint(BaseModel):
    """
    A specific challenge or problem inferred from the profile that the outreach message can address,
    selected from a curated list of role/industry-specific pain points.
    """
    id: str = Field(..., description="Unique identifier for the pain point")
    role: str = Field(..., description="Associated role for this pain point")
    industry: Optional[str] = Field(None, description="Associated industry for this pain point")
    description: str = Field(..., description="Detailed description of the pain point")
    category: str = Field(..., description="Category of the pain point (e.g., 'sales', 'marketing', 'product')")
    effectiveness_score: Optional[float] = Field(None, description="Historical effectiveness score")


class ToneValidatorConfiguration(BaseModel):
    """
    Configuration for validating that generated messages adhere to requested tone parameters using prescriptive rules.
    """
    tone_type: str = Field(..., description="The tone type (Friendly, Direct, Authority, Casual)")
    emoji_limit: int = Field(1, description="Maximum number of emojis allowed")
    slang_allowed: bool = Field(False, description="Whether slang is allowed")
    formality_level: int = Field(3, ge=1, le=5, description="Formality level (1-5 scale)")
    exclamation_limit: int = Field(2, description="Maximum number of exclamation marks")
    capitalization_rules: str = Field("standard", description="Capitalization guidelines")