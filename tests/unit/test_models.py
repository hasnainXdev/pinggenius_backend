import pytest
from fastapi.testclient import TestClient
from main import app
from models.profile import LinkedInProfile
from models.sequence import OutreachSequence, Message
from services.sequence_generator import Tone


client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "PingGenius LinkedIn Outreach API"}


def test_linkedin_profile_model():
    """Test the LinkedInProfile model"""
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test",
        role="Engineer",
        company="Test Corp",
        industry="Technology",
        recent_activity="Published article",
    )

    assert profile.url == "https://www.linkedin.com/in/test"
    assert profile.role == "Engineer"
    assert profile.company == "Test Corp"
    assert profile.industry == "Technology"
    assert profile.recent_activity == "Published article"


def test_outreach_sequence_model():
    """Test the OutreachSequence model"""
    sequence = OutreachSequence(
        profile_id="test_profile_id",
        connection_note="Hi there!",
        dm_1="Following up on my connection request",
        follow_up_1="Hope you had a chance to read my message",
        follow_up_2="Last follow-up",
        tone=Tone.FRIENDLY.value,
    )

    assert sequence.profile_id == "test_profile_id"
    assert sequence.connection_note == "Hi there!"
    assert sequence.dm_1 == "Following up on my connection request"
    assert sequence.follow_up_1 == "Hope you had a chance to read my message"
    assert sequence.follow_up_2 == "Last follow-up"
    assert sequence.tone == "Friendly"


def test_tone_enum():
    """Test the Tone enum values"""
    assert Tone.FRIENDLY.value == "Friendly"
    assert Tone.DIRECT.value == "Direct"
    assert Tone.AUTHORITY.value == "Authority"
    assert Tone.CASUAL.value == "Casual"
