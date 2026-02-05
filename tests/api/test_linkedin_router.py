import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from ..api.linkedin.router import router
from ..models.linkedin_profile import LinkedInProfile
from ..models.context_validation_result import ContextValidationResult
from ..services.validation_engine import ValidationEngine
from fastapi import FastAPI

# Create a test app with the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_validate_linkedin_context_success():
    """Test successful validation of LinkedIn context."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp",
        "pain_points": ["scaling challenges"],
        "recent_activity": ["published article"]
    }
    
    response = client.post("/linkedin/context/validate", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "profile_id" in data
    assert "context_depth_score" in data
    assert "validation_passed" in data
    assert data["validation_passed"] is True
    assert data["context_depth_score"] >= 3  # Should be rich context


def test_validate_linkedin_context_failure():
    """Test validation failure when required fields are missing."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user"
        # Missing role/company and other required fields
    }
    
    response = client.post("/linkedin/context/validate", json=profile_data)
    
    assert response.status_code == 422  # Validation error


def test_validate_linkedin_context_with_details_success():
    """Test successful validation with detailed response."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp"
    }
    
    response = client.post("/linkedin/context/validate-with-details", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["context_depth_score"] >= 2  # Should have at least role and company


def test_validate_linkedin_context_with_details_failure():
    """Test validation failure with detailed response."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user"
        # Missing required fields
    }
    
    response = client.post("/linkedin/context/validate-with-details", json=profile_data)
    
    assert response.status_code == 422  # Unprocessable entity for validation failure
    data = response.json()
    assert data["detail"]["is_valid"] is False
    assert "missing_fields" in data["detail"]
    assert "role or title" in data["detail"]["missing_fields"]


def test_analyze_linkedin_profile():
    """Test LinkedIn profile analysis."""
    profile_data = {
        "url": "https://www.linkedin.com/in/test-user",
        "profile_url": "https://www.linkedin.com/in/test-user",
        "role": "Software Engineer",
        "company": "Test Corp",
        "pain_points": ["scaling challenges"],
        "recent_activity": ["published article"]
    }
    
    response = client.post("/linkedin/context/analyze", json=profile_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "profile_id" in data
    assert "selected_anchor" in data
    assert "anchor_type" in data
    assert "context_depth_score" in data
    assert "generation_mode" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/linkedin/context/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "linkedin-context-validation"


def test_validate_linkedin_context_error_handling():
    """Test error handling in validation endpoint."""
    # Test with invalid data that causes a validation error
    invalid_profile_data = {
        "url": "invalid-url",  # This should cause a validation error
        "profile_url": "invalid-url",
        "role": "",  # Empty role should cause validation error
        "company": "Test Corp"
    }
    
    response = client.post("/linkedin/context/validate", json=invalid_profile_data)
    
    # Should return 422 for validation errors
    assert response.status_code == 422


def test_analyze_linkedin_profile_error_handling():
    """Test error handling in analysis endpoint."""
    # Test with invalid data
    invalid_profile_data = {
        "url": "invalid-url",
        "profile_url": "invalid-url",
        "role": "",  # Empty role should cause validation error
        "company": "Test Corp"
    }
    
    response = client.post("/linkedin/context/analyze", json=invalid_profile_data)
    
    # Should return 422 for validation errors
    assert response.status_code == 422