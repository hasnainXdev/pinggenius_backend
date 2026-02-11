from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TonePreference(BaseModel):
    """
    User-selected parameter that influences the style and language of generated messages
    """

    id: Optional[str] = None
    name: str  # The name of the tone (Friendly, Direct, Authority, Casual)
    description: str  # Brief description of the tone characteristics
    created_at: datetime = datetime.now()
