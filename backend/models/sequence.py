from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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


class SequenceContext(BaseModel):
    """
    Information about previous messages in a sequence that informs the generation of subsequent messages,
    stored temporarily during generation with option to persist valuable sequences permanently.
    """

    sequence_id: Optional[str] = None
    previous_messages: List[Dict[str, Any]] = []  # List of previous messages in the sequence
    context_summary: str = ""  # Summary of the conversation context
    tone_consistency_log: List[Dict[str, Any]] = []  # Log of tone validation results
    temporary_storage: bool = True  # Whether this context is in temporary storage


class OutreachSequence(BaseModel):
    """
    A collection of four messages generated for a specific LinkedIn profile
    """

    id: Optional[str] = None
    user_id: Optional[str] = None  # ID of the user who generated this sequence
    profile_id: str  # Reference to the associated LinkedInProfile
    connection_note: str  # The connection request message
    dm_1: str  # First direct message
    follow_up_1: str  # First follow-up message
    follow_up_2: str  # Second follow-up message
    tone: str  # The tone used for generation (Friendly, Direct, Authority, Casual)
    predicted_reply_score: float = 0.0  # Predicted reply rate for this sequence
    pain_point_used: Optional[str] = None  # Pain point that was incorporated
    sequence_context: Optional[Dict[str, Any]] = None  # Context maintained between messages
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status: str = "GENERATED"  # Status of the sequence (GENERATED, REFINING, REFINED, ARCHIVED)
