from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    id: Optional[str] = None
    sequence_id: str
    content: str
    position: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class OutreachSequence(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    profile_id: str
    connection_note: str
    dm_1: str
    follow_up_1: str
    follow_up_2: str
    tone: str
    predicted_reply_score: float = 0.0
    pain_point_used: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status: str = "GENERATED"
