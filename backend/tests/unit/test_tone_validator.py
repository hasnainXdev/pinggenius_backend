import pytest
from services.tone_validator import ToneValidatorService


class TestToneValidatorService:
    """
    Unit tests for ToneValidatorService
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ToneValidatorService()
    
    def test_get_tone_config_friendly(self):
        """Test getting tone configuration for friendly tone."""
        config = self.service.get_tone_config("friendly")
        
        assert config is not None
        assert config.tone_type == "friendly"
        assert config.emoji_limit == 2
        assert config.slang_allowed is True
        assert config.formality_level == 2
        assert config.exclamation_limit == 2
    
    def test_get_tone_config_authority(self):
        """Test getting tone configuration for authority tone."""
        config = self.service.get_tone_config("authority")
        
        assert config is not None
        assert config.tone_type == "authority"
        assert config.emoji_limit == 0
        assert config.slang_allowed is False
        assert config.formality_level == 5
        assert config.exclamation_limit == 1
    
    def test_get_tone_config_invalid(self):
        """Test getting tone configuration for invalid tone."""
        config = self.service.get_tone_config("invalid_tone")
        
        assert config is None
    
    def test_validate_message_tone_friendly_valid(self):
        """Test validating a message with appropriate friendly tone."""
        message = "Hey there! Hope you're having a great day 😊"
        is_valid, violations = self.service.validate_message_tone(message, "friendly")
        
        assert is_valid is True
        assert len(violations) == 0
    
    def test_validate_message_tone_friendly_too_many_emojis(self):
        """Test validating a message with too many emojis for friendly tone."""
        message = "Hey there! 😊😊😊😊 This is a friendly message"
        is_valid, violations = self.service.validate_message_tone(message, "friendly")
        
        assert is_valid is False
        assert "Too many emojis: 4 (max 2)" in violations
    
    def test_validate_message_tone_authority_no_slang(self):
        """Test validating a message with appropriate authority tone."""
        message = "I hope this message finds you well. I would like to discuss a potential opportunity."
        is_valid, violations = self.service.validate_message_tone(message, "authority")
        
        assert is_valid is True
        assert len(violations) == 0
    
    def test_validate_message_tone_authority_with_slang(self):
        """Test validating a message with slang for authority tone."""
        message = "Hey dude, this is totally awesome and rad!"
        is_valid, violations = self.service.validate_message_tone(message, "authority")
        
        assert is_valid is False
        assert "Message contains slang but tone doesn't allow it" in violations
    
    def test_validate_message_tone_direct_exclamation_limit(self):
        """Test validating a message with too many exclamation marks for direct tone."""
        message = "We need to talk now!!! This is urgent!!!"
        is_valid, violations = self.service.validate_message_tone(message, "direct")
        
        assert is_valid is False
        assert "Too many exclamation marks: 6 (max 1)" in violations
    
    def test_validate_message_tone_casual_with_slang(self):
        """Test validating a message with slang for casual tone (should be valid)."""
        message = "Hey man, this is super cool and awesome!"
        is_valid, violations = self.service.validate_message_tone(message, "casual")
        
        # Casual allows slang, so this should be valid regardless of slang
        # The validation might fail for other reasons like formality
        assert is_valid is True or "Message contains slang but tone doesn't allow it" not in violations
    
    def test_count_emojis_simple(self):
        """Test counting emojis in a simple message."""
        text = "Hello! 😊 How are you?"
        count = self.service._count_emojis(text)
        
        assert count == 1
    
    def test_count_emojis_multiple(self):
        """Test counting multiple emojis in a message."""
        text = "Hi there! 😊👍🎉 How's it going?"
        count = self.service._count_emojis(text)
        
        assert count == 3
    
    def test_count_emojis_none(self):
        """Test counting emojis when there are none."""
        text = "Hello! How are you?"
        count = self.service._count_emojis(text)
        
        assert count == 0
    
    def test_contains_slang_positive(self):
        """Test detecting slang in a message."""
        text = "This is really cool and awesome, dude!"
        has_slang = self.service._contains_slang(text)
        
        assert has_slang is True
    
    def test_contains_slang_negative(self):
        """Test detecting slang in a message without slang."""
        text = "This is quite interesting and wonderful."
        has_slang = self.service._contains_slang(text)
        
        assert has_slang is False
    
    def test_appears_too_casual_positive(self):
        """Test detecting if a message appears too casual for formal tone."""
        text = "Hey there folks, hope you're doing great!"
        is_casual = self.service._appears_too_casual(text)
        
        assert is_casual is True
    
    def test_appears_too_casual_negative(self):
        """Test detecting if a formal message appears too casual."""
        text = "Dear Sir or Madam, I hope this message finds you well."
        is_casual = self.service._appears_too_casual(text)
        
        assert is_casual is False


class TestToneValidationAndRegeneration:
    """
    Unit tests for tone validation and regeneration functionality
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = ToneValidatorService()
    
    def test_validate_and_regenerate_if_needed_valid(self):
        """Test validation and regeneration when message is already valid."""
        message = "This is a professionally written message."
        regenerated_msg, was_regenerated, violations = self.service.validate_and_regenerate_if_needed(
            message, "authority"
        )
        
        assert regenerated_msg == message
        assert was_regenerated is False
        assert len(violations) == 0
    
    def test_validate_and_regenerate_if_needed_invalid(self):
        """Test validation and regeneration when message is invalid."""
        message = "Hey bro! This is totally rad and awesome! 😊😊😊😊"
        
        # Define a simple regeneration function for testing
        def simple_regeneration(original, tone):
            return f"[REGENERATED] This is a properly toned message for {tone}."
        
        regenerated_msg, was_regenerated, violations = self.service.validate_and_regenerate_if_needed(
            message, "authority", simple_regeneration
        )
        
        assert "[REGENERATED]" in regenerated_msg
        assert "authority" in regenerated_msg
        assert was_regenerated is True
        assert len(violations) > 0  # Original message had violations
    
    def test_validate_and_regenerate_if_needed_no_regeneration_func(self):
        """Test validation when no regeneration function is provided."""
        message = "Hey bro! This is totally rad and awesome! 😊😊😊😊"
        
        regenerated_msg, was_regenerated, violations = self.service.validate_and_regenerate_if_needed(
            message, "authority"
        )
        
        # Without a regeneration function, the original message should be returned
        # but was_regenerated should be False
        assert regenerated_msg == message
        assert was_regenerated is False
        assert len(violations) > 0  # Original message had violations