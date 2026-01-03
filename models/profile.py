from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class LinkedInProfile(BaseModel):
    """
    Represents the target's LinkedIn profile with extracted information
    """

    id: Optional[str] = None
    url: str  # The original LinkedIn profile URL
    role: str  # Current role of the profile owner
    company: str  # Current company of the profile owner
    industry: str  # Industry/ICP signals from the profile
    recent_activity: Optional[str] = None  # Recent activity information (optional)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
