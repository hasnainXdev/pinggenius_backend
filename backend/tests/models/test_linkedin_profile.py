import pytest
from datetime import datetime
from ..models.linkedin_profile import LinkedInProfile


def test_linkedin_profile_creation():
    """Test creating a LinkedInProfile with valid data."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp"
    )
    
    assert profile.profile_url == "https://www.linkedin.com/in/test-user"
    assert profile.role == "Software Engineer"
    assert profile.company == "Test Corp"
    assert profile.created_at is not None
    assert profile.updated_at is not None


def test_linkedin_profile_with_optional_fields():
    """Test creating a LinkedInProfile with optional fields."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Developer",
        industry="Technology",
        pain_points=["scaling challenges", "team coordination"],
        recent_activity=["published article", "conference speaker"]
    )
    
    assert profile.title == "Developer"
    assert profile.industry == "Technology"
    assert "scaling challenges" in profile.pain_points
    assert "published article" in profile.recent_activity


def test_validate_required_fields_both_role_and_company():
    """Test validation when both role and company are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    assert missing_fields == []


def test_validate_required_fields_role_and_industry():
    """Test validation when role and industry are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        industry="Tech"
    )
    
    missing_fields = profile.validate_required_fields()
    assert missing_fields == []


def test_validate_required_fields_title_and_company():
    """Test validation when title and company are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    assert missing_fields == []


def test_validate_required_fields_title_and_industry():
    """Test validation when title and industry are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        industry="Tech"
    )
    
    missing_fields = profile.validate_required_fields()
    assert missing_fields == []


def test_validate_required_fields_missing_identity():
    """Test validation when identity field is missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    assert "role or title" in missing_fields


def test_validate_required_fields_missing_affiliation():
    """Test validation when affiliation field is missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer"
    )
    
    missing_fields = profile.validate_required_fields()
    assert "company or industry" in missing_fields


def test_validate_required_fields_both_missing():
    """Test validation when both identity and affiliation fields are missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user"
    )
    
    missing_fields = profile.validate_required_fields()
    assert "role or title" in missing_fields
    assert "company or industry" in missing_fields


def test_pain_points_default_value():
    """Test that pain_points defaults to an empty list."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    
    assert profile.pain_points == []


def test_recent_activity_default_value():
    """Test that recent_activity defaults to an empty list."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    
    assert profile.recent_activity == []