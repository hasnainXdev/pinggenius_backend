from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .outreach_message import OutreachMessage


class ContextAwareOutreachSequence(BaseModel):
    """
    A series of messages that maintain context continuity around a single anchor.
    This is a context-aware version of the outreach sequence for the context validation feature.
    """
    id: Optional[str] = None
    profile_id: str  # Reference to the LinkedInProfile
    sequence_title: str  # Brief description of the sequence
    selected_anchor: str  # The anchor point used for the entire sequence
    messages: List[OutreachMessage]  # Ordered list of messages in the sequence
    tone_preference: str  # Desired tone for the sequence (Authority, Friendly, Casual)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def add_message(self, message: OutreachMessage):
        """Add a message to the sequence."""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_message_by_order(self, order: int) -> Optional[OutreachMessage]:
        """Get a message by its order in the sequence."""
        for msg in self.messages:
            if msg.message_order == order:
                return msg
        return None

    def get_latest_message(self) -> Optional[OutreachMessage]:
        """Get the latest message in the sequence based on message_order."""
        if not self.messages:
            return None
        return max(self.messages, key=lambda msg: msg.message_order)

    def get_messages_by_anchor_reference(self, anchor_point: str) -> List[OutreachMessage]:
        """Get all messages that reference the given anchor point."""
        referenced_messages = []
        for msg in self.messages:
            if msg.check_anchor_reference(anchor_point):
                referenced_messages.append(msg)
        return referenced_messages

    def calculate_anchor_consistency_score(self, anchor_point: str) -> float:
        """Calculate the consistency score for anchor references across all messages."""
        if not self.messages:
            return 0.0

        messages_referencing_anchor = 0
        for msg in self.messages:
            if msg.check_anchor_reference(anchor_point):
                messages_referencing_anchor += 1

        return messages_referencing_anchor / len(self.messages)

    def get_follow_up_ready_state(self) -> dict:
        """Get the state information needed for generating follow-ups."""
        latest_message = self.get_latest_message()
        anchor_references = self.get_messages_by_anchor_reference(self.selected_anchor)

        return {
            "latest_message": latest_message.model_dump() if latest_message else None,
            "total_messages": len(self.messages),
            "anchor_consistency_score": self.calculate_anchor_consistency_score(self.selected_anchor),
            "messages_referencing_anchor": len(anchor_references),
            "tone_preference": self.tone_preference,
            "selected_anchor": self.selected_anchor
        }