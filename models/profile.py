from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class LinkedInProfile(BaseModel):
    """
    Represents the target's LinkedIn profile with extracted information
    """

    id: Optional[str] = None
    url: str = Field(..., description="The original LinkedIn profile URL")
    role: str = Field(..., description="Current role of the profile owner")
    company: Optional[str] = Field(None, description="Current company of the profile owner")
    industry: Optional[str] = Field(None, description="Industry/ICP signals from the profile")
    pain_point: Optional[str] = Field(None, description="Inferred pain point from role/industry")
    recent_activity: Optional[str] = Field(None, description="Recent activity information (optional)")
    tone: Optional[str] = Field(None, description="Requested tone for outreach generation")
    context: Optional[dict] = Field(default_factory=dict, description="Extracted context for outreach generation")
    created_at: datetime = Field(default=datetime.now(), description="Timestamp of profile analysis")
    updated_at: datetime = Field(default=datetime.now(), description="Timestamp of last update")

    @field_validator('url')
    def validate_url(cls, v):
        """Validates that the URL is a proper LinkedIn profile URL"""
        linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
        if not re.match(linkedin_pattern, v):
            raise ValueError('URL must be a valid LinkedIn profile URL')
        return v

    @field_validator('role')
    def validate_role(cls, v):
        """Validates that the role is not empty and not a generic term"""
        if not v or v.strip() == "":
            raise ValueError('Role is required and cannot be empty')

        # Check for generic terms that don't provide enough context
        generic_roles = ["person", "user", "employee", "individual", "worker"]
        if v.lower() in generic_roles:
            raise ValueError(f'Generic role "{v}" does not provide sufficient context for targeted outreach')

        return v

    @model_validator(mode='after')
    def validate_company_or_industry_present(self):
        """Validates that either company or industry is present"""
        if not self.company and not self.industry:
            raise ValueError('Either company or industry is required for profile analysis')
        return self

    class Config:
        # Allow extra fields during development, but strict in production
        extra = "allow"
