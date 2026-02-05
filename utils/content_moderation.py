import re
from typing import List, Tuple


class ContentModeration:
    """
    Utilities for content validation and moderation.
    """
    
    def __init__(self):
        self.prohibited_phrases = [
            "intrigued by", "unique challenges", "just checking in", 
            "gentle nudge", "hopping on a quick call", "free consultation",
            "thought you might be interested", "would love to connect",
            "I noticed you're", "I see you work at", "I noticed your post",
            "wondering if you'd be open to", "hope you're doing well",
            "I hope this finds you well", "thanks for connecting",
            "would appreciate your thoughts", "looking forward to hearing from you"
        ]
        self.max_characters = 240

    def enforce_character_limit(self, content: str, max_chars: int = 240) -> bool:
        """
        Check if content is within the character limit.

        Args:
            content: The content to check
            max_chars: Maximum number of characters allowed (default 240)

        Returns:
            Boolean indicating if content is within limit
        """
        return len(content) <= max_chars

    def enforce_character_limit_detailed(self, content: str, max_chars: int = 240) -> dict:
        """
        Check if content is within the character limit with detailed results.

        Args:
            content: The content to check
            max_chars: Maximum number of characters allowed (default 240)

        Returns:
            Dictionary with detailed validation results
        """
        content_length = len(content)
        is_within_limit = content_length <= max_chars
        excess_chars = max(0, content_length - max_chars)

        return {
            'is_within_limit': is_within_limit,
            'content_length': content_length,
            'max_allowed': max_chars,
            'excess_characters': excess_chars,
            'compliance_percentage': (content_length / max_chars) * 100 if max_chars > 0 else 0
        }

    def truncate_to_limit(self, content: str, max_chars: int = 240) -> str:
        """
        Truncate content to fit within the character limit.

        Args:
            content: The content to truncate
            max_chars: Maximum number of characters allowed (default 240)

        Returns:
            Truncated content string
        """
        if len(content) <= max_chars:
            return content

        # Try to truncate at sentence boundary if possible
        truncated = content[:max_chars]

        # Find the last sentence ending before the limit
        last_sentence_end = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))

        if last_sentence_end != -1 and last_sentence_end > max_chars * 0.8:  # Only if it's reasonably close to the end
            return truncated[:last_sentence_end + 1]

        # If no sentence boundary found, return the truncated content
        return truncated

    def check_for_prohibited_phrases(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check if content contains prohibited phrases.

        Args:
            content: The content to check

        Returns:
            Tuple of (contains_prohibited, list_of_found_phrases)
        """
        found_phrases = []
        content_lower = content.lower()

        for phrase in self.prohibited_phrases:
            if phrase.lower() in content_lower:
                found_phrases.append(phrase)

        return len(found_phrases) > 0, found_phrases

    def filter_prohibited_phrases_detailed(self, content: str) -> dict:
        """
        Check for prohibited phrases with detailed results.

        Args:
            content: The content to check

        Returns:
            Dictionary with detailed filtering results
        """
        found_phrases = []
        content_lower = content.lower()

        for phrase in self.prohibited_phrases:
            if phrase.lower() in content_lower:
                found_phrases.append({
                    'phrase': phrase,
                    'position': content_lower.find(phrase.lower()),
                    'case_match': phrase in content  # Whether it was an exact case match
                })

        return {
            'contains_prohibited': len(found_phrases) > 0,
            'found_phrases': found_phrases,
            'prohibited_count': len(found_phrases),
            'clean_content': self.remove_prohibited_phrases(content) if found_phrases else content
        }

    def add_prohibited_phrase(self, phrase: str):
        """
        Add a new prohibited phrase to the list.

        Args:
            phrase: The phrase to add to the prohibited list
        """
        if phrase not in self.prohibited_phrases:
            self.prohibited_phrases.append(phrase)

    def remove_prohibited_phrase(self, phrase: str):
        """
        Remove a prohibited phrase from the list.

        Args:
            phrase: The phrase to remove from the prohibited list
        """
        if phrase in self.prohibited_phrases:
            self.prohibited_phrases.remove(phrase)

    def remove_prohibited_phrases(self, content: str) -> str:
        """
        Remove prohibited phrases from content.
        
        Args:
            content: The content to clean
            
        Returns:
            Cleaned content with prohibited phrases removed
        """
        cleaned_content = content
        
        for phrase in self.prohibited_phrases:
            # Use word boundaries to avoid partial matches within other words
            pattern = r'\b' + re.escape(phrase) + r'\b'
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
            
        # Clean up any double spaces that might result from removal
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
        
        return cleaned_content

    def validate_tone(self, content: str, required_tone: str = None) -> bool:
        """
        Validate that content meets tone requirements.

        Args:
            content: The content to validate
            required_tone: The required tone (Authority, Friendly, Casual)

        Returns:
            Boolean indicating if tone requirements are met
        """
        # For now, we'll just return True
        # In a real implementation, this would analyze the content for tone
        if not required_tone:
            return True

        # Simple heuristics for different tones
        content_lower = content.lower()

        if required_tone.lower() == "authority":
            # Authority tone typically has more formal language
            authority_indicators = ["our solution", "industry leader", "best practice", "according to research"]
            for indicator in authority_indicators:
                if indicator in content_lower:
                    return True
        elif required_tone.lower() == "friendly":
            # Friendly tone typically has more personal language
            friendly_indicators = ["hi there", "hope you're", "great to meet", "nice to connect"]
            for indicator in friendly_indicators:
                if indicator in content_lower:
                    return True
        elif required_tone.lower() == "casual":
            # Casual tone typically has informal language
            casual_indicators = ["hey", "cool", "awesome", "just wanted"]
            for indicator in casual_indicators:
                if indicator in content_lower:
                    return True

        # If no specific indicators found, default to True for now
        return True

    def analyze_tone(self, content: str) -> dict:
        """
        Analyze the tone of the content and provide detailed results.

        Args:
            content: The content to analyze

        Returns:
            Dictionary with tone analysis results
        """
        content_lower = content.lower()

        # Define tone indicators
        tone_indicators = {
            "authority": [
                "our solution", "industry leader", "best practice", "according to research",
                "data shows", "study indicates", "expert recommendation", "proven method"
            ],
            "friendly": [
                "hi there", "hope you're", "great to meet", "nice to connect",
                "wondering if", "would love to", "thinking about", "reaching out"
            ],
            "casual": [
                "hey", "cool", "awesome", "just wanted", "thought you'd like",
                "check this out", "quick question", "random thought"
            ]
        }

        # Count indicators for each tone
        tone_scores = {}
        for tone, indicators in tone_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content_lower)
            tone_scores[tone] = count

        # Determine dominant tone
        dominant_tone = max(tone_scores, key=tone_scores.get) if any(tone_scores.values()) else "neutral"

        return {
            "dominant_tone": dominant_tone,
            "tone_scores": tone_scores,
            "confidence": max(tone_scores.values()) / sum(tone_scores.values()) if sum(tone_scores.values()) > 0 else 0,
            "suggestions": self._get_tone_suggestions(content, dominant_tone)
        }

    def _get_tone_suggestions(self, content: str, current_tone: str) -> list:
        """
        Get suggestions for improving the tone of the content.

        Args:
            content: The content to analyze
            current_tone: The currently detected tone

        Returns:
            List of suggestions for tone improvement
        """
        suggestions = []

        if current_tone == "neutral":
            suggestions.append("Consider adding more personality to establish a clear tone")

        # Check for mixed tones
        content_lower = content.lower()
        authority_count = sum(1 for indicator in ["our solution", "industry leader", "best practice"] if indicator in content_lower)
        friendly_count = sum(1 for indicator in ["hi there", "hope you're", "great to meet"] if indicator in content_lower)
        casual_count = sum(1 for indicator in ["hey", "cool", "awesome"] if indicator in content_lower)

        if sum([authority_count, friendly_count, casual_count]) > 2:
            suggestions.append("Content seems to mix multiple tones; consider choosing one consistent tone")

        return suggestions

    def moderate_content(self, content: str, required_tone: str = None) -> dict:
        """
        Perform comprehensive content moderation.
        
        Args:
            content: The content to moderate
            required_tone: The required tone (Authority, Friendly, Casual)
            
        Returns:
            Dictionary with moderation results
        """
        results = {
            'within_character_limit': self.enforce_character_limit(content),
            'contains_prohibited_phrases': False,
            'found_prohibited_phrases': [],
            'tone_valid': self.validate_tone(content, required_tone),
            'cleaned_content': content
        }
        
        # Check for prohibited phrases
        contains_prohibited, found_phrases = self.check_for_prohibited_phrases(content)
        results['contains_prohibited_phrases'] = contains_prohibited
        results['found_prohibited_phrases'] = found_phrases
        
        # Clean content if needed
        if contains_prohibited:
            results['cleaned_content'] = self.remove_prohibited_phrases(content)
        
        return results