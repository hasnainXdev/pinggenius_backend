import pytest
from datetime import datetime
from ..models.outreach_message import OutreachMessage
from ..models.context_aware_outreach_sequence import ContextAwareOutreachSequence


def test_outreach_sequence_creation():
    """Test creating a ContextAwareOutreachSequence with valid data."""
    sequence = ContextAwareOutreachSequence(
        profile_id="test-profile-123",
        sequence_title="Initial outreach sequence",
        selected_anchor="Scaling challenges",
        tone_preference="Friendly",
        messages=[]
    )
    
    assert sequence.profile_id == "test-profile-123"
    assert sequence.sequence_title == "Initial outreach sequence"
    assert sequence.selected_anchor == "Scaling challenges"
    assert sequence.tone_preference == "Friendly"
    assert sequence.messages == []
    assert sequence.created_at is not None
    assert sequence.updated_at is not None


def test_add_message_to_sequence():
    """Test adding a message to the sequence."""
    sequence = ContextAwareOutreachSequence(
        profile_id="test-profile-123",
        sequence_title="Initial outreach sequence",
        selected_anchor="Scaling challenges",
        tone_preference="Friendly",
        messages=[]
    )
    
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content="Hello, I noticed your post about scaling challenges..."
    )
    
    initial_update_time = sequence.updated_at
    sequence.add_message(message)
    
    assert len(sequence.messages) == 1
    assert sequence.messages[0] == message
    assert sequence.updated_at > initial_update_time


def test_get_message_by_order():
    """Test retrieving a message by its order."""
    sequence = ContextAwareOutreachSequence(
        profile_id="test-profile-123",
        sequence_title="Initial outreach sequence",
        selected_anchor="Scaling challenges",
        tone_preference="Friendly",
        messages=[]
    )
    
    message1 = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content="Hello, I noticed your post about scaling challenges..."
    )
    
    message2 = OutreachMessage(
        sequence_id="seq-123",
        message_order=1,
        content="Following up on our previous conversation..."
    )
    
    sequence.add_message(message1)
    sequence.add_message(message2)
    
    retrieved_msg = sequence.get_message_by_order(0)
    assert retrieved_msg == message1
    
    retrieved_msg = sequence.get_message_by_order(1)
    assert retrieved_msg == message2
    
    retrieved_msg = sequence.get_message_by_order(2)
    assert retrieved_msg is None


def test_sequence_defaults():
    """Test that default values are properly set."""
    sequence = ContextAwareOutreachSequence(
        profile_id="test-profile-123",
        sequence_title="Initial outreach sequence",
        selected_anchor="Scaling challenges",
        tone_preference="Friendly"
    )
    
    assert sequence.messages == []
    assert sequence.created_at is not None
    assert sequence.updated_at is not None
    assert isinstance(sequence.created_at, datetime)
    assert isinstance(sequence.updated_at, datetime)


def test_multiple_messages_in_sequence():
    """Test sequence with multiple messages."""
    messages = [
        OutreachMessage(sequence_id="seq-123", message_order=0, content="Message 1"),
        OutreachMessage(sequence_id="seq-123", message_order=1, content="Message 2"),
        OutreachMessage(sequence_id="seq-123", message_order=2, content="Message 3")
    ]
    
    sequence = ContextAwareOutreachSequence(
        profile_id="test-profile-123",
        sequence_title="Multi-message sequence",
        selected_anchor="Scaling challenges",
        tone_preference="Friendly",
        messages=messages
    )
    
    assert len(sequence.messages) == 3
    assert all(isinstance(msg, OutreachMessage) for msg in sequence.messages)