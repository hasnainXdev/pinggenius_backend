import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from tests.test_main import test_app  # Import the test app that doesn't connect to MongoDB
from models.profile import LinkedInProfile
from models.sequence import OutreachSequence
from services.sequence_generator import Tone


def test_read_root():
    """Test the root endpoint"""
    client = TestClient(test_app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "PingGenius LinkedIn Outreach API"}


@patch('api.profile.router.profile_service')
@patch('database.mongo.mongodb')
def test_analyze_linkedin_profile_success(mock_mongodb, mock_profile_service):
    """Test successful LinkedIn profile analysis"""
    # Mock the MongoDB
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_result = MagicMock()
    mock_result.inserted_id = "test_profile_id"
    mock_profiles_collection.insert_one.return_value = mock_result
    mock_db.profiles = mock_profiles_collection
    mock_mongodb.get_database.return_value = mock_db
    mock_mongodb.connect = MagicMock()

    # Mock the profile service response
    mock_profile = MagicMock()
    mock_profile.id = None  # Will be set after DB insertion
    mock_profile.url = "https://www.linkedin.com/in/test"
    mock_profile.role = "Software Engineer"
    mock_profile.company = "Test Company"
    mock_profile.industry = "Technology"
    mock_profile.recent_activity = "Published a new article"
    mock_profile.created_at = datetime.now()
    mock_profile.updated_at = datetime.now()

    mock_profile_service.validate_profile_url.return_value = True
    mock_profile_service.analyze_profile = AsyncMock(return_value=mock_profile)

    # Create test client with patched MongoDB
    client = TestClient(test_app)
    # Make the request
    response = client.post("/profile/analyze", json={"url": "https://www.linkedin.com/in/test"})

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://www.linkedin.com/in/test"
    assert data["role"] == "Software Engineer"
    assert data["company"] == "Test Company"
    assert data["industry"] == "Technology"
    assert data["recent_activity"] == "Published a new article"


@patch('api.profile.router.profile_service')
@patch('database.mongo.mongodb')
def test_analyze_linkedin_profile_invalid_url(mock_mongodb, mock_profile_service):
    """Test LinkedIn profile analysis with invalid URL"""
    # Mock the MongoDB
    mock_mongodb.connect = MagicMock()

    # Mock the profile service to return False for validation
    mock_profile_service.validate_profile_url.return_value = False
    mock_profile_service.analyze_profile = AsyncMock(return_value=None)

    # Create test client with patched MongoDB
    client = TestClient(test_app)
    # Make the request
    response = client.post("/profile/analyze", json={"url": "https://invalid-url.com"})

    # Assertions
    assert response.status_code == 400
    data = response.json()
    assert "error" in data  # The error is at the top level
    assert data["error"]["error"] == "Invalid LinkedIn profile URL"


@patch('database.mongo.mongodb')
def test_generate_outreach_sequence_success(mock_mongodb):
    """Test successful outreach sequence generation"""
    # Mock the database
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_sequences_collection = MagicMock()
    mock_result = MagicMock()
    mock_result.inserted_id = "test_sequence_id"
    mock_sequences_collection.insert_one.return_value = mock_result
    # Create a proper profile object with required fields
    profile_data = {
        "_id": "test_profile_id",
        "url": "https://www.linkedin.com/in/test",
        "role": "Software Engineer",
        "company": "Test Company",
        "industry": "Technology",
        "recent_activity": "Published a new article",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    mock_profiles_collection.find_one.return_value = profile_data
    mock_db.profiles = mock_profiles_collection
    mock_db.sequences = mock_sequences_collection
    mock_mongodb.get_database.return_value = mock_db
    mock_mongodb.connect = MagicMock()

    # Mock the sequence service
    with patch('api.outreach.router.sequence_service') as mock_sequence_service:
        # Create a proper sequence object with all required attributes
        from models.sequence import OutreachSequence
        from models.profile import LinkedInProfile
        from services.sequence_generator import Tone

        # Create the profile object that will be passed to the service
        profile = LinkedInProfile(
            id="test_profile_id",
            url="https://www.linkedin.com/in/test",
            role="Software Engineer",
            company="Test Company",
            industry="Technology",
            recent_activity="Published a new article"
        )

        # Create the sequence object that will be returned by the service
        mock_sequence = OutreachSequence(
            id=None,  # Will be set after DB insertion
            profile_id="test_profile_id",
            connection_note="Hi there!",
            dm_1="Following up on my connection request",
            follow_up_1="Hope you had a chance to read my message",
            follow_up_2="Last follow-up",
            tone=Tone.FRIENDLY.value,
        )

        mock_sequence_service.generate_sequence = AsyncMock(return_value=mock_sequence)

        # Create test client with patched MongoDB
        client = TestClient(test_app)
        # Make the request
        response = client.post("/outreach/generate", json={"profile_id": "test_profile_id", "tone": "Friendly"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == "test_profile_id"
        assert data["connection_note"] == "Hi there!"
        assert data["dm_1"] == "Following up on my connection request"
        assert data["follow_up_1"] == "Hope you had a chance to read my message"
        assert data["follow_up_2"] == "Last follow-up"
        assert data["tone"] == "Friendly"


@patch('database.mongo.mongodb')
def test_generate_outreach_sequence_invalid_profile(mock_mongodb):
    """Test outreach sequence generation with invalid profile ID"""
    # Mock the database to return None for the profile
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_profiles_collection.find_one.return_value = None
    mock_db.profiles = mock_profiles_collection
    mock_mongodb.get_database.return_value = mock_db
    mock_mongodb.connect = MagicMock()

    # Create test client with patched MongoDB
    client = TestClient(test_app)
    # Make the request
    response = client.post("/outreach/generate", json={"profile_id": "nonexistent_profile", "tone": "Friendly"})

    # Assertions
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"] == "Profile not found"


@patch('database.mongo.mongodb')
def test_get_outreach_sequence_success(mock_mongodb):
    """Test successful retrieval of an outreach sequence"""
    # Mock the database
    mock_db = MagicMock()
    mock_sequences_collection = MagicMock()
    now = datetime.now()
    # Create a proper sequence object with string dates
    sequence_data = {
        "_id": "test_sequence_id",
        "profile_id": "test_profile_id",
        "connection_note": "Hi there!",
        "dm_1": "Following up on my connection request",
        "follow_up_1": "Hope you had a chance to read my message",
        "follow_up_2": "Last follow-up",
        "tone": "Friendly",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    mock_sequences_collection.find_one.return_value = sequence_data
    mock_db.sequences = mock_sequences_collection
    mock_mongodb.get_database.return_value = mock_db
    mock_mongodb.connect = MagicMock()

    # Create test client with patched MongoDB
    client = TestClient(test_app)
    # Make the request
    response = client.get("/outreach/test_sequence_id")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_sequence_id"
    assert data["profile_id"] == "test_profile_id"
    assert data["connection_note"] == "Hi there!"
    assert data["dm_1"] == "Following up on my connection request"
    assert data["follow_up_1"] == "Hope you had a chance to read my message"
    assert data["follow_up_2"] == "Last follow-up"
    assert data["tone"] == "Friendly"


@patch('database.mongo.mongodb')
def test_get_outreach_sequence_not_found(mock_mongodb):
    """Test retrieval of a non-existent outreach sequence"""
    # Mock the database to return None
    mock_db = MagicMock()
    mock_sequences_collection = MagicMock()
    mock_sequences_collection.find_one.return_value = None
    mock_db.sequences = mock_sequences_collection
    mock_mongodb.get_database.return_value = mock_db
    mock_mongodb.connect = MagicMock()

    # Create test client with patched MongoDB
    client = TestClient(test_app)
    # Make the request
    response = client.get("/outreach/nonexistent_sequence")

    # Assertions
    assert response.status_code == 404
    assert "not found" in response.text or "not found" in response.json().get("detail", "")


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