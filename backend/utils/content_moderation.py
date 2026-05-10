import re
from typing import List, Tuple


class ContentModeration:
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
        return len(content) <= max_chars

    def truncate_to_limit(self, content: str, max_chars: int = 240) -> str:
        if len(content) <= max_chars:
            return content
        truncated = content[:max_chars]
        last_end = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
        if last_end != -1 and last_end > max_chars * 0.8:
            return truncated[:last_end + 1]
        return truncated

    def check_for_prohibited_phrases(self, content: str) -> Tuple[bool, List[str]]:
        content_lower = content.lower()
        found = [p for p in self.prohibited_phrases if p.lower() in content_lower]
        return len(found) > 0, found

    def remove_prohibited_phrases(self, content: str) -> str:
        cleaned = content
        for phrase in self.prohibited_phrases:
            cleaned = re.sub(r'\b' + re.escape(phrase) + r'\b', '', cleaned, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', cleaned).strip()

    def validate_tone(self, content: str, required_tone: str = None) -> bool:
        if not required_tone:
            return True
        content_lower = content.lower()
        indicators = {
            "authority": ["our solution", "industry leader", "best practice", "according to research"],
            "friendly": ["hi there", "hope you're", "great to meet", "nice to connect"],
            "casual": ["hey", "cool", "awesome", "just wanted"],
        }
        for indicator in indicators.get(required_tone.lower(), []):
            if indicator in content_lower:
                return True
        return True

    def moderate_content(self, content: str, required_tone: str = None) -> dict:
        contains_prohibited, found_phrases = self.check_for_prohibited_phrases(content)
        return {
            'within_character_limit': self.enforce_character_limit(content),
            'contains_prohibited_phrases': contains_prohibited,
            'found_prohibited_phrases': found_phrases,
            'tone_valid': self.validate_tone(content, required_tone),
            'cleaned_content': self.remove_prohibited_phrases(content) if contains_prohibited else content,
        }
