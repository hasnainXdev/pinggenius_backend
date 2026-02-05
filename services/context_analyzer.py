from typing import List, Optional, Tuple
from ..models.linkedin_profile import LinkedInProfile
from ..models.analysis_result import AnalysisResult
from ..models.outreach_message import OutreachMessage
from ..models.context_aware_outreach_sequence import ContextAwareOutreachSequence
from .validation_engine import ValidationEngine, GenerationMode
import random


class ContextAnalyzer:
    """
    Service for analyzing LinkedIn profiles and selecting anchors for outreach.
    """
    
    def __init__(self):
        self.validation_engine = ValidationEngine()

    def analyze_profile(self, profile: LinkedInProfile) -> AnalysisResult:
        """
        Analyze a LinkedIn profile and select a single anchor point for outreach.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            AnalysisResult with selected anchor and other details
        """
        # Calculate context depth score
        context_depth_score = self.validation_engine.calculate_context_depth_score(profile)

        # Select anchor based on priority hierarchy: pain_points > recent_activity > role-based
        selected_anchor, anchor_type = self._select_anchor(profile)

        # Determine generation mode based on context depth score
        generation_mode = self.validation_engine.get_generation_mode_from_score(context_depth_score)

        # Prepare analysis details
        analysis_details = {
            "pain_points_found": bool(profile.pain_points),
            "recent_activity_found": bool(profile.recent_activity),
            "role_based_anchor": anchor_type == "role_based",
            "context_richness": self._get_context_richness_label(context_depth_score)
        }

        result = AnalysisResult(
            profile_id=profile.id or "",
            selected_anchor=selected_anchor,
            anchor_type=anchor_type,
            context_depth_score=context_depth_score,
            generation_mode=generation_mode,
            analysis_details=analysis_details
        )

        return result

    def apply_anchor_priority_logic(self, profile: LinkedInProfile) -> Tuple[str, str]:
        """
        Apply the anchor priority logic to select the best anchor point.

        Priority hierarchy:
        1. Pain points (if available)
        2. Recent activity (if available)
        3. Role-based (if available)

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Tuple of (selected_anchor, anchor_type)
        """
        # This method encapsulates the priority logic
        return self._select_anchor(profile)

    def evaluate_anchor_quality(self, profile: LinkedInProfile, anchor: str, anchor_type: str) -> float:
        """
        Evaluate the quality of the selected anchor based on profile context.

        Args:
            profile: LinkedInProfile that was analyzed
            anchor: The selected anchor string
            anchor_type: The type of anchor selected

        Returns:
            Quality score between 0 and 1
        """
        score = 0.0

        # Higher priority anchors get higher base scores
        if anchor_type == "pain_point":
            score += 0.9
        elif anchor_type == "recent_activity":
            score += 0.7
        elif anchor_type == "role_based":
            score += 0.5
        else:
            score += 0.3  # fallback anchors get lower scores

        # Adjust score based on context richness
        context_score = profile.context_depth_score / 4.0  # Normalize to 0-1 range
        score = (score + context_score) / 2.0  # Average the anchor type score with context score

        return min(score, 1.0)  # Ensure score doesn't exceed 1.0

    def _select_anchor(self, profile: LinkedInProfile) -> Tuple[str, str]:
        """
        Select an anchor point based on priority hierarchy.

        Priority:
        1. Pain points (if available)
        2. Recent activity (if available)
        3. Role-based (if available)

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Tuple of (selected_anchor, anchor_type)
        """
        # Priority 1: Pain points
        if profile.pain_points and len(profile.pain_points) > 0:
            # Select the first pain point as the anchor
            anchor = profile.pain_points[0]
            return anchor, "pain_point"

        # Priority 2: Recent activity
        if profile.recent_activity and len(profile.recent_activity) > 0:
            # Select the first recent activity as the anchor
            anchor = profile.recent_activity[0]
            return anchor, "recent_activity"

        # Priority 3: Role-based anchor
        if profile.role or profile.title:
            # Create a role-based anchor
            role_part = profile.role or profile.title
            company_part = profile.company or profile.industry or "their company"
            anchor = f"{role_part} at {company_part}"
            return anchor, "role_based"

        # If no context is available, return a generic anchor
        anchor = f"the opportunity to connect with {profile.profile_url.split('/')[-1] if profile.profile_url else 'unknown'}"
        return anchor, "role_based"

    def select_anchor_with_fallback(self, profile: LinkedInProfile) -> Tuple[str, str]:
        """
        Select an anchor point with additional fallback strategies.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Tuple of (selected_anchor, anchor_type)
        """
        # Use the standard selection method first
        anchor, anchor_type = self._select_anchor(profile)

        # If we still don't have a meaningful anchor, try additional strategies
        if not anchor or anchor.startswith("the opportunity to connect"):
            # Try to create an anchor based on any available information
            if profile.role:
                anchor = f"your role as {profile.role}"
            elif profile.title:
                anchor = f"your position as {profile.title}"
            elif profile.company:
                anchor = f"your company {profile.company}"
            elif profile.industry:
                anchor = f"your industry {profile.industry}"
            else:
                anchor = "potential networking opportunity"

            anchor_type = "fallback"

        return anchor, anchor_type

    def _get_context_richness_label(self, score: int) -> str:
        """
        Get a label for the context richness based on the score.
        
        Args:
            score: Context depth score (0-4)
            
        Returns:
            String label for the context richness
        """
        if score >= 3:
            return "Rich"
        elif score == 2:
            return "Moderate"
        elif score == 1:
            return "Limited"
        else:
            return "Insufficient"

    def generate_diagnostic_question(self, profile: LinkedInProfile) -> str:
        """
        Generate a diagnostic question for low-context situations.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Diagnostic question string
        """
        # Create a pool of questions based on available profile information
        questions = []

        # Role-based questions
        if profile.role:
            questions.extend([
                f"What's the biggest challenge you're facing in your role as {profile.role}?",
                f"How do you find working in {profile.role} at {profile.company or profile.industry or 'your organization'}?",
                f"What aspect of being a {profile.role} do you find most rewarding?"
            ])

        # Company-based questions
        if profile.company:
            questions.extend([
                f"What's been the most interesting development at {profile.company} recently?",
                f"How has {profile.company} been adapting to changes in the {profile.industry or 'market'}?",
                f"What's your favorite thing about working at {profile.company}?"
            ])

        # Industry-based questions
        if profile.industry:
            questions.extend([
                f"How do you see the {profile.industry} industry evolving in the next year?",
                f"What trends are you seeing in {profile.industry} that excite you most?",
                f"What challenges do you think organizations in {profile.industry} face today?"
            ])

        # Generic questions for when little context is available
        if not questions:
            questions = [
                "What's the most interesting project you're working on right now?",
                "What trends are you seeing in your field that excite you most?",
                "What's been the highlight of your week?",
                "What's a challenge you're currently facing that I might be able to help with?"
            ]

        # Choose a random question from the list
        return random.choice(questions)

    def generate_diagnostic_questions_set(self, profile: LinkedInProfile, count: int = 3) -> list:
        """
        Generate a set of diagnostic questions for low-context situations.

        Args:
            profile: LinkedInProfile to analyze
            count: Number of questions to generate (default 3)

        Returns:
            List of diagnostic question strings
        """
        questions_pool = []

        # Role-based questions
        if profile.role:
            questions_pool.extend([
                f"What's the biggest challenge you're facing in your role as {profile.role}?",
                f"How do you find working in {profile.role} at {profile.company or profile.industry or 'your organization'}?",
                f"What aspect of being a {profile.role} do you find most rewarding?",
                f"What skills do you think are most important for success as a {profile.role}?"
            ])

        # Company-based questions
        if profile.company:
            questions_pool.extend([
                f"What's been the most interesting development at {profile.company} recently?",
                f"How has {profile.company} been adapting to changes in the {profile.industry or 'market'}?",
                f"What's your favorite thing about working at {profile.company}?",
                f"What opportunities do you see for {profile.company} in the coming year?"
            ])

        # Industry-based questions
        if profile.industry:
            questions_pool.extend([
                f"How do you see the {profile.industry} industry evolving in the next year?",
                f"What trends are you seeing in {profile.industry} that excite you most?",
                f"What challenges do you think organizations in {profile.industry} face today?",
                f"What innovations in {profile.industry} are you most excited about?"
            ])

        # Experience-based questions
        if profile.role and profile.company:
            questions_pool.extend([
                f"How has your experience been transitioning to {profile.company} as a {profile.role}?",
                f"What unique challenges does {profile.company} present in your role as {profile.role}?"
            ])

        # Generic questions for when little context is available
        if not questions_pool:
            questions_pool = [
                "What's the most interesting project you're working on right now?",
                "What trends are you seeing in your field that excite you most?",
                "What's been the highlight of your week?",
                "What's a challenge you're currently facing that I might be able to help with?",
                "What professional goals are you focusing on this year?",
                "What book or article has influenced your thinking recently?"
            ]

        # Shuffle the questions and return the requested count
        random.shuffle(questions_pool)
        return questions_pool[:count]

    def generate_exploratory_message(self, profile: LinkedInProfile) -> str:
        """
        Generate an exploratory message that asks diagnostic questions.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Exploratory message string with diagnostic questions
        """
        # Generate a diagnostic question
        question = self.generate_diagnostic_question(profile)

        # Create an exploratory message that includes the question
        message_templates = [
            f"Hi! I noticed your profile and thought you might be interested in connecting. {question}",
            f"I came across your profile and found your background interesting. {question}",
            f"Hope you're doing well! I saw your profile and had a question: {question}",
            f"Hi there! I found your profile through mutual connections. {question}"
        ]

        return random.choice(message_templates)

    def apply_quality_control_to_message(self, message_content: str, anchor_point: str = None,
                                      required_tone: str = None, max_chars: int = 240) -> dict:
        """
        Apply quality control to a generated message.

        Args:
            message_content: The content of the message to check
            anchor_point: Optional anchor point to check for references
            required_tone: Optional required tone to validate
            max_chars: Maximum number of characters allowed (default 240)

        Returns:
            Dictionary with quality control results
        """
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()

        # Check character limit
        char_limit_result = moderator.enforce_character_limit_detailed(message_content, max_chars)

        # Check for prohibited phrases
        phrase_result = moderator.filter_prohibited_phrases_detailed(message_content)

        # Validate tone if required
        tone_result = None
        if required_tone:
            tone_result = moderator.analyze_tone(message_content)
            tone_compliant = moderator.validate_tone(message_content, required_tone)
        else:
            tone_compliant = True
            tone_result = {"dominant_tone": "not_checked", "tone_scores": {}, "confidence": 0}

        # Check anchor reference if provided
        anchor_references = 0
        if anchor_point:
            # Count occurrences of anchor in message
            anchor_lower = anchor_point.lower()
            content_lower = message_content.lower()
            anchor_references = content_lower.count(anchor_lower)

        # Compile results
        overall_quality = all([
            char_limit_result['is_within_limit'],
            not phrase_result['contains_prohibited'],
            tone_compliant
        ])

        return {
            "overall_quality_pass": overall_quality,
            "character_limit_check": char_limit_result,
            "prohibited_phrases_check": phrase_result,
            "tone_check": {
                "required_tone": required_tone,
                "tone_compliant": tone_compliant,
                "analysis": tone_result
            },
            "anchor_reference_check": {
                "anchor_provided": bool(anchor_point),
                "references_count": anchor_references,
                "references_anchor": anchor_references > 0
            },
            "quality_score": self._calculate_quality_score(char_limit_result, phrase_result, tone_compliant, anchor_references > 0)
        }

    def _calculate_quality_score(self, char_limit_result: dict, phrase_result: dict,
                                tone_compliant: bool, references_anchor: bool) -> float:
        """
        Calculate an overall quality score based on various checks.

        Args:
            char_limit_result: Result from character limit check
            phrase_result: Result from prohibited phrases check
            tone_compliant: Whether the message is tone compliant
            references_anchor: Whether the message references the anchor

        Returns:
            Quality score between 0 and 1
        """
        score = 0.0

        # Character limit compliance: contributes up to 0.25 to the score
        if char_limit_result['is_within_limit']:
            score += 0.25
        else:
            # Partial credit based on compliance percentage
            score += 0.25 * (char_limit_result['compliance_percentage'] / 100)

        # Prohibited phrases: contributes up to 0.25 to the score
        if not phrase_result['contains_prohibited']:
            score += 0.25

        # Tone compliance: contributes up to 0.25 to the score
        if tone_compliant:
            score += 0.25

        # Anchor reference: contributes up to 0.25 to the score
        if references_anchor:
            score += 0.25

        return round(score, 2)

    def regenerate_message_with_stricter_phrasing(self, original_message: str, anchor_point: str,
                                               required_tone: str = None,
                                               score_threshold: float = 0.7) -> tuple:
        """
        Regenerate a message with stricter phrasing if the internal score falls below threshold.

        Args:
            original_message: The original message that needs regeneration
            anchor_point: The anchor point to maintain in the regenerated message
            required_tone: The required tone for the message
            score_threshold: The threshold below which regeneration is needed (default 0.7)

        Returns:
            Tuple of (regenerated_message, score_improved, original_score, new_score)
        """
        from ..services.validation_engine import ValidationEngine
        validation_engine = ValidationEngine()

        # Evaluate the original message
        original_evaluation = validation_engine.evaluate_message_comprehensively(
            original_message, anchor_point, required_tone
        )
        original_score = original_evaluation["internal_scoring"]["overall_score"]

        # Check if regeneration is needed
        needs_regeneration = original_score < score_threshold

        if not needs_regeneration:
            return original_message, False, original_score, original_score

        # Generate a stricter version of the message
        regenerated_message = self._generate_stricter_message(original_message, anchor_point, required_tone)

        # Evaluate the regenerated message
        regenerated_evaluation = validation_engine.evaluate_message_comprehensively(
            regenerated_message, anchor_point, required_tone
        )
        new_score = regenerated_evaluation["internal_scoring"]["overall_score"]

        # Return the better of the two messages
        if new_score > original_score:
            return regenerated_message, True, original_score, new_score
        else:
            # If the regenerated message is not better, return the original
            return original_message, False, original_score, new_score

    def _generate_stricter_message(self, original_message: str, anchor_point: str,
                                 required_tone: str = None) -> str:
        """
        Generate a stricter version of the message that addresses identified issues.

        Args:
            original_message: The original message to improve
            anchor_point: The anchor point to maintain
            required_tone: The required tone for the message

        Returns:
            Improved message with stricter phrasing
        """
        # This is a simplified implementation - in a real system, this would involve
        # calling an AI model or more sophisticated text generation logic

        # Identify potential issues and fix them
        stricter_message = original_message

        # Remove overly promotional language
        promotional_phrases = [
            "amazing opportunity", "don't miss out", "limited time",
            "act now", "exclusive offer", "special deal"
        ]

        for phrase in promotional_phrases:
            stricter_message = stricter_message.replace(phrase, "")

        # Clean up extra spaces
        stricter_message = ' '.join(stricter_message.split())

        # Ensure the anchor point is included
        if anchor_point and anchor_point.lower() not in stricter_message.lower():
            # Add the anchor point to the message
            stricter_message = f"Regarding {anchor_point}: {stricter_message}"

        # Apply character limit if needed
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()
        if len(stricter_message) > 240:
            stricter_message = moderator.truncate_to_limit(stricter_message)

        return stricter_message

    def apply_regeneration_check(self, message_content: str, anchor_point: str,
                               required_tone: str = None, threshold: float = 0.7) -> dict:
        """
        Apply regeneration check to determine if a message needs to be regenerated.

        Args:
            message_content: The content of the message to check
            anchor_point: The anchor point for the message
            required_tone: The required tone for the message
            threshold: The score threshold for regeneration (default 0.7)

        Returns:
            Dictionary with regeneration decision and details
        """
        from ..services.validation_engine import ValidationEngine
        validation_engine = ValidationEngine()

        # Evaluate the message
        evaluation = validation_engine.evaluate_message_comprehensively(
            message_content, anchor_point, required_tone
        )
        current_score = evaluation["internal_scoring"]["overall_score"]

        # Determine if regeneration is needed
        needs_regeneration = current_score < threshold

        result = {
            "current_score": current_score,
            "threshold": threshold,
            "needs_regeneration": needs_regeneration,
            "original_message": message_content,
            "evaluation": evaluation
        }

        if needs_regeneration:
            # Regenerate the message
            regenerated_message, improved, orig_score, new_score = self.regenerate_message_with_stricter_phrasing(
                message_content, anchor_point, required_tone, threshold
            )

            result.update({
                "regenerated_message": regenerated_message,
                "score_improved": improved,
                "original_score": orig_score,
                "new_score": new_score
            })
        else:
            result["regenerated_message"] = message_content

        return result

    def handle_multiple_roles_companies(self, profile: LinkedInProfile) -> tuple:
        """
        Handle profiles with multiple roles or companies by selecting the most relevant/recent.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Tuple of (selected_role_or_title, selected_company_or_industry)
        """
        # In this implementation, we'll just return the first available values
        # In a real implementation, this would involve more sophisticated logic to determine
        # the most relevant/recent role and company
        selected_role = profile.role or profile.title
        selected_company = profile.company or profile.industry

        return selected_role, selected_company

    def handle_multiple_roles_companies_advanced(self, profile: LinkedInProfile,
                                              custom_logic_func=None) -> tuple:
        """
        Advanced handling of profiles with multiple roles or companies.

        Args:
            profile: LinkedInProfile to analyze
            custom_logic_func: Optional custom function to determine the most relevant role/company

        Returns:
            Tuple of (selected_role_or_title, selected_company_or_industry, metadata)
        """
        # If a custom logic function is provided, use it
        if custom_logic_func:
            return custom_logic_func(profile)

        # Default logic: prioritize role over title, company over industry
        selected_role = profile.role or profile.title
        selected_company = profile.company or profile.industry

        # Create metadata about the selection
        metadata = {
            "role_selected": "role" if profile.role else "title" if profile.title else None,
            "company_selected": "company" if profile.company else "industry" if profile.industry else None,
            "multiple_roles_available": bool(profile.role and profile.title),
            "multiple_companies_available": bool(profile.company and profile.industry)
        }

        return selected_role, selected_company, metadata

    def select_most_relevant_role_company(self, profile: LinkedInProfile) -> dict:
        """
        Select the most relevant role and company based on available information.

        Args:
            profile: LinkedInProfile to analyze

        Returns:
            Dictionary with selected role/company and reasoning
        """
        result = {
            "selected_role": None,
            "selected_company": None,
            "reasoning": []
        }

        # Select role over title if both are available
        if profile.role and profile.title:
            result["selected_role"] = profile.role
            result["reasoning"].append("Selected role over title as role takes precedence")
        elif profile.role:
            result["selected_role"] = profile.role
            result["reasoning"].append("Selected role as it's the only role-related field available")
        elif profile.title:
            result["selected_role"] = profile.title
            result["reasoning"].append("Selected title as role is not available")
        else:
            result["reasoning"].append("No role or title available")

        # Select company over industry if both are available
        if profile.company and profile.industry:
            result["selected_company"] = profile.company
            result["reasoning"].append("Selected company over industry as company takes precedence")
        elif profile.company:
            result["selected_company"] = profile.company
            result["reasoning"].append("Selected company as it's the only company-related field available")
        elif profile.industry:
            result["selected_company"] = profile.industry
            result["reasoning"].append("Selected industry as company is not available")
        else:
            result["reasoning"].append("No company or industry available")

        return result

    def inject_sequence_memory(self, sequence: 'ContextAwareOutreachSequence',
                              selected_anchor: str,
                              previous_outputs: List[str]) -> 'ContextAwareOutreachSequence':
        """
        Inject sequence memory (selected anchor, previous outputs) into follow-up generation.

        Args:
            sequence: The current outreach sequence
            selected_anchor: The selected anchor point for the sequence
            previous_outputs: List of previous message outputs in the sequence

        Returns:
            Updated ContextAwareOutreachSequence with injected memory
        """
        # Add the selected anchor and previous outputs to the sequence context
        sequence.sequence_context = {
            "selected_anchor": selected_anchor,
            "previous_outputs": previous_outputs,
            "message_count": len(previous_outputs)
        }

        return sequence

    def inject_sequence_memory_advanced(self, sequence: 'ContextAwareOutreachSequence',
                                      selected_anchor: str,
                                      previous_outputs: List[str],
                                      tone_preference: str = None,
                                      engagement_history: List[dict] = None) -> 'ContextAwareOutreachSequence':
        """
        Inject advanced sequence memory with additional context for follow-up generation.

        Args:
            sequence: The current outreach sequence
            selected_anchor: The selected anchor point for the sequence
            previous_outputs: List of previous message outputs in the sequence
            tone_preference: The preferred tone for the sequence
            engagement_history: Historical engagement data (optional)

        Returns:
            Updated ContextAwareOutreachSequence with injected advanced memory
        """
        # Create a comprehensive context object
        sequence_context = {
            "selected_anchor": selected_anchor,
            "previous_outputs": previous_outputs,
            "message_count": len(previous_outputs),
            "tone_preference": tone_preference,
            "engagement_history": engagement_history or [],
            "sequence_position": len(previous_outputs),  # Current position in sequence
            "anchor_consistency_checks": self._perform_anchor_consistency_checks(selected_anchor, previous_outputs)
        }

        # Add the context to the sequence
        sequence.sequence_context = sequence_context

        return sequence

    def _perform_anchor_consistency_checks(self, anchor_point: str, previous_outputs: List[str]) -> List[dict]:
        """
        Perform checks to ensure anchor consistency across previous outputs.

        Args:
            anchor_point: The selected anchor point
            previous_outputs: List of previous message outputs

        Returns:
            List of consistency check results for each message
        """
        from ..services.validation_engine import ValidationEngine
        validation_engine = ValidationEngine()

        consistency_results = []

        for idx, message in enumerate(previous_outputs):
            check_result = validation_engine.validate_anchor_reference_in_message(anchor_point, message)
            consistency_results.append({
                "message_index": idx,
                "message_preview": message[:50] + "..." if len(message) > 50 else message,
                "references_anchor": check_result["references_anchor"],
                "match_percentage": check_result["match_percentage"],
                "details": check_result["details"]
            })

        return consistency_results

    def generate_follow_up(self, sequence: ContextAwareOutreachSequence,
                          previous_message: OutreachMessage) -> OutreachMessage:
        """
        Generate a follow-up message that references the anchor and builds on previous messages.

        Args:
            sequence: The current outreach sequence
            previous_message: The previous message in the sequence

        Returns:
            New OutreachMessage for the follow-up
        """
        # Get the selected anchor from the sequence context
        anchor = sequence.sequence_context.get("selected_anchor", "") if sequence.sequence_context else ""

        # Get previous outputs to build on the conversation
        previous_outputs = sequence.sequence_context.get("previous_outputs", []) if sequence.sequence_context else []

        # Create a follow-up message that references the anchor and builds on previous messages
        if previous_outputs:
            # Use the last message as context for the follow-up
            last_message = previous_outputs[-1]
            follow_up_content = f"Building on our previous conversation, I wanted to add: {anchor[:50]}..."
        else:
            follow_up_content = f"Following up on our previous discussion about {anchor[:50]}..."

        # Ensure the message stays within character limits
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()
        if len(follow_up_content) > 240:
            follow_up_content = moderator.truncate_to_limit(follow_up_content)

        # Create the new message
        new_message_order = previous_message.message_order + 1
        new_message = OutreachMessage(
            sequence_id=sequence.id or "",
            message_order=new_message_order,
            content=follow_up_content
        )

        return new_message

    def generate_follow_up_advanced(self, sequence: ContextAwareOutreachSequence,
                                   previous_message: OutreachMessage,
                                   tone_override: str = None) -> OutreachMessage:
        """
        Generate an advanced follow-up message with more contextual awareness.

        Args:
            sequence: The current outreach sequence
            previous_message: The previous message in the sequence
            tone_override: Optional tone to override the sequence's default

        Returns:
            New OutreachMessage for the follow-up with enhanced context
        """
        # Get the selected anchor from the sequence context
        anchor = sequence.sequence_context.get("selected_anchor", "") if sequence.sequence_context else ""

        # Get previous outputs to build on the conversation
        previous_outputs = sequence.sequence_context.get("previous_outputs", []) if sequence.sequence_context else []

        # Get tone preference
        tone_preference = tone_override or sequence.sequence_context.get("tone_preference") if sequence.sequence_context else "Friendly"

        # Create follow-up templates based on tone
        follow_up_templates = {
            "Authority": f"Regarding {anchor[:40]}, I wanted to share some insights from our research...",
            "Friendly": f"Thanks for the previous conversation about {anchor[:40]}. I had another thought...",
            "Casual": f"Hey! Coming back to what we discussed about {anchor[:40]}, I remembered..."
        }

        # Select template based on tone
        follow_up_content = follow_up_templates.get(tone_preference, follow_up_templates["Friendly"])

        # Ensure the message stays within character limits
        from ..utils.content_moderation import ContentModeration
        moderator = ContentModeration()
        if len(follow_up_content) > 240:
            follow_up_content = moderator.truncate_to_limit(follow_up_content)

        # Create the new message
        new_message_order = previous_message.message_order + 1
        new_message = OutreachMessage(
            sequence_id=sequence.id or "",
            message_order=new_message_order,
            content=follow_up_content
        )

        return new_message