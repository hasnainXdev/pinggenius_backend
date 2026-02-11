import pytest
from ..models.linkedin_profile import LinkedInProfile
from ..services.context_analyzer import ContextAnalyzer


def test_anchor_selection_with_pain_points():
    """Test anchor selection when pain points are available (highest priority)."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=["scaling challenges", "team coordination"],
        recent_activity=["published article", "conference speaker"]
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert anchor == "scaling challenges"  # First pain point should be selected
    assert anchor_type == "pain_point"


def test_anchor_selection_with_recent_activity():
    """Test anchor selection when only recent activity is available."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=[],  # Empty list
        recent_activity=["published article", "conference speaker"]
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert anchor == "published article"  # First recent activity should be selected
    assert anchor_type == "recent_activity"


def test_anchor_selection_with_role_only():
    """Test anchor selection when only role is available."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="Test Corp",
        pain_points=[],  # Empty list
        recent_activity=[]  # Empty list
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert "Software Engineer" in anchor
    assert "Test Corp" in anchor
    assert anchor_type == "role_based"


def test_anchor_selection_with_title_instead_of_role():
    """Test anchor selection when title is used instead of role."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="",  # Empty role
        title="Engineering Manager",
        company="Test Corp",
        pain_points=[],  # Empty list
        recent_activity=[]  # Empty list
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert "Engineering Manager" in anchor
    assert "Test Corp" in anchor
    assert anchor_type == "role_based"


def test_anchor_selection_with_industry_instead_of_company():
    """Test anchor selection when industry is used instead of company."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="Software Engineer",
        company="",  # Empty company
        industry="Technology",
        pain_points=[],  # Empty list
        recent_activity=[]  # Empty list
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert "Software Engineer" in anchor
    assert "Technology" in anchor
    assert anchor_type == "role_based"


def test_anchor_selection_with_no_context():
    """Test anchor selection when no context is available."""
    analyzer = ContextAnalyzer()
    
    profile = LinkedInProfile(
        url="https://www.linkedin.com/in/test-user",
        profile_url="https://www.linkedin.com/in/test-user",
        role="",  # Empty role
        company="",  # Empty company
        pain_points=[],  # Empty list
        recent_activity=[]  # Empty list
    )
    
    anchor, anchor_type = analyzer._select_anchor(profile)
    
    assert "test-user" in anchor  # Should contain part of the profile URL
    assert anchor_type == "role_based"