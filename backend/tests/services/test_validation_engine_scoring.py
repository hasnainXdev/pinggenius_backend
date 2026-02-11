import pytest
from ..models.linkedin_profile import LinkedInProfile
from ..services.validation_engine import ValidationEngine


def test_context_depth_scoring_all_fields_present():
    """Test context depth scoring when all fields are present."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 4  # All 4 scoring elements present


def test_context_depth_scoring_with_title_instead_of_role():
    """Test context depth scoring when using title instead of role."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        title="Manager",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 4  # All 4 scoring elements present (title counts as identity)


def test_context_depth_scoring_with_industry_instead_of_company():
    """Test context depth scoring when using industry instead of company."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        industry="Technology",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 4  # All 4 scoring elements present (industry counts as affiliation)


def test_context_depth_scoring_only_identity_and_affiliation():
    """Test context depth scoring with only identity and affiliation fields."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp"
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 2  # Only identity and affiliation present


def test_context_depth_scoring_only_identity():
    """Test context depth scoring with only identity field."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer"
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 1  # Only identity present


def test_context_depth_scoring_only_affiliation():
    """Test context depth scoring with only affiliation field."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        company="Test Corp"
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 1  # Only affiliation present


def test_context_depth_scoring_no_context():
    """Test context depth scoring with no context fields."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user"
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 0  # No context fields present


def test_context_depth_scoring_empty_lists():
    """Test context depth scoring with empty pain_points and recent_activity lists."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=[],  # Empty list
        recent_activity=[]  # Empty list
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 2  # Only identity and affiliation, empty lists don't count


def test_context_depth_scoring_none_values():
    """Test context depth scoring with None values for optional fields."""
    validation_engine = ValidationEngine()
    
    profile = LinkedInProfile(
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=None,  # None value
        recent_activity=None  # None value
    )
    
    score = validation_engine.calculate_context_depth_score(profile)
    
    assert score == 2  # Only identity and affiliation, None values don't count