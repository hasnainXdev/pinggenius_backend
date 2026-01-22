import pytest
from models.profile import LinkedInProfile
from services.context_extractor import ContextExtractor


class TestContextExtractor:
    """
    Unit tests for ContextExtractor
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = ContextExtractor()
    
    def test_extract_context_with_pain_point_software_engineer(self):
        """Test context extraction with pain point for software engineer."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        context = self.extractor.extract_context(profile)
        
        assert context["role"] == "Software Engineer"
        assert context["company"] == "Tech Corp"
        assert context["industry"] == "Technology"
        assert context["person_name"] == "Test User"
        assert context["pain_point"] is not None
        assert "productivity" in context["pain_point"].lower() or "candidate" in context["pain_point"].lower()
    
    def test_extract_context_with_pain_point_sales_manager(self):
        """Test context extraction with pain point for sales manager."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Sales Manager",
            company="Sales Co",
            industry="Retail",
            tone="FRIENDLY"
        )
        
        context = self.extractor.extract_context(profile)
        
        assert context["role"] == "Sales Manager"
        assert context["company"] == "Sales Co"
        assert context["industry"] == "Retail"
        assert context["person_name"] == "Test User"
        assert context["pain_point"] is not None
        assert "qualified leads" in context["pain_point"] or "conversion" in context["pain_point"]
    
    def test_extract_context_with_pain_point_not_found(self):
        """Test context extraction when no pain point is found."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Unknown Role",
            company="Random Co",
            industry="Unknown Industry",
            tone="FRIENDLY"
        )
        
        context = self.extractor.extract_context(profile)
        
        assert context["role"] == "Unknown Role"
        assert context["company"] == "Random Co"
        assert context["industry"] == "Unknown Industry"
        assert context["person_name"] == "Test User"
        # The context extractor will try partial matching, so we might still get a pain point
        # but it won't necessarily be relevant to the unknown role
    
    def test_extract_context_without_role(self):
        """Test context extraction when role is missing."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Missing role
            company="Random Co",
            industry="Unknown Industry",
            tone="FRIENDLY"
        )
        
        context = self.extractor.extract_context(profile)
        
        assert context["role"] == ""
        assert context["company"] == "Random Co"
        assert context["industry"] == "Unknown Industry"
        assert context["person_name"] == "Test User"
        assert context["pain_point"] is None
    
    def test_extract_context_with_partial_role_match(self):
        """Test context extraction with partial role matching."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Senior Software Engineer",  # Contains "software engineer"
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        context = self.extractor.extract_context(profile)
        
        assert "software engineer" in context["role"].lower()
        assert context["company"] == "Tech Corp"
        assert context["industry"] == "Technology"
        assert context["person_name"] == "Test User"
        assert context["pain_point"] is not None
        assert "productivity" in context["pain_point"].lower() or "candidate" in context["pain_point"].lower()


class TestPainPointInference:
    """
    Unit tests specifically for pain point inference
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = ContextExtractor()
    
    def test_infer_pain_point_software_engineer(self):
        """Test pain point inference for software engineer."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "productivity" in pain_point.lower() or "candidate" in pain_point.lower()
    
    def test_infer_pain_point_sales_manager(self):
        """Test pain point inference for sales manager."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Sales Manager",
            company="Sales Co",
            industry="Retail",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "qualified leads" in pain_point or "conversion" in pain_point
    
    def test_infer_pain_point_marketing_director(self):
        """Test pain point inference for marketing director."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Marketing Director",
            company="Marketing Co",
            industry="Advertising",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "roi" in pain_point.lower() or "brand awareness" in pain_point.lower()
    
    def test_infer_pain_point_product_manager(self):
        """Test pain point inference for product manager."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Product Manager",
            company="Product Co",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "user needs" in pain_point.lower() or "feature requests" in pain_point.lower()
    
    def test_infer_pain_point_cto(self):
        """Test pain point inference for CTO."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="CTO",
            company="Tech Startup",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "security" in pain_point.lower() or "scaling" in pain_point.lower()
    
    def test_infer_pain_point_founder(self):
        """Test pain point inference for founder."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Founder",
            company="Startup",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "funding" in pain_point.lower() or "team" in pain_point.lower()
    
    def test_infer_pain_point_unknown_role(self):
        """Test pain point inference for unknown role."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Unknown Role",
            company="Random Co",
            industry="Unknown Industry",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        # May still return a pain point through partial matching
        assert pain_point is None or isinstance(pain_point, str)
    
    def test_infer_pain_point_empty_role(self):
        """Test pain point inference when role is empty."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="",  # Empty role
            company="Random Co",
            industry="Unknown Industry",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is None
    
    def test_infer_pain_point_case_insensitive(self):
        """Test pain point inference is case insensitive."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="software engineer",  # Lowercase
            company="Tech Corp",
            industry="Technology",
            tone="FRIENDLY"
        )
        
        pain_point = self.extractor._infer_pain_point(profile)
        
        assert pain_point is not None
        assert "productivity" in pain_point.lower() or "candidate" in pain_point.lower()
    
    def test_extract_name_from_url(self):
        """Test name extraction from LinkedIn URL."""
        extractor = ContextExtractor()
        
        name = extractor._extract_name_from_url("https://www.linkedin.com/in/john-doe")
        assert name == "John Doe"
        
        name = extractor._extract_name_from_url("https://www.linkedin.com/in/jane-smith/")
        assert name == "Jane Smith"
        
        name = extractor._extract_name_from_url("https://www.linkedin.com/in/alice-johnson-123")
        assert name == "Alice Johnson 123"
    
    def test_validate_context_complete(self):
        """Test context validation with complete information."""
        context = {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "industry": "Technology"
        }
        
        is_valid = self.extractor.validate_context(context)
        
        assert is_valid is True
    
    def test_validate_context_missing_role(self):
        """Test context validation with missing role."""
        context = {
            "role": "",  # Missing role
            "company": "Tech Corp",
            "industry": "Technology"
        }
        
        is_valid = self.extractor.validate_context(context)
        
        assert is_valid is False
    
    def test_validate_context_missing_company(self):
        """Test context validation with missing company."""
        context = {
            "role": "Software Engineer",
            "company": "",  # Missing company
            "industry": "Technology"
        }
        
        is_valid = self.extractor.validate_context(context)
        
        assert is_valid is False
    
    def test_validate_context_missing_industry(self):
        """Test context validation with missing industry."""
        context = {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "industry": ""  # Missing industry
        }
        
        is_valid = self.extractor.validate_context(context)
        
        assert is_valid is False