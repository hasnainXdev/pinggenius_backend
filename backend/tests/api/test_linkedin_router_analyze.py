import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from ..api.linkedin.router import router
from ..models.linkedin_profile import LinkedInProfile
from fastapi import FastAPI

# Create a test app with the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_analyze_endpoint_with_pain_points():
    """Test the analyze endpoint when pain points are available."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp",
        "pain_points": ["scaling challenges", "team coordination"],
        "recent_activity": ["published article"]
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "selected_anchor" in data
    assert "anchor_type" in data
    assert "context_depth_score" in data
    assert "generation_mode" in data
    assert data["selected_anchor"] == "scaling challenges"  # Should pick first pain point
    assert data["anchor_type"] == "pain_point"
    assert data["context_depth_score"] == 4  # All 4 elements present
    assert data["generation_mode"] == "Precision"  # Rich context


def test_analyze_endpoint_with_recent_activity_only():
    """Test the analyze endpoint when only recent activity is available."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp",
        "pain_points": [],  # No pain points
        "recent_activity": ["published article"]
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "selected_anchor" in data
    assert "anchor_type" in data
    assert "context_depth_score" in data
    assert "generation_mode" in data
    assert data["selected_anchor"] == "published article"  # Should pick recent activity
    assert data["anchor_type"] == "recent_activity"
    assert data["context_depth_score"] == 3  # 3 elements present (role, company, recent_activity)
    assert data["generation_mode"] == "Precision"  # Still rich context


def test_analyze_endpoint_with_role_only():
    """Test the analyze endpoint when only role is available."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp",
        "pain_points": [],  # No pain points
        "recent_activity": []  # No recent activity
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "selected_anchor" in data
    assert "anchor_type" in data
    assert "context_depth_score" in data
    assert "generation_mode" in data
    assert "Software Engineer" in data["selected_anchor"]
    assert "Test Corp" in data["selected_anchor"]
    assert data["anchor_type"] == "role_based"
    assert data["context_depth_score"] == 2  # 2 elements present (role, company)
    assert data["generation_mode"] == "Safe Personalization"  # Moderate context


def test_analyze_endpoint_error_handling():
    """Test error handling in the analyze endpoint."""
    # Invalid profile data
    invalid_profile_data = {
        "url": "invalid-url",  # This should cause a validation error
        "profile_url": "invalid-url",
        "role": "",  # Empty role should cause validation error
        "company": "Test Corp"
    }
    
    response = client.post("/linkedin/context/analyze", json=invalid_profile_data)
    
    # Should return 422 for validation errors
    assert response.status_code == 422


def test_analyze_endpoint_with_insufficient_context():
    """Test the analyze endpoint with insufficient context."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "",  # No company
        "industry": "",  # No industry
        "pain_points": [],  # No pain points
        "recent_activity": []  # No recent activity
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    # This should still work but with low context score
    assert response.status_code == 200
    data = response.json()
    assert data["context_depth_score"] == 1  # Only role is present
    assert data["generation_mode"] == "Exploratory"  # Low context mode


def test_analyze_endpoint_with_all_context_elements():
    """Test the analyze endpoint with all context elements present."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "title": "Senior Software Engineer",  # Both role and title
        "company": "Test Corp",
        "industry": "Technology",  # Both company and industry
        "pain_points": ["scaling challenges", "team coordination"],
        "recent_activity": ["published article", "conference speaker"]
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["context_depth_score"] == 4  # All elements present
    assert data["generation_mode"] == "Precision"  # Highest context mode
    assert data["selected_anchor"] == "scaling challenges"  # Pain points have priority
    assert data["anchor_type"] == "pain_point"