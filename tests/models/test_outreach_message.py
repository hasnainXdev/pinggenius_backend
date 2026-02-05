import pytest
from datetime import datetime
from ..models.outreach_message import OutreachMessage


def test_outreach_message_creation():
    """Test creating an OutreachMessage with valid data."""
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content="Hello, I noticed your post about scaling challenges..."
    )
    
    assert message.sequence_id == "seq-123"
    assert message.message_order == 0
    assert "scaling challenges" in message.content
    assert message.character_count == len(message.content)
    assert message.created_at is not None


def test_outreach_message_with_all_fields():
    """Test creating an OutreachMessage with all fields."""
    message = OutreachMessage(
        id="msg-456",
        sequence_id="seq-123",
        message_order=1,
        content="Following up on our previous conversation...",
        character_count=50,
        tone_compliant=True,
        contains_prohibited_phrases=False,
        references_anchor=True
    )
    
    assert message.id == "msg-456"
    assert message.sequence_id == "seq-123"
    assert message.message_order == 1
    assert message.content == "Following up on our previous conversation..."
    assert message.character_count == 50  # Provided value should be preserved
    assert message.tone_compliant is True
    assert message.contains_prohibited_phrases is False
    assert message.references_anchor is True
    assert message.created_at is not None


def test_outreach_message_content_length_validation_valid():
    """Test that valid content lengths are accepted."""
    # Test with content exactly at the limit
    valid_content = "x" * 240
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content=valid_content
    )
    
    assert len(message.content) == 240
    assert message.character_count == 240


def test_outreach_message_content_length_validation_invalid():
    """Test that content exceeding the limit raises an error."""
    invalid_content = "x" * 241  # One character over the limit
    
    with pytest.raises(ValueError):
        OutreachMessage(
            sequence_id="seq-123",
            message_order=0,
            content=invalid_content
        )


def test_outreach_message_order_validation_valid():
    """Test that valid message orders are accepted."""
    # Test with order 0 (minimum valid value)
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content="Test message"
    )
    
    assert message.message_order == 0
    
    # Test with higher order values
    message2 = OutreachMessage(
        sequence_id="seq-123",
        message_order=5,
        content="Test message"
    )
    
    assert message2.message_order == 5


def test_outreach_message_order_validation_invalid():
    """Test that invalid message orders raise an error."""
    with pytest.raises(ValueError):
        OutreachMessage(
            sequence_id="seq-123",
            message_order=-1,  # Negative value should be invalid
            content="Test message"
        )


def test_character_count_auto_calculation():
    """Test that character count is calculated automatically if not provided."""
    content = "This is a test message."
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content=content
    )
    
    assert message.character_count == len(content)


def test_character_count_preserved_if_provided():
    """Test that provided character count is preserved."""
    content = "This is a test message."
    provided_count = 100
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content=content,
        character_count=provided_count
    )
    
    assert message.character_count == provided_count  # Should preserve provided value


def test_outreach_message_defaults():
    """Test that default values are properly set."""
    message = OutreachMessage(
        sequence_id="seq-123",
        message_order=0,
        content="Test message"
    )
    
    assert message.id is None
    assert message.character_count == len("Test message")
    assert message.tone_compliant is False
    assert message.contains_prohibited_phrases is False
    assert message.references_anchor is False
    assert message.created_at is not None
    assert isinstance(message.created_at, datetime)