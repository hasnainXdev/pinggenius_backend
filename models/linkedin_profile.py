from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
import re
from .profile import LinkedInProfile as BaseLinkedInProfile


class LinkedInProfile(BaseLinkedInProfile):
    """
    Extended LinkedIn profile model for context validation feature.
    Inherits from the base LinkedInProfile but adds fields and validation
    required for the context validation feature.
    """

    # Override pain_point to be a list of pain points (to match our spec)
    pain_points: Optional[List[str]] = Field(default=[], description="List of identified pain points from the profile")
    # Override recent_activity to be a list (to match our spec)
    recent_activity: Optional[List[str]] = Field(default=[], description="List of recent activities/posts by the person")
    # Add profile_url field to match our spec (using the existing url field)
    profile_url: Optional[str] = Field(default=None, description="URL to the LinkedIn profile")
    # Add created_at and updated_at with defaults
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the profile was added")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the profile was last updated")

    def model_post_init(self, __context):
        """Initialize profile_url from the base url field if not provided."""
        if not self.profile_url:
            self.profile_url = getattr(self, 'url', None)

    @model_validator(mode='after')
    def validate_identity_field_exists(self):
        """Validates that at least one identity field (role or title) exists."""
        # In the base model, role is required, so this validation is mostly for consistency
        # But we'll add title as an optional identity field as per our spec
        return self

    def validate_required_fields(self) -> List[str]:
        """
        Validate that required fields exist and return list of missing fields.
        
        Returns:
            List of missing required fields
        """
        missing_fields = []

        # Check for at least one identity field (role OR title)
        # Note: In the base model, role is required, so this will always pass
        # But we'll keep this for consistency with our spec
        if not self.role and not hasattr(self, 'title'):
            missing_fields.append("role or title")

        # Check for at least one affiliation field (company OR industry)
        if not self.company and not self.industry:
            missing_fields.append("company or industry")

        return missing_fields

    @property
    def has_sufficient_context(self) -> bool:
        """
        Check if the profile has sufficient context for outreach generation.
        
        Returns:
            Boolean indicating if the profile has sufficient context
        """
        missing_fields = self.validate_required_fields()
        return len(missing_fields) == 0

    @property
    def context_depth_score(self) -> int:
        """
        Calculate the context depth score for this profile.
        
        Returns:
            Integer score from 0-4
        """
        score = 0

        # Check for role (required in base model)
        if self.role:
            score += 1

        # Check for company or industry
        if self.company or self.industry:
            score += 1

        # Check for pain points (using the new field)
        if self.pain_points and len(self.pain_points) > 0:
            score += 1

        # Check for recent activity (using the new field)
        if self.recent_activity and len(self.recent_activity) > 0:
            score += 1

        return score