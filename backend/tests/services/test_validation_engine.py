import pytest
from ..models.linkedin_profile import LinkedInProfile
from ..services.validation_engine import ValidationEngine, GenerationMode


def test_context_validation_logic_pass():
    """Test context validation logic when validation passes."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp"
    )
    
    result = validation_engine.validate_context(profile)
    
    assert result.validation_passed is True
    assert result.missing_fields == []
    assert result.context_depth_score >= 2  # Should have at least role/company


def test_context_validation_logic_fail():
    """Test context validation logic when validation fails."""
    validation_engine = ValidationEngine()
    
    # Profile missing required fields
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user"
        # Missing role/title and company/industry
    )
    
    result = validation_engine.validate_context(profile)
    
    assert result.validation_passed is False
    assert "role or title" in result.missing_fields
    assert "company or industry" in result.missing_fields


def test_context_validation_with_title_instead_of_role():
    """Test context validation when using title instead of role."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        industry="Technology"
    )
    
    result = validation_engine.validate_context(profile)
    
    assert result.validation_passed is True
    assert result.missing_fields == []


def test_context_validation_with_industry_instead_of_company():
    """Test context validation when using industry instead of company."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        industry="Technology"
    )
    
    result = validation_engine.validate_context(profile)
    
    assert result.validation_passed is True
    assert result.missing_fields == []


def test_context_validation_with_all_fields():
    """Test context validation with a profile that has all fields."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    result = validation_engine.validate_context(profile)
    
    assert result.validation_passed is True
    assert result.missing_fields == []
    assert result.context_depth_score == 4  # All 4 scoring elements present


def test_context_validation_generation_mode_mapping():
    """Test that generation mode is correctly mapped based on context depth score."""
    validation_engine = ValidationEngine()
    
    # Rich context (score >= 3) should map to Precision mode
    rich_profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    rich_result = validation_engine.validate_context(rich_profile)
    assert rich_result.generation_mode == GenerationMode.PRECISION.value
    
    # Moderate context (score = 2) should map to Safe Personalization mode
    moderate_profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    moderate_result = validation_engine.validate_context(moderate_profile)
    assert moderate_result.generation_mode == GenerationMode.SAFE_PERSONALIZATION.value
    
    # Low context (score <= 1) should map to Exploratory mode
    low_profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer"
    )
    low_result = validation_engine.validate_context(low_profile)
    assert low_result.generation_mode == GenerationMode.EXPLORATORY.value