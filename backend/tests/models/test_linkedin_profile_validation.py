import pytest
from ..models.linkedin_profile import LinkedInProfile


def test_required_field_validation_both_role_and_company():
    """Test required field validation when both role and company are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert missing_fields == []


def test_required_field_validation_role_and_industry():
    """Test required field validation when role and industry are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        industry="Technology"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert missing_fields == []


def test_required_field_validation_title_and_company():
    """Test required field validation when title and company are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert missing_fields == []


def test_required_field_validation_title_and_industry():
    """Test required field validation when title and industry are provided."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        industry="Technology"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert missing_fields == []


def test_required_field_validation_missing_identity():
    """Test required field validation when identity field is missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        company="Test Corp"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert "role or title" in missing_fields


def test_required_field_validation_missing_affiliation():
    """Test required field validation when affiliation field is missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert "company or industry" in missing_fields


def test_required_field_validation_both_missing():
    """Test required field validation when both identity and affiliation fields are missing."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user"
    )
    
    missing_fields = profile.validate_required_fields()
    
    assert "role or title" in missing_fields
    assert "company or industry" in missing_fields


def test_required_field_validation_empty_strings():
    """Test required field validation with empty string values."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="",  # Empty string
        company=""  # Empty string
    )
    
    missing_fields = profile.validate_required_fields()
    
    # Empty strings are falsy, so both identity and affiliation would be considered missing
    assert "role or title" in missing_fields
    assert "company or industry" in missing_fields


def test_required_field_validation_none_values():
    """Test required field validation with None values."""
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role=None,  # None value
        company=None  # None value
    )
    
    missing_fields = profile.validate_required_fields()
    
    # None values are falsy, so both identity and affiliation would be considered missing
    assert "role or title" in missing_fields
    assert "company or industry" in missing_fields