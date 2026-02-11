import pytest
from datetime import datetime
from ..models.analysis_result import AnalysisResult


def test_analysis_result_creation():
    """Test creating an AnalysisResult with valid data."""
    analysis_details = {
        "pain_points_found": True,
        "recent_activity_found": False,
        "context_richness": "Rich"
    }
    
    result = AnalysisResult(
        profile_id="test-profile-123",
        selected_anchor="Scaling challenges",
        anchor_type="pain_point",
        context_depth_score=3,
        generation_mode="Precision",
        analysis_details=analysis_details
    )
    
    assert result.profile_id == "test-profile-123"
    assert result.selected_anchor == "Scaling challenges"
    assert result.anchor_type == "pain_point"
    assert result.context_depth_score == 3
    assert result.generation_mode == "Precision"
    assert result.analysis_details == analysis_details
    assert result.analysis_timestamp is not None


def test_analysis_result_with_minimal_data():
    """Test creating an AnalysisResult with minimal required data."""
    result = AnalysisResult(
        profile_id="test-profile-456",
        selected_anchor="Role at company",
        anchor_type="role_based",
        context_depth_score=1,
        generation_mode="Exploratory"
    )
    
    assert result.profile_id == "test-profile-456"
    assert result.selected_anchor == "Role at company"
    assert result.anchor_type == "role_based"
    assert result.context_depth_score == 1
    assert result.generation_mode == "Exploratory"
    assert result.analysis_details == {}  # Should default to empty dict
    assert result.analysis_timestamp is not None


def test_analysis_result_context_depth_score_validation_valid():
    """Test that valid context depth scores are accepted."""
    # Valid scores: 0-4
    for score in range(5):
        result = AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="pain_point",
            context_depth_score=score,
            generation_mode="Precision"
        )
        assert result.context_depth_score == score


def test_analysis_result_context_depth_score_validation_invalid():
    """Test that invalid context depth scores raise an error."""
    # Invalid scores: < 0 or > 4
    with pytest.raises(ValueError):
        AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="pain_point",
            context_depth_score=-1,
            generation_mode="Precision"
        )
    
    with pytest.raises(ValueError):
        AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="pain_point",
            context_depth_score=5,
            generation_mode="Precision"
        )


def test_analysis_result_generation_mode_validation_valid():
    """Test that valid generation modes are accepted."""
    valid_modes = ["Precision", "Safe Personalization", "Exploratory"]
    
    for mode in valid_modes:
        result = AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="pain_point",
            context_depth_score=3,
            generation_mode=mode
        )
        assert result.generation_mode == mode


def test_analysis_result_generation_mode_validation_invalid():
    """Test that invalid generation modes raise an error."""
    with pytest.raises(ValueError):
        AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="pain_point",
            context_depth_score=3,
            generation_mode="Invalid Mode"
        )


def test_analysis_result_anchor_type_validation_valid():
    """Test that valid anchor types are accepted."""
    valid_types = ["pain_point", "recent_activity", "role_based"]
    
    for anchor_type in valid_types:
        result = AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type=anchor_type,
            context_depth_score=3,
            generation_mode="Precision"
        )
        assert result.anchor_type == anchor_type


def test_analysis_result_anchor_type_validation_invalid():
    """Test that invalid anchor types raise an error."""
    with pytest.raises(ValueError):
        AnalysisResult(
            profile_id="test-profile",
            selected_anchor="Test anchor",
            anchor_type="invalid_type",
            context_depth_score=3,
            generation_mode="Precision"
        )


def test_analysis_result_defaults():
    """Test that default values are properly set."""
    result = AnalysisResult(
        profile_id="test-profile",
        selected_anchor="Test anchor",
        anchor_type="pain_point",
        context_depth_score=2,
        generation_mode="Safe Personalization"
    )
    
    # Check that analysis_details defaults to empty dict
    assert result.analysis_details == {}
    
    # Check that timestamp is set automatically
    assert result.analysis_timestamp is not None
    assert isinstance(result.analysis_timestamp, datetime)