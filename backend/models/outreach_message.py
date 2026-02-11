from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class OutreachMessage(BaseModel):
    """
    An individual message in an outreach sequence.
    """
    id: Optional[str] = None
    sequence_id: str  # Reference to the OutreachSequence
    message_order: int  # Position in the sequence (0 for connection note, 1+ for DMs/follow-ups)
    content: str  # The actual message content
    character_count: Optional[int] = None  # Number of characters in the message
    tone_compliant: bool = False  # Whether the message meets tone requirements
    contains_prohibited_phrases: bool = False  # Whether the message contains blacklisted phrases
    references_anchor: bool = False  # Whether the message references the selected anchor
    created_at: datetime = datetime.now()

    @field_validator('content')
    def validate_content_length(cls, v):
        """Validate that content is ≤ 240 characters."""
        if len(v) > 240:
            raise ValueError('Content must be ≤ 240 characters')
        return v

    @field_validator('message_order')
    def validate_message_order(cls, v):
        """Validate that message_order is ≥ 0."""
        if v < 0:
            raise ValueError('Message order must be ≥ 0')
        return v

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate character count if not provided
        if self.character_count is None and self.content:
            self.character_count = len(self.content)

    def check_anchor_reference(self, anchor_point: str) -> bool:
        """
        Check if this message references the given anchor point.

        Args:
            anchor_point: The anchor point to check for

        Returns:
            Boolean indicating if the message references the anchor
        """
        if not anchor_point or not self.content:
            return False

        # Convert both to lowercase for case-insensitive comparison
        anchor_lower = anchor_point.lower()
        content_lower = self.content.lower()

        # Check if the anchor appears in the content
        self.references_anchor = anchor_lower in content_lower
        return self.references_anchor

    def validate_message_quality(self, anchor_point: str = None,
                               prohibited_phrases: list = None,
                               required_tone: str = None,
                               max_chars: int = 240) -> dict:
        """
        Validate the quality of this message against various criteria.

        Args:
            anchor_point: Optional anchor point to check for references
            prohibited_phrases: Optional list of prohibited phrases to check for
            required_tone: Optional required tone to validate
            max_chars: Maximum number of characters allowed (default 240)

        Returns:
            Dictionary with validation results
        """
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()

        results = {
            'content_length_valid': len(self.content) <= max_chars,
            'message_order_valid': self.message_order >= 0,
            'references_anchor': False,
            'contains_prohibited_phrases': False,
            'tone_compliant': self.tone_compliant,
            'character_count': len(self.content),
            'max_allowed_chars': max_chars
        }

        # Check anchor reference if anchor_point is provided
        if anchor_point:
            results['references_anchor'] = self.check_anchor_reference(anchor_point)

        # Check for prohibited phrases if list is provided
        if prohibited_phrases:
            content_lower = self.content.lower()
            for phrase in prohibited_phrases:
                if phrase.lower() in content_lower:
                    results['contains_prohibited_phrases'] = True
                    break
        else:
            # Use the default prohibited phrases from the content moderator
            phrase_check = moderator.filter_prohibited_phrases_detailed(self.content)
            results['contains_prohibited_phrases'] = phrase_check['contains_prohibited']
            results['found_prohibited_phrases'] = phrase_check['found_phrases']

        # Validate tone if required
        if required_tone:
            results['tone_compliant'] = moderator.validate_tone(self.content, required_tone)
            results['tone_analysis'] = moderator.analyze_tone(self.content)

        # Character limit check with details
        results['character_limit_check'] = moderator.enforce_character_limit_detailed(self.content, max_chars)

        return results

    def apply_full_quality_control(self, anchor_point: str = None,
                                  required_tone: str = None,
                                  prohibited_phrases: list = None) -> dict:
        """
        Apply full quality control to this message.

        Args:
            anchor_point: Optional anchor point to check for references
            required_tone: Optional required tone to validate
            prohibited_phrases: Optional list of prohibited phrases to check for

        Returns:
            Dictionary with comprehensive quality control results
        """
        from ..utils.content_moderation import ContentModeration
        from ..services.context_analyzer import ContextAnalyzer

        # Use the context analyzer's quality control method
        analyzer = ContextAnalyzer()
        quality_result = analyzer.apply_quality_control_to_message(
            self.content,
            anchor_point,
            required_tone
        )

        # Also run the model's own validation
        model_validation = self.validate_message_quality(anchor_point, prohibited_phrases, required_tone)

        # Combine results
        return {
            'model_validation': model_validation,
            'service_quality_check': quality_result,
            'overall_quality_pass': quality_result['overall_quality_pass'] and model_validation['content_length_valid'],
            'final_tone_compliant': quality_result['tone_check']['tone_compliant'],
            'final_references_anchor': quality_result['anchor_reference_check']['references_anchor']
        }