from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    """
    An individual component of an outreach sequence
    """

    id: Optional[str] = None
    sequence_id: str  # Reference to the parent OutreachSequence
    content: str  # The actual text content of the message
    position: int  # Position in the sequence (1-4: connection_note, dm_1, follow_up_1, follow_up_2)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class OutreachSequence(BaseModel):
    """
    A collection of four messages generated for a specific LinkedIn profile
    """

    id: Optional[str] = None
    profile_id: str  # Reference to the associated LinkedInProfile
    connection_note: str  # The connection request message
    dm_1: str  # First direct message
    follow_up_1: str  # First follow-up message
    follow_up_2: str  # Second follow-up message
    tone: str  # The tone used for generation (Friendly, Direct, Authority, Casual)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status: str = "GENERATED"  # Status of the sequence (GENERATED, REFINING, REFINED)
