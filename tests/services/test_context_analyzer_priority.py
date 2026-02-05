import pytest
from ..models.linkedin_profile import LinkedInProfile
from ..services.context_analyzer import ContextAnalyzer


def test_anchor_priority_pain_points_highest():
    """Test that pain points have the highest priority."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert result.selected_anchor == "scaling challenges"
    assert result.anchor_type == "pain_point"
    assert result.generation_mode in ["Precision", "Safe Personalization", "Exploratory"]


def test_anchor_priority_recent_activity_when_no_pain_points():
    """Test that recent activity has priority when pain points are not available."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=[],  # No pain points
        recent_activity=["published article"]
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert result.selected_anchor == "published article"
    assert result.anchor_type == "recent_activity"


def test_anchor_priority_role_based_when_no_context():
    """Test that role-based anchor is used when no pain points or recent activity."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=[],  # No pain points
        recent_activity=[]  # No recent activity
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert "Software Engineer" in result.selected_anchor
    assert "Test Corp" in result.selected_anchor
    assert result.anchor_type == "role_based"


def test_anchor_priority_with_title_instead_of_role():
    """Test anchor priority when using title instead of role."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="",  # No role
        title="Engineering Manager",
        company="Test Corp",
        pain_points=[],  # No pain points
        recent_activity=[]  # No recent activity
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert "Engineering Manager" in result.selected_anchor
    assert "Test Corp" in result.selected_anchor
    assert result.anchor_type == "role_based"


def test_anchor_priority_with_industry_instead_of_company():
    """Test anchor priority when using industry instead of company."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="",  # No company
        industry="Technology",
        pain_points=[],  # No pain points
        recent_activity=[]  # No recent activity
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert "Software Engineer" in result.selected_anchor
    assert "Technology" in result.selected_anchor
    assert result.anchor_type == "role_based"


def test_anchor_priority_generation_mode_mapping():
    """Test that generation mode is correctly mapped based on context depth."""
    analyzer = ContextAnalyzer()
    
    # Rich context (pain points + recent activity) should result in Precision mode
    rich_profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    rich_result = analyzer.analyze_profile(rich_profile)
    assert rich_result.generation_mode == "Precision"
    assert rich_result.context_depth_score == 4
    
    # Moderate context (role + company) should result in Safe Personalization mode
    moderate_profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="Test Corp",
        pain_points=[],  # No pain points
        recent_activity=[]  # No recent activity
    )
    moderate_result = analyzer.analyze_profile(moderate_profile)
    assert moderate_result.generation_mode == "Safe Personalization"
    assert moderate_result.context_depth_score == 2
    
    # Low context (just role) should result in Exploratory mode
    low_profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Engineer",
        company="",  # No company
        industry="Technology",
        pain_points=[],  # No pain points
        recent_activity=[]  # No recent activity
    )
    low_result = analyzer.analyze_profile(low_profile)
    assert low_result.generation_mode == "Exploratory"
    assert low_result.context_depth_score == 2  # Role + industry = 2


def test_anchor_priority_analysis_details():
    """Test that analysis details are correctly populated."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=["scaling challenges"],
        recent_activity=["published article"]
    )
    
    result = analyzer.analyze_profile(profile)
    
    assert result.analysis_details is not None
    assert result.analysis_details["pain_points_found"] is True
    assert result.analysis_details["recent_activity_found"] is True
    assert result.analysis_details["context_richness"] == "Rich"