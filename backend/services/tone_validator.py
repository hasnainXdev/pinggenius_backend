import re
from typing import Dict, List, Tuple, Optional
from models.validation import ToneValidatorConfiguration
from utils.logging import log_tone_validation_result


class ToneValidatorService:
    """
    Service for validating that generated messages adhere to requested tone parameters
    using prescriptive rules and regenerating messages that violate tone requirements.
    """
    
    def __init__(self):
        # Define configurations for different tones
        self.tone_configs = {
            "friendly": ToneValidatorConfiguration(
                tone_type="friendly",
                emoji_limit=2,
                slang_allowed=True,
                formality_level=2,
                exclamation_limit=2,
                capitalization_rules="casual"
            ),
            "direct": ToneValidatorConfiguration(
                tone_type="direct",
                emoji_limit=1,
                slang_allowed=False,
                formality_level=3,
                exclamation_limit=1,
                capitalization_rules="standard"
            ),
            "authority": ToneValidatorConfiguration(
                tone_type="authority",
                emoji_limit=0,
                slang_allowed=False,
                formality_level=5,
                exclamation_limit=1,
                capitalization_rules="formal"
            ),
            "casual": ToneValidatorConfiguration(
                tone_type="casual",
                emoji_limit=3,
                slang_allowed=True,
                formality_level=1,
                exclamation_limit=3,
                capitalization_rules="relaxed"
            )
        }
    
    def get_tone_config(self, tone: str) -> Optional[ToneValidatorConfiguration]:
        """
        Gets the configuration for a specific tone.
        
        Args:
            tone: The requested tone
            
        Returns:
            ToneValidatorConfiguration if found, None otherwise
        """
        return self.tone_configs.get(tone.lower())
    
    def validate_message_tone(self, message: str, tone: str) -> Tuple[bool, List[str]]:
        """
        Validates if a message adheres to the specified tone parameters.
        
        Args:
            message: The message to validate
            tone: The requested tone
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        config = self.get_tone_config(tone.lower())
        if not config:
            return False, [f"Unsupported tone: {tone}"]
        
        violations = []
        
        # Check emoji count
        emoji_count = self._count_emojis(message)
        if emoji_count > config.emoji_limit:
            violations.append(f"Too many emojis: {emoji_count} (max {config.emoji_limit})")
        
        # Check slang if not allowed
        if not config.slang_allowed and self._contains_slang(message):
            violations.append("Message contains slang but tone doesn't allow it")
        
        # Check exclamation marks
        exclamation_count = message.count('!')
        if exclamation_count > config.exclamation_limit:
            violations.append(f"Too many exclamation marks: {exclamation_count} (max {config.exclamation_limit})")
        
        # Check formality based on capitalization rules
        if config.formality_level >= 4 and self._appears_too_casual(message):
            violations.append("Message appears too casual for requested formal tone")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def _count_emojis(self, text: str) -> int:
        """
        Counts the number of emojis in a text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Number of emojis found
        """
        # Simple regex to match common emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+",
            re.UNICODE
        )
        return len(emoji_pattern.findall(text))
    
    def _contains_slang(self, text: str) -> bool:
        """
        Checks if the text contains slang terms.
        
        Args:
            text: The text to analyze
            
        Returns:
            Boolean indicating if slang is detected
        """
        slang_terms = [
            'gonna', 'wanna', 'gotta', 'hafta', 'lemme', 'gimme', 'outta',
            'dunno', 'kinda', 'sorta', "y'all", 'folks', 'cool', 'awesome',
            'rad', 'lit', 'sick', 'dope', 'chill', 'hangout', 'buddy',
            'pal', 'mate', 'dude', 'bro', 'sis', 'homie', 'crew', 'gang',
            'yeet', 'bae', 'fam', 'squad', 'flex', 'ghost', 'slide'
        ]
        
        text_lower = text.lower()
        return any(slang in text_lower for slang in slang_terms)
    
    def _appears_too_casual(self, text: str) -> bool:
        """
        Checks if the text appears too casual for formal tones.
        
        Args:
            text: The text to analyze
            
        Returns:
            Boolean indicating if text appears too casual
        """
        casual_indicators = [
            r'\byo\b',  # 'yo'
            r'\bhey\b',  # 'hey'
            r'\bhi there\b',  # 'hi there'
            r'\bsup\b',  # 'sup'
            r'\bwassup\b',  # 'wassup'
            r'\bwhats up\b',  # 'whats up'
            r'\bhowdy\b',  # 'howdy'
            r'\bhey guys?\b',  # 'hey guys/y'
            r'\bhi folks?\b',  # 'hi folks'
            r'\byeah\b',  # 'yeah' (vs 'yes')
        ]
        
        text_lower = text.lower()
        for pattern in casual_indicators:
            if re.search(pattern, text_lower):
                return True
                
        return False
    
    def validate_and_regenerate_if_needed(self, message: str, tone: str, 
                                         regenerate_func=None) -> Tuple[str, bool, List[str]]:
        """
        Validates a message's tone and regenerates it if needed.
        
        Args:
            message: The message to validate
            tone: The requested tone
            regenerate_func: Optional function to regenerate the message if validation fails
            
        Returns:
            Tuple of (validated_message, was_regenerated, violations)
        """
        is_valid, violations = self.validate_message_tone(message, tone)
        
        log_tone_validation_result(message, tone, is_valid, False)
        
        if is_valid:
            return message, False, violations
        
        # If validation fails and we have a regeneration function, try to regenerate
        if regenerate_func:
            regenerated_message = regenerate_func(message, tone)
            is_valid_after_regenerate, new_violations = self.validate_message_tone(regenerated_message, tone)
            
            log_tone_validation_result(regenerated_message, tone, is_valid_after_regenerate, True)
            
            if is_valid_after_regenerate:
                return regenerated_message, True, new_violations
            else:
                # If regeneration didn't fix the issues, return the original with violations
                return regenerated_message, True, new_violations
        
        # If no regeneration function provided, return original with violations
        return message, False, violations