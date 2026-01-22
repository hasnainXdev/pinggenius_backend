import pytest
from models.profile import LinkedInProfile
from services.profile_validation import ProfileValidationService
from models.validation import ValidationResult


class TestProfileValidationService:
    """
    Unit tests for ProfileValidationService
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ProfileValidationService()
    
    def test_validate_profile_completeness_valid_profile(self):
        """Test validation of a complete profile with required fields."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.validate_profile_completeness(profile)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.required_fields_present["role"] is True
        assert result.required_fields_present["company"] is True
        assert result.required_fields_present["industry"] is True
    
    def test_validate_profile_completeness_missing_role(self):
        """Test validation of a profile missing the role field."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.validate_profile_completeness(profile)
        
        assert result.is_valid is False
        assert "Role is required for profile analysis" in result.errors
        assert result.required_fields_present["role"] is False
    
    def test_validate_profile_completeness_missing_company_and_industry(self):
        """Test validation of a profile missing both company and industry."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # Missing company
            industry="",  # Missing industry
            tone="FRIENDLY"
        )
        
        result = self.service.validate_profile_completeness(profile)
        
        assert result.is_valid is False
        assert "Either company or industry is required for profile analysis" in result.errors
    
    def test_validate_profile_completeness_valid_with_only_company(self):
        """Test validation of a profile with role and company but no industry."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="",  # No industry
            tone="FRIENDLY"
        )
        
        result = self.service.validate_profile_completeness(profile)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_profile_completeness_valid_with_only_industry(self):
        """Test validation of a profile with role and industry but no company."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # No company
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.validate_profile_completeness(profile)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_check_role_requirement_present(self):
        """Test role requirement check when role is present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.check_role_requirement(profile)
        
        assert result is True
    
    def test_check_role_requirement_missing(self):
        """Test role requirement check when role is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.check_role_requirement(profile)
        
        assert result is False
    
    def test_check_company_or_industry_requirement_both_present(self):
        """Test company/industry requirement check when both are present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.check_company_or_industry_requirement(profile)
        
        assert result is True
    
    def test_check_company_or_industry_requirement_company_only(self):
        """Test company/industry requirement check when only company is present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="",  # No industry
            tone="FRIENDLY"
        )
        
        result = self.service.check_company_or_industry_requirement(profile)
        
        assert result is True
    
    def test_check_company_or_industry_requirement_industry_only(self):
        """Test company/industry requirement check when only industry is present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # No company
            industry="Technology",
            tone="FRIENDLY"
        )
        
        result = self.service.check_company_or_industry_requirement(profile)
        
        assert result is True
    
    def test_check_company_or_industry_requirement_missing_both(self):
        """Test company/industry requirement check when both are missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # No company
            industry="",  # No industry
            tone="FRIENDLY"
        )
        
        result = self.service.check_company_or_industry_requirement(profile)
        
        assert result is False
    
    def test_infer_pain_point_software_engineer_tech(self):
        """Test pain point inference for software engineer in tech."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.service.infer_pain_point(profile)
        
        assert pain_point is not None
        assert "software engineer" in pain_point.role.lower()
        assert "technology" in pain_point.industry.lower()
        assert "Scaling team productivity" == pain_point.description
        assert "technology" == pain_point.category
    
    def test_infer_pain_point_product_manager_finance(self):
        """Test pain point inference for product manager in finance."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Product Manager",
            company="Finance Co",
            industry="Finance",
            tone="FRIENDLY"
        )
        
        pain_point = self.service.infer_pain_point(profile)
        
        assert pain_point is not None
        assert "product manager" in pain_point.role.lower()
        assert "finance" in pain_point.industry.lower()
        assert "Balancing feature velocity with quality" == pain_point.description
        assert "product" == pain_point.category
    
    def test_infer_pain_point_no_match(self):
        """Test pain point inference when no match is found."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Unknown Role",
            company="Random Co",
            industry="Unknown Industry",
            tone="FRIENDLY"
        )
        
        pain_point = self.service.infer_pain_point(profile)
        
        assert pain_point is None
    
    def test_infer_pain_point_missing_role(self):
        """Test pain point inference when role is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.service.infer_pain_point(profile)
        
        assert pain_point is None
    
    def test_infer_pain_point_missing_industry(self):
        """Test pain point inference when industry is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="",  # Missing industry
            tone="FRIENDLY"
        )

        # Even with missing industry, should find a match based on role
        pain_point = self.service.infer_pain_point(profile)

        assert pain_point is not None
        assert "software engineer" in pain_point.role.lower()
        assert "Scaling team productivity" == pain_point.description


class TestProfileCompletenessValidation:
    """
    Unit tests for profile completeness validation
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ProfileValidationService()

    def test_complete_profile_validation_success(self):
        """Test validation of a complete profile with all required fields."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )

        result = self.service.validate_profile_completeness(profile)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.required_fields_present["role"] is True
        assert result.required_fields_present["company"] is True
        assert result.required_fields_present["industry"] is True

    def test_complete_profile_validation_missing_role(self):
        """Test validation fails when role is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )

        result = self.service.validate_profile_completeness(profile)

        assert result.is_valid is False
        assert "Role is required for profile analysis" in result.errors
        assert result.required_fields_present["role"] is False

    def test_complete_profile_validation_missing_company_and_industry(self):
        """Test validation fails when both company and industry are missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # Missing company
            industry="",  # Missing industry
            tone="FRIENDLY"
        )

        result = self.service.validate_profile_completeness(profile)

        assert result.is_valid is False
        assert "Either company or industry is required for profile analysis" in result.errors
        assert result.required_fields_present["company"] is False
        assert result.required_fields_present["industry"] is False

    def test_complete_profile_validation_with_company_only(self):
        """Test validation passes when role and company are present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Sales Representative",
            company="Sales Co",
            industry="",  # Missing industry but company present
            tone="FRIENDLY"
        )

        result = self.service.validate_profile_completeness(profile)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.required_fields_present["role"] is True
        assert result.required_fields_present["company"] is True
        assert result.required_fields_present["industry"] is False

    def test_complete_profile_validation_with_industry_only(self):
        """Test validation passes when role and industry are present."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Marketing Manager",
            company="",  # Missing company but industry present
            industry="Marketing",
            tone="FRIENDLY"
        )

        result = self.service.validate_profile_completeness(profile)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.required_fields_present["role"] is True
        assert result.required_fields_present["company"] is False
        assert result.required_fields_present["industry"] is True


class TestUserFeedbackResponses:
    """
    Unit tests for user feedback responses
    """

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ProfileValidationService()

    def test_enhance_error_message_with_role_missing(self):
        """Test enhanced error message when role is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )

        validation_result = self.service.validate_profile_completeness(profile)

        enhanced_error = self.service.enhance_error_message(validation_result, profile)

        assert enhanced_error["error"] == "Validation failed"
        assert "role is required" in enhanced_error["message"].lower()
        assert enhanced_error["actionable_alternative"] == "Please provide the person's role or job title"

    def test_enhance_error_message_with_company_and_industry_missing(self):
        """Test enhanced error message when both company and industry are missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # Missing company
            industry="",  # Missing industry
            tone="FRIENDLY"
        )

        validation_result = self.service.validate_profile_completeness(profile)

        enhanced_error = self.service.enhance_error_message(validation_result, profile)

        assert enhanced_error["error"] == "Validation failed"
        assert "either company or industry is required" in enhanced_error["message"].lower()
        assert enhanced_error["actionable_alternative"] == "Please provide either company or industry information"

    def test_enhance_error_message_with_role_and_company_industry_missing(self):
        """Test enhanced error message when role and company/industry are missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="",  # Missing company
            industry="",  # Missing industry
            tone="FRIENDLY"
        )

        validation_result = self.service.validate_profile_completeness(profile)

        enhanced_error = self.service.enhance_error_message(validation_result, profile)

        assert enhanced_error["error"] == "Validation failed"
        assert "role is required" in enhanced_error["message"].lower()
        assert enhanced_error["actionable_alternative"] == "Please provide the person's role or job title"

    def test_enhance_error_message_with_all_required_fields_present(self):
        """Test enhanced error message when all required fields are present (should not occur in error case)."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",  # Industry provided
            tone="FRIENDLY"
        )

        validation_result = self.service.validate_profile_completeness(profile)

        # If validation passes, enhance_error_message shouldn't be called normally
        # But let's test the function anyway with a manually created failed validation
        from models.validation import ValidationResult
        failed_result = ValidationResult(
            is_valid=False,
            errors=["Test error for all fields present"],
            required_fields_present={
                "role": True,
                "company": True,
                "industry": True
            }
        )

        enhanced_error = self.service.enhance_error_message(failed_result, profile)

        assert enhanced_error["error"] == "Validation failed"
        assert "test error for all fields present" in enhanced_error["message"].lower()
        assert enhanced_error["actionable_alternative"] == "Please provide a role, and either company or industry information for better results"

    def test_enhance_error_message_with_industry_provided_only(self):
        """Test enhanced error message when only industry is provided (valid case)."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="",  # No company
            industry="Technology",  # Industry provided
            tone="FRIENDLY"
        )

        validation_result = self.service.validate_profile_completeness(profile)

        # This should actually pass validation, so let's test with a failed validation
        from models.validation import ValidationResult
        failed_result = ValidationResult(
            is_valid=False,
            errors=["Test error for industry only case"],
            required_fields_present={
                "role": True,
                "company": False,
                "industry": True
            }
        )

        enhanced_error = self.service.enhance_error_message(failed_result, profile)

        assert enhanced_error["error"] == "Validation failed"
        assert "test error for industry only case" in enhanced_error["message"].lower()
        assert enhanced_error["actionable_alternative"] == "Please provide a role, and either company or industry information for better results"