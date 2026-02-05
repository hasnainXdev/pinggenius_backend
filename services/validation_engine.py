from typing import List, Tuple
from ..models.linkedin_profile import LinkedInProfile
from ..models.context_validation_result import ContextValidationResult
from ..models.analysis_result import AnalysisResult
from enum import Enum


class GenerationMode(str, Enum):
    PRECISION = "Precision"
    SAFE_PERSONALIZATION = "Safe Personalization"
    EXPLORATORY = "Exploratory"


class ValidationEngine:
    """
    Core validation engine for LinkedIn context validation.
    """

    def __init__(self):
        self.prohibited_phrases = [
            "intrigued by", "unique challenges", "just checking in",
            "gentle nudge", "hopping on a quick call", "free consultation",
            "thought you might be interested", "would love to connect",
            "I noticed you're", "I see you work at", "I noticed your post"
        ]

    def validate_context(self, profile: LinkedInProfile) -> ContextValidationResult:
        """
        Validate that sufficient context exists in the LinkedIn profile.

        Args:
            profile: LinkedInProfile to validate

        Returns:
            ContextValidationResult with validation details
        """
        missing_fields = profile.validate_required_fields()

        context_depth_score = self.calculate_context_depth_score(profile)
        validation_passed = len(missing_fields) == 0

        # Determine generation mode based on context depth score
        if context_depth_score >= 3:
            generation_mode = GenerationMode.PRECISION.value
        elif context_depth_score == 2:
            generation_mode = GenerationMode.SAFE_PERSONALIZATION.value
        else:
            generation_mode = GenerationMode.EXPLORATORY.value

        # For now, we'll set anchor_point to None; it will be set during analysis
        result = ContextValidationResult(
            profile_id=profile.id or "",
            context_depth_score=context_depth_score,
            validation_passed=validation_passed,
            missing_fields=missing_fields,
            anchor_point=None,
            generation_mode=generation_mode
        )

        return result

    def validate_profile_for_outreach(self, profile: LinkedInProfile) -> Tuple[bool, List[str], int]:
        """
        Comprehensive validation of a LinkedIn profile for outreach generation.

        Args:
            profile: LinkedInProfile to validate

        Returns:
            Tuple of (is_valid, missing_fields, context_depth_score)
        """
        missing_fields = profile.validate_required_fields()
        context_depth_score = self.calculate_context_depth_score(profile)
        is_valid = len(missing_fields) == 0

        return is_valid, missing_fields, context_depth_score

    def calculate_context_depth_score(self, profile: LinkedInProfile) -> int:
        """
        Calculate context depth score based on the presence of key fields.

        Scoring:
        - Role or Title present: +1 point
        - Company or Industry present: +1 point
        - Pain Points present: +1 point
        - Recent Activity present: +1 point
        - Maximum possible score: 4 points

        Args:
            profile: LinkedInProfile to score

        Returns:
            Integer score from 0-4
        """
        score = 0

        # Check for role or title
        if profile.role or profile.title:
            score += 1

        # Check for company or industry
        if profile.company or profile.industry:
            score += 1

        # Check for pain points
        if profile.pain_points and len(profile.pain_points) > 0:
            score += 1

        # Check for recent activity
        if profile.recent_activity and len(profile.recent_activity) > 0:
            score += 1

        return score

    def get_generation_mode_from_score(self, context_depth_score: int) -> str:
        """
        Determine the generation mode based on context depth score.

        Args:
            context_depth_score: The calculated context depth score

        Returns:
            Generation mode as a string
        """
        if context_depth_score >= 3:
            return GenerationMode.PRECISION.value
        elif context_depth_score == 2:
            return GenerationMode.SAFE_PERSONALIZATION.value
        else:
            return GenerationMode.EXPLORATORY.value

    def validate_anchor_consistency(self, anchor_point: str, message_content: str) -> bool:
        """
        Validate that a message references the selected anchor point.

        Args:
            anchor_point: The selected anchor point
            message_content: The content of the message to validate

        Returns:
            Boolean indicating if the message references the anchor
        """
        # Simple check: does the anchor appear in the message content?
        # In a real implementation, this could be more sophisticated
        if not anchor_point or not message_content:
            return False

        # Convert both to lowercase for case-insensitive comparison
        anchor_lower = anchor_point.lower()
        content_lower = message_content.lower()

        # Check if the anchor appears in the content
        return anchor_lower in content_lower

    def validate_anchor_reference_in_message(self, anchor_point: str, message_content: str) -> dict:
        """
        Validate anchor reference in a message with detailed results.

        Args:
            anchor_point: The selected anchor point
            message_content: The content of the message to validate

        Returns:
            Dictionary with validation details
        """
        if not anchor_point or not message_content:
            return {
                "references_anchor": False,
                "match_percentage": 0.0,
                "details": "Either anchor point or message content is empty"
            }

        # Convert both to lowercase for case-insensitive comparison
        anchor_lower = anchor_point.lower()
        content_lower = message_content.lower()

        # Check if the anchor appears in the content
        references_anchor = anchor_lower in content_lower

        # Calculate match percentage based on how much of the anchor is found
        match_percentage = 0.0
        if references_anchor:
            # If the anchor is found, the match is 100%
            match_percentage = 100.0
        else:
            # Calculate partial match if any part of the anchor is found
            words_in_anchor = anchor_lower.split()
            matched_words = sum(1 for word in words_in_anchor if word in content_lower)
            if len(words_in_anchor) > 0:
                match_percentage = (matched_words / len(words_in_anchor)) * 100

        return {
            "references_anchor": references_anchor,
            "match_percentage": match_percentage,
            "details": f"Anchor '{anchor_point}' {'found' if references_anchor else 'not found'} in message"
        }

    def validate_anchor_consistency_across_sequence(self, anchor_point: str, messages: List[str]) -> dict:
        """
        Validate that all messages in a sequence reference the selected anchor point.

        Args:
            anchor_point: The selected anchor point
            messages: List of message contents in the sequence

        Returns:
            Dictionary with validation results for the entire sequence
        """
        if not anchor_point or not messages:
            return {
                "all_reference_anchor": False,
                "messages_referencing_anchor": 0,
                "total_messages": len(messages) if messages else 0,
                "details": "Either anchor point or messages list is empty"
            }

        messages_referencing_anchor = 0
        message_results = []

        for i, message in enumerate(messages):
            validation_result = self.validate_anchor_reference_in_message(anchor_point, message)
            message_results.append({
                "message_index": i,
                "content_preview": message[:50] + "..." if len(message) > 50 else message,
                **validation_result
            })

            if validation_result["references_anchor"]:
                messages_referencing_anchor += 1

        all_reference_anchor = messages_referencing_anchor == len(messages)

        return {
            "all_reference_anchor": all_reference_anchor,
            "messages_referencing_anchor": messages_referencing_anchor,
            "total_messages": len(messages),
            "consistency_percentage": (messages_referencing_anchor / len(messages)) * 100 if messages else 0,
            "message_results": message_results
        }

    def validate_anchor_reference_for_follow_up(self, anchor_point: str, follow_up_message: str,
                                             previous_messages: List[str] = None) -> dict:
        """
        Validate that a follow-up message references the anchor and builds on previous messages.

        Args:
            anchor_point: The selected anchor point
            follow_up_message: The content of the follow-up message
            previous_messages: List of previous messages in the sequence (optional)

        Returns:
            Dictionary with validation results for the follow-up
        """
        # Validate anchor reference in the follow-up message
        anchor_validation = self.validate_anchor_reference_in_message(anchor_point, follow_up_message)

        # Check if the follow-up builds on previous messages (if provided)
        builds_on_previous = False
        if previous_messages:
            # Check if the follow-up references content from previous messages
            follow_up_lower = follow_up_message.lower()
            for prev_message in previous_messages:
                # Look for references to previous content
                prev_content = prev_message.lower()
                # This is a simple check - in practice, this could be more sophisticated
                if any(word in follow_up_lower for word in prev_content.split()[:10]):  # Check first 10 words
                    builds_on_previous = True
                    break

        return {
            "follow_up_references_anchor": anchor_validation["references_anchor"],
            "follow_up_builds_on_previous": builds_on_previous,
            "anchor_match_details": anchor_validation,
            "continuity_check": {
                "references_previous_content": builds_on_previous,
                "previous_messages_count": len(previous_messages) if previous_messages else 0
            },
            "overall_valid": anchor_validation["references_anchor"]  # For now, anchor reference is the key factor
        }

    def ensure_follow_up_continuity(self, anchor_point: str, follow_up_message: str,
                                 previous_messages: List[str] = None) -> dict:
        """
        Ensure continuity in follow-up messages by validating anchor reference and context building.

        Args:
            anchor_point: The selected anchor point for the sequence
            follow_up_message: The follow-up message to validate
            previous_messages: Previous messages in the sequence

        Returns:
            Dictionary with continuity validation results
        """
        validation_result = self.validate_anchor_reference_for_follow_up(
            anchor_point,
            follow_up_message,
            previous_messages
        )

        # Additional checks for continuity
        issues = []
        suggestions = []

        if not validation_result["follow_up_references_anchor"]:
            issues.append("Follow-up message does not reference the selected anchor")
            suggestions.append(f"Include the anchor '{anchor_point}' in the follow-up message")

        if not validation_result["follow_up_builds_on_previous"]:
            issues.append("Follow-up message does not build on previous messages")
            if previous_messages:
                suggestions.append("Reference content from previous messages to maintain continuity")

        validation_result.update({
            "continuity_issues": issues,
            "continuity_suggestions": suggestions,
            "continuity_score": self._calculate_continuity_score(validation_result)
        })

        return validation_result

    def _calculate_continuity_score(self, validation_result: dict) -> float:
        """
        Calculate a continuity score based on validation results.

        Args:
            validation_result: The validation result dictionary

        Returns:
            Continuity score between 0 and 1
        """
        score = 0.0

        # Anchor reference is critical: contributes 0.6 to the score
        if validation_result["follow_up_references_anchor"]:
            score += 0.6

        # Building on previous messages: contributes 0.4 to the score
        if validation_result["follow_up_builds_on_previous"]:
            score += 0.4

        return round(score, 2)

    def validate_internal_scoring(self, message_content: str, selected_anchor: str,
                                 context_relevance: float, specificity: float,
                                 human_plausibility: float, question_quality: float) -> float:
        """
        Internal scoring for messages on context reuse, specificity, human plausibility, and question quality.

        Args:
            message_content: The content of the message
            selected_anchor: The selected anchor point
            context_relevance: Relevance of the message to the context (0-1)
            specificity: Specificity of the message (0-1)
            human_plausibility: How plausible the message sounds (0-1)
            question_quality: Quality of any questions in the message (0-1)

        Returns:
            Overall score for the message
        """
        # Calculate weighted average of all factors
        weights = {
            'relevance': 0.25,
            'specificity': 0.25,
            'plausibility': 0.25,
            'question_quality': 0.25
        }

        overall_score = (
            context_relevance * weights['relevance'] +
            specificity * weights['specificity'] +
            human_plausibility * weights['plausibility'] +
            question_quality * weights['question_quality']
        )

        return overall_score

    def calculate_internal_message_score(self, message_content: str, selected_anchor: str,
                                       context_reuse: float = 0.0, specificity: float = 0.0,
                                       human_plausibility: float = 0.0, question_quality: float = 0.0,
                                       anchor_reference: float = 0.0, character_compliance: float = 0.0,
                                       tone_alignment: float = 0.0) -> dict:
        """
        Calculate internal scoring for messages on context reuse, specificity, human plausibility,
        question quality, anchor reference, character compliance, and tone alignment.

        Args:
            message_content: The content of the message
            selected_anchor: The selected anchor point
            context_reuse: How well the message reuses context (0-1)
            specificity: Specificity of the message (0-1)
            human_plausibility: How plausible the message sounds (0-1)
            question_quality: Quality of any questions in the message (0-1)
            anchor_reference: How well the message references the anchor (0-1)
            character_compliance: Compliance with character limits (0-1)
            tone_alignment: Alignment with required tone (0-1)

        Returns:
            Dictionary with detailed scoring results
        """
        # Define weights for different scoring factors
        weights = {
            'context_reuse': 0.15,
            'specificity': 0.15,
            'human_plausibility': 0.15,
            'question_quality': 0.15,
            'anchor_reference': 0.15,
            'character_compliance': 0.10,
            'tone_alignment': 0.15
        }

        # Calculate weighted score
        weighted_score = (
            context_reuse * weights['context_reuse'] +
            specificity * weights['specificity'] +
            human_plausibility * weights['human_plausibility'] +
            question_quality * weights['question_quality'] +
            anchor_reference * weights['anchor_reference'] +
            character_compliance * weights['character_compliance'] +
            tone_alignment * weights['tone_alignment']
        )

        # Determine quality level based on score
        if weighted_score >= 0.8:
            quality_level = "Excellent"
        elif weighted_score >= 0.6:
            quality_level = "Good"
        elif weighted_score >= 0.4:
            quality_level = "Fair"
        else:
            quality_level = "Poor"

        return {
            "overall_score": round(weighted_score, 3),
            "quality_level": quality_level,
            "scores": {
                "context_reuse": context_reuse,
                "specificity": specificity,
                "human_plausibility": human_plausibility,
                "question_quality": question_quality,
                "anchor_reference": anchor_reference,
                "character_compliance": character_compliance,
                "tone_alignment": tone_alignment
            },
            "weights": weights,
            "weighted_score": round(weighted_score, 3)
        }

    def evaluate_message_comprehensively(self, message_content: str, selected_anchor: str,
                                       required_tone: str = None) -> dict:
        """
        Perform comprehensive evaluation of a message using internal scoring.

        Args:
            message_content: The content of the message to evaluate
            selected_anchor: The selected anchor point
            required_tone: The required tone for the message

        Returns:
            Dictionary with comprehensive evaluation results
        """
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()

        # Evaluate each scoring dimension
        context_reuse = self._evaluate_context_reuse(message_content, selected_anchor)
        specificity = self._evaluate_specificity(message_content)
        human_plausibility = self._evaluate_human_plausibility(message_content)
        question_quality = self._evaluate_question_quality(message_content)
        anchor_reference = self._evaluate_anchor_reference(message_content, selected_anchor)
        character_compliance = self._evaluate_character_compliance(message_content)
        tone_alignment = self._evaluate_tone_alignment(message_content, required_tone) if required_tone else 1.0

        # Calculate the internal score
        score_result = self.calculate_internal_message_score(
            message_content, selected_anchor,
            context_reuse, specificity, human_plausibility,
            question_quality, anchor_reference, character_compliance, tone_alignment
        )

        return {
            "internal_scoring": score_result,
            "detailed_evaluations": {
                "context_reuse": {
                    "score": context_reuse,
                    "details": self._explain_context_reuse_evaluation(message_content, selected_anchor)
                },
                "specificity": {
                    "score": specificity,
                    "details": self._explain_specificity_evaluation(message_content)
                },
                "human_plausibility": {
                    "score": human_plausibility,
                    "details": self._explain_human_plausibility_evaluation(message_content)
                },
                "question_quality": {
                    "score": question_quality,
                    "details": self._explain_question_quality_evaluation(message_content)
                },
                "anchor_reference": {
                    "score": anchor_reference,
                    "details": self._explain_anchor_reference_evaluation(message_content, selected_anchor)
                },
                "character_compliance": {
                    "score": character_compliance,
                    "details": self._explain_character_compliance_evaluation(message_content)
                },
                "tone_alignment": {
                    "score": tone_alignment,
                    "details": self._explain_tone_alignment_evaluation(message_content, required_tone) if required_tone else "Not checked"
                }
            }
        }

    def _evaluate_context_reuse(self, message_content: str, selected_anchor: str) -> float:
        """Evaluate how well the message reuses context."""
        # Check if the message references the selected anchor
        if not selected_anchor or not message_content:
            return 0.0

        anchor_lower = selected_anchor.lower()
        content_lower = message_content.lower()

        # Score based on how many times the anchor appears
        anchor_occurrences = content_lower.count(anchor_lower)
        if anchor_occurrences > 0:
            # Give higher score for more references but cap at 1.0
            return min(1.0, anchor_occurrences * 0.3)
        else:
            return 0.0

    def _evaluate_specificity(self, message_content: str) -> float:
        """Evaluate the specificity of the message."""
        # Messages with specific details score higher
        # This is a simplified evaluation - in practice, this would be more sophisticated
        if len(message_content) < 20:
            # Too short to be specific
            return 0.2

        # Look for specific indicators
        specific_indicators = [
            "specific", "particular", "detailed", "concrete", "actual",
            "exact", "precise", "well-defined", "tailored", "customized"
        ]

        content_lower = message_content.lower()
        specific_count = sum(1 for indicator in specific_indicators if indicator in content_lower)

        # Normalize to 0-1 scale
        return min(1.0, specific_count * 0.3)

    def _evaluate_human_plausibility(self, message_content: str) -> float:
        """Evaluate how plausible the message sounds."""
        # Check for common implausible patterns
        implausible_patterns = [
            "click here", "buy now", "limited time", "act fast",
            "amazing offer", "guaranteed results", "risk free"
        ]

        content_lower = message_content.lower()
        implausible_count = sum(1 for pattern in implausible_patterns if pattern in content_lower)

        # Lower score for more implausible patterns
        plausibility_score = max(0.0, 1.0 - (implausible_count * 0.2))

        return plausibility_score

    def _evaluate_question_quality(self, message_content: str) -> float:
        """Evaluate the quality of questions in the message."""
        # Look for question marks and evaluate question quality
        question_count = message_content.count('?')

        if question_count == 0:
            return 0.0

        # Evaluate based on question count and content
        # More thoughtful questions score higher
        content_lower = message_content.lower()

        thoughtful_indicators = [
            "how do", "what do you", "what's your", "tell me about",
            "can you explain", "what challenges", "what opportunities"
        ]

        thoughtful_count = sum(1 for indicator in thoughtful_indicators if indicator in content_lower)

        # Normalize to 0-1 scale
        return min(1.0, (thoughtful_count * 0.5) + (question_count * 0.2))

    def _evaluate_anchor_reference(self, message_content: str, selected_anchor: str) -> float:
        """Evaluate how well the message references the anchor."""
        if not selected_anchor or not message_content:
            return 0.0

        anchor_lower = selected_anchor.lower()
        content_lower = message_content.lower()

        # Check for direct reference
        if anchor_lower in content_lower:
            return 1.0
        else:
            # Check for partial matches or related terms
            anchor_words = anchor_lower.split()
            matches = sum(1 for word in anchor_words if word in content_lower)

            if matches > 0:
                return min(1.0, matches / len(anchor_words) * 0.7)
            else:
                return 0.0

    def _evaluate_character_compliance(self, message_content: str) -> float:
        """Evaluate compliance with character limits."""
        max_chars = 240
        length = len(message_content)

        if length <= max_chars:
            return 1.0
        else:
            # Decrease score proportionally to how much over the limit
            excess_ratio = (length - max_chars) / max_chars
            return max(0.0, 1.0 - excess_ratio)

    def _evaluate_tone_alignment(self, message_content: str, required_tone: str) -> float:
        """Evaluate alignment with the required tone."""
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()

        # Use the existing tone validation
        is_aligned = moderator.validate_tone(message_content, required_tone)

        return 1.0 if is_aligned else 0.3  # Lower score if not aligned

    def _explain_context_reuse_evaluation(self, message_content: str, selected_anchor: str) -> str:
        """Provide explanation for context reuse evaluation."""
        if not selected_anchor:
            return "No anchor provided for context reuse evaluation"

        anchor_lower = selected_anchor.lower()
        content_lower = message_content.lower()
        occurrences = content_lower.count(anchor_lower)

        if occurrences > 0:
            return f"Message references the anchor '{selected_anchor}' {occurrences} time(s)"
        else:
            return f"Message does not reference the anchor '{selected_anchor}'"

    def _explain_specificity_evaluation(self, message_content: str) -> str:
        """Provide explanation for specificity evaluation."""
        return "Specificity evaluated based on presence of detailed, tailored language"

    def _explain_human_plausibility_evaluation(self, message_content: str) -> str:
        """Provide explanation for human plausibility evaluation."""
        return "Plausibility evaluated based on absence of marketing clichés and spam-like phrases"

    def _explain_question_quality_evaluation(self, message_content: str) -> str:
        """Provide explanation for question quality evaluation."""
        return "Question quality evaluated based on presence of thoughtful, open-ended questions"

    def _explain_anchor_reference_evaluation(self, message_content: str, selected_anchor: str) -> str:
        """Provide explanation for anchor reference evaluation."""
        if not selected_anchor:
            return "No anchor provided for reference evaluation"

        anchor_lower = selected_anchor.lower()
        content_lower = message_content.lower()

        if anchor_lower in content_lower:
            return f"Direct reference to anchor '{selected_anchor}' found"
        else:
            return f"No direct reference to anchor '{selected_anchor}' found"

    def _explain_character_compliance_evaluation(self, message_content: str) -> str:
        """Provide explanation for character compliance evaluation."""
        length = len(message_content)
        max_chars = 240

        if length <= max_chars:
            return f"Message length ({length}) is within limit ({max_chars})"
        else:
            return f"Message length ({length}) exceeds limit ({max_chars}) by {length - max_chars} characters"

    def _explain_tone_alignment_evaluation(self, message_content: str, required_tone: str) -> str:
        """Provide explanation for tone alignment evaluation."""
        return f"Tone alignment checked against required tone: {required_tone}"

    def apply_low_context_safeguards(self, profile: LinkedInProfile) -> dict:
        """
        Apply safeguards for low-context situations to prevent inappropriate messages.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Dictionary with safeguard recommendations
        """
        context_depth_score = profile.context_depth_score
        safeguards_needed = context_depth_score <= 1  # Apply safeguards for low context

        recommendations = {
            "avoid_assumptions": safeguards_needed,
            "use_exploratory_tone": safeguards_needed,
            "focus_on_questions": safeguards_needed,
            "avoid_compliments": safeguards_needed,
            "minimal_specificity": safeguards_needed,
            "suggested_approach": "exploratory" if safeguards_needed else "standard"
        }

        if safeguards_needed:
            # Additional recommendations for low-context situations
            recommendations.update({
                "recommended_phrases": [
                    "I noticed your profile and thought you might be interested in connecting.",
                    "I came across your profile and found your background interesting.",
                    "Hope you're doing well! I saw your profile and had a question:"
                ],
                "avoid_phrases": [
                    "I see you're working on amazing things at",
                    "Your work at [company] looks impressive",
                    "I noticed your expertise in [specific area]"
                ],
                "recommended_strategy": "Ask diagnostic questions to learn more about the prospect"
            })

        return {
            "safeguards_applied": safeguards_needed,
            "context_depth_score": context_depth_score,
            "recommendations": recommendations
        }

    def validate_message_for_low_context(self, message_content: str, context_depth_score: int) -> dict:
        """
        Validate a message specifically for low-context situations.

        Args:
            message_content: The content of the message to validate
            context_depth_score: The context depth score of the profile

        Returns:
            Dictionary with validation results
        """
        is_low_context = context_depth_score <= 1
        results = {
            "is_low_context": is_low_context,
            "message_appropriate": True,
            "issues_found": [],
            "suggestions": []
        }

        if is_low_context:
            # Check if the message makes inappropriate assumptions
            assumption_keywords = [
                "I see you're", "Your work at", "I noticed your expertise",
                "Your success at", "Your achievements in", "I see you've been"
            ]

            content_lower = message_content.lower()
            for keyword in assumption_keywords:
                if keyword.lower() in content_lower:
                    results["message_appropriate"] = False
                    results["issues_found"].append(f"Message contains assumption phrase: '{keyword}'")
                    results["suggestions"].append(f"Avoid assumption phrases like '{keyword}', use more exploratory language")

            # Check if the message is too specific
            too_specific_indicators = [
                "your specific project", "your team's initiative", "your department's strategy",
                "your role in [specific]", "your work on [specific]"
            ]

            for indicator in too_specific_indicators:
                if indicator.lower() in content_lower:
                    results["message_appropriate"] = False
                    results["issues_found"].append(f"Message is too specific for low context: '{indicator}'")
                    results["suggestions"].append(f"Avoid specific references, use more general language")

        return results

    def should_regenerate(self, internal_score: float, threshold: float = 0.7) -> bool:
        """
        Determine if a message should be regenerated based on internal scoring.

        Args:
            internal_score: The internal score of the message
            threshold: The threshold below which regeneration is needed (default 0.7)

        Returns:
            Boolean indicating if regeneration is needed
        """
        return internal_score < threshold

    def is_exploratory_mode_needed(self, context_depth_score: int, threshold: int = 1) -> bool:
        """
        Determine if exploratory mode is needed based on context depth score.

        Args:
            context_depth_score: The calculated context depth score
            threshold: The threshold below which exploratory mode is triggered (default 1)

        Returns:
            Boolean indicating if exploratory mode is needed
        """
        return context_depth_score <= threshold

    def apply_exploratory_mode_logic(self, profile: LinkedInProfile) -> dict:
        """
        Apply exploratory mode logic for low-context situations.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Dictionary with exploratory mode recommendations
        """
        context_depth_score = profile.context_depth_score
        needs_exploratory_mode = self.is_exploratory_mode_needed(context_depth_score)

        recommendations = []

        if needs_exploratory_mode:
            # Generate diagnostic questions for low-context situations
            recommendations.extend([
                "Avoid making assumptions about the prospect's situation",
                "Ask open-ended questions to learn more about their needs",
                "Focus on building rapport rather than pitching solutions",
                "Keep messages brief and non-committal"
            ])

            # Suggest specific question types based on available context
            if profile.role:
                recommendations.append(f"As they have the role '{profile.role}', you could ask about challenges in that position")
            if profile.company:
                recommendations.append(f"As they work at '{profile.company}', you could inquire about company initiatives")
            if profile.industry:
                recommendations.append(f"In the '{profile.industry}' industry, you could explore market trends")

        return {
            "needs_exploratory_mode": needs_exploratory_mode,
            "context_depth_score": context_depth_score,
            "recommendations": recommendations,
            "mode": "Exploratory" if needs_exploratory_mode else "Standard"
        }