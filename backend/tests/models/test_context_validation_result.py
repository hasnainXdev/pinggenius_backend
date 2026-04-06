import pytest
from datetime import datetime
from ..models.context_validation_result import ContextValidationResult


def test_context_validation_result_creation():
    """Test creating a ContextValidationResult with valid data."""
    result = ContextValidationResult(
        profile_id="test-profile-123",
        context_depth_score=3,
        validation_passed=True,
        missing_fields=[],
        anchor_point="Scaling challenges",
        generation_mode="Precision"
    )
    
    assert result.profile_id == "test-profile-123"
    assert result.context_depth_score == 3
    assert result.validation_passed is True
    assert result.missing_fields == []
    assert result.anchor_point == "Scaling challenges"
    assert result.generation_mode == "Precision"
    assert result.validation_timestamp is not None


def test_context_validation_result_with_missing_fields():
    """Test creating a ContextValidationResult with missing fields."""
    result = ContextValidationResult(
        profile_id="test-profile-456",
        context_depth_score=1,
        validation_passed=False,
        missing_fields=["company or industry"],
        anchor_point=None,
        generation_mode="Exploratory"
    )
    
    assert result.profile_id == "test-profile-456"
    assert result.context_depth_score == 1
    assert result.validation_passed is False
    assert "company or industry" in result.missing_fields
    assert result.anchor_point is None
    assert result.generation_mode == "Exploratory"


def test_context_validation_result_score_validation_valid():
    """Test that valid context depth scores are accepted."""
    # Valid scores: 0-4
    for score in range(5):
        result = ContextValidationResult(
            profile_id="test-profile",
            context_depth_score=score,
            validation_passed=True,
            missing_fields=[],
            generation_mode="Precision"
        )
        assert result.context_depth_score == score


def test_context_validation_result_score_validation_invalid():
    """Test that invalid context depth scores raise an error."""
    # Invalid scores: < 0 or > 4
    with pytest.raises(ValueError):
        ContextValidationResult(
            profile_id="test-profile",
            context_depth_score=-1,
            validation_passed=True,
            missing_fields=[],
            generation_mode="Precision"
        )
    
    with pytest.raises(ValueError):
        ContextValidationResult(
            profile_id="test-profile",
            context_depth_score=5,
            validation_passed=True,
            missing_fields=[],
            generation_mode="Precision"
        )


def test_context_validation_result_generation_mode_validation_valid():
    """Test that valid generation modes are accepted."""
    valid_modes = ["Precision", "Safe Personalization", "Exploratory"]
    
    for mode in valid_modes:
        result = ContextValidationResult(
            profile_id="test-profile",
            context_depth_score=3,
            validation_passed=True,
            missing_fields=[],
            generation_mode=mode
        )
        assert result.generation_mode == mode


def test_context_validation_result_generation_mode_validation_invalid():
    """Test that invalid generation modes raise an error."""
    with pytest.raises(ValueError):
        ContextValidationResult(
            profile_id="test-profile",
            context_depth_score=3,
            validation_passed=True,
            missing_fields=[],
            generation_mode="Invalid Mode"
        )


def test_context_validation_result_defaults():
    """Test that default values are properly set."""
    result = ContextValidationResult(
        profile_id="test-profile",
        context_depth_score=2,
        validation_passed=True,
        missing_fields=[],
        generation_mode="Safe Personalization"
    )
    
    # Check that timestamp is set automatically
    assert result.validation_timestamp is not None
    assert isinstance(result.validation_timestamp, datetime)