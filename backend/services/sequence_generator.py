from models.sequence import OutreachSequence, Message, SequenceContext
from models.profile import LinkedInProfile
from models.validation import ToneValidatorConfiguration
from typing import Optional, List, Dict, Any
from agents import (
    Agent,
    Runner,
    RunConfig,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from config.settings import settings
from utils.retry import retry_with_backoff
from database.mongo import get_db
from enum import Enum
import logging
import json
import os
import time

# Import the tone validator service
from services.tone_validator import ToneValidatorService
from utils.timeout_manager import llm_timeout_manager

set_tracing_disabled(True)

# Initialize clients only if API keys are available
gemini_client = None
model = None
config = None

if settings.gemini_api_key:
    gemini_client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="models/gemini-2.5-flash",
        openai_client=gemini_client,
    )

    config = RunConfig(
        model=model,
        model_provider=gemini_client,
    )
else:
    logging.warning("Gemini API key not configured. Using fallback responses.")


# Simple string constants for tone values
TONE_FRIENDLY = "Friendly"
TONE_DIRECT = "Direct"
TONE_AUTHORITY = "Authority"
TONE_CASUAL = "Casual"

VALID_TONES = [TONE_FRIENDLY, TONE_DIRECT, TONE_AUTHORITY, TONE_CASUAL]


class SequenceGeneratorService:
    """
    Service for generating LinkedIn outreach sequences using OpenAI Agents
    """

    def __init__(self):
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        self.tone_instructions = {
            TONE_FRIENDLY: "Write in a warm, conversational tone that feels approachable and friendly.",
            TONE_DIRECT: "Write in a clear, straightforward tone that gets to the point efficiently.",
            TONE_AUTHORITY: "Write in a confident, expert-led tone that demonstrates knowledge and credibility.",
            TONE_CASUAL: "Write in a relaxed, natural tone that feels informal and easy-going.",
        }
        # In-memory storage for temporary sequence contexts during generation
        self.temporary_contexts = {}
        # Initialize the tone validator service
        self.tone_validator = ToneValidatorService()

        # Cache for frequently used agent configurations to reduce initialization overhead
        self.agent_cache = {}

    def _store_temporary_context(self, sequence_id: str, context: SequenceContext):
        """
        Store sequence context temporarily during generation
        """
        # Clean up old contexts periodically to prevent memory buildup
        self._cleanup_old_contexts()
        self.temporary_contexts[sequence_id] = context

    def _retrieve_temporary_context(self, sequence_id: str) -> Optional[SequenceContext]:
        """
        Retrieve temporary sequence context
        """
        return self.temporary_contexts.get(sequence_id)

    def _remove_temporary_context(self, sequence_id: str):
        """
        Remove temporary sequence context after persistence decision
        """
        if sequence_id in self.temporary_contexts:
            del self.temporary_contexts[sequence_id]

    def _cleanup_old_contexts(self):
        """
        Clean up temporary contexts that are older than a certain threshold to prevent memory buildup
        """
        import time
        current_time = time.time()
        # Keep contexts for up to 1 hour (3600 seconds)
        threshold = current_time - 3600

        # Also limit total number of contexts to prevent memory issues
        if len(self.temporary_contexts) > 1000:  # Arbitrary limit
            # Remove oldest contexts - since we store creation time in sequence_id,
            # we can use that to determine age
            sorted_contexts = sorted(
                self.temporary_contexts.items(),
                key=lambda x: float(x[0].split('_')[-1]) if x[0].split('_')[-1].replace('.', '').isdigit() else 0
            )
            contexts_to_remove = len(self.temporary_contexts) - 500  # Keep 500 most recent
            for i in range(min(contexts_to_remove, len(sorted_contexts))):
                del self.temporary_contexts[sorted_contexts[i][0]]

    @retry_with_backoff(
        stop_attempts=3, wait_min=1, wait_max=10, retryable_exceptions=(Exception,)
    )
    async def generate_sequence(
        self, profile: LinkedInProfile, tone: str = TONE_FRIENDLY
    ) -> OutreachSequence:
        """
        Generate a pain-first LinkedIn outreach sequence.
        Focus: relevance, curiosity, and human tone.
        """

        try:
            # Check if API key is available
            if not config:
                # Return fallback messages if no API key is configured
                logging.warning("No API key configured, returning fallback messages")
                outputs = [
                    "Hi, I noticed your profile and thought we might have some common interests in this field.",
                    "I'm reaching out because I found your recent work interesting and would love to connect.",
                    "Following up on my previous message - would appreciate your thoughts on this topic.",
                    "Thanks for your time. Feel free to reach out if you'd like to discuss further."
                ]
            else:
                # Create a unique key for the agent configuration based on tone
                agent_key = f"outreach_strategist_{tone.lower()}"

                # Check if we have a cached agent for this configuration
                if agent_key not in self.agent_cache:
                    agent = Agent(
                        name="LinkedIn Outreach Strategist",
                        instructions=(
                            "You are an expert at writing LinkedIn DMs that get replies.\n"
                            "Your job is NOT to praise.\n"
                            "Your job is to surface a relevant pain or tension and start a conversation.\n\n"
                            "Rules:\n"
                            "- Do NOT sound salesy\n"
                            "- Do NOT over-compliment\n"
                            "- Avoid buzzwords\n"
                            "- Keep messages human and short\n"
                            "- Sound like a real person who understands the reader\n"
                            "- force single line\n"
                            "- remove leading/trailing quotes\n"
                            f"- Tone: {tone}\n"
                            "- Generate ALL messages in a single response in the specified format\n"
                        ),
                    )
                    # Cache the agent for reuse (with a reasonable size limit)
                    if len(self.agent_cache) < 10:  # Limit cache size
                        self.agent_cache[agent_key] = agent
                else:
                    agent = self.agent_cache[agent_key]

                # Handle both object attributes and dictionary keys
                profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else None)
                profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else None)
                profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else None)

                if (
                    (profile_role is None or not profile_role.strip())
                    or ((profile_company is None or not profile_company.strip())
                        and (profile_industry is None or not profile_industry.strip()))
                ):
                    raise ValueError(
                        "Profile must have role, and either company or industry for generation."
                    )

                context = self._prepare_context_for_generation(profile, tone)

                # Create a temporary sequence context
                sequence_id = f"temp_{profile.id or ''}_{int(time.time())}"
                sequence_context = SequenceContext(
                    sequence_id=sequence_id,
                    previous_messages=[],
                    context_summary="",
                    tone_consistency_log=[],
                    temporary_storage=True
                )

                # Customize instructions based on whether we have a specific pain point
                dm1_instruction = (
                    "Write the first DM after connecting.\n"
                    "- Acknowledge a likely pain or challenge related to their role\n"
                    "- Ask ONE thoughtful question\n"
                    "- No selling, no links\n"
                    "- Under 200 characters"
                )

                if context.get("pain_point"):
                    dm1_instruction = (
                        f"Write the first DM after connecting.\n"
                        f"- Address this specific pain point: {context['pain_point']}\n"
                        f"- Ask ONE thoughtful question related to this pain point\n"
                        f"- No selling, no links\n"
                        f"- Under 200 characters"
                    )

                # Create a single prompt that asks for all messages at once
                prompt = f"""
                Context:
                {json.dumps(context, indent=2)}

                Generate a complete LinkedIn outreach sequence with the following messages:

                1. CONNECTION NOTE: Write a LinkedIn connection request.
                   - One sentence
                   - Light curiosity
                   - NO pitch
                   - Mention role or work only once
                   - Under 180 characters

                2. DM 1: {dm1_instruction}

                3. FOLLOW-UP 1: Write the first follow-up.
                   - Polite nudge
                   - Reframe the pain or curiosity
                   - Assume they are busy, not ignoring
                   - Under 180 characters

                4. FOLLOW-UP 2: Write the final follow-up.
                   - Graceful exit
                   - No pressure
                   - Leave door open for later
                   - Under 180 characters

                FORMAT REQUIREMENTS:
                Respond with exactly this format:
                [CONNECTION_NOTE_START]
                {{connection_note_content}}
                [CONNECTION_NOTE_END]

                [DM_1_START]
                {{dm_1_content}}
                [DM_1_END]

                [FOLLOW_UP_1_START]
                {{follow_up_1_content}}
                [FOLLOW_UP_1_END]

                [FOLLOW_UP_2_START]
                {{follow_up_2_content}}
                [FOLLOW_UP_2_END]

                Do not include any other text or explanations outside of the required format.
                """

                # Apply timeout protection for the single LLM call
                try:
                    result = await llm_timeout_manager.run_with_timeout(
                        Runner.run(agent, input=prompt, run_config=config),
                        timeout=15  # 15-second timeout for single call (more generous than 4x8s)
                    )
                except TimeoutError:
                    logging.warning("Timeout occurred while generating outreach sequence")
                    # Return fallback messages
                    outputs = [
                        "I wanted to connect with you.",
                        "Hi, I noticed your work in this field.",
                        "Following up on my previous message.",
                        "Thanks for your time, hope to connect."
                    ]
                else:
                    text = result.final_output.strip()

                    # Parse the response to extract individual messages
                    outputs = self._parse_sequence_response(text)

                    # If parsing failed, use fallback messages
                    if len(outputs) != 4:
                        logging.warning(f"Failed to parse sequence response, using fallback messages. Response: {text}")
                        outputs = [
                            "I wanted to connect with you.",
                            "Hi, I noticed your work in this field.",
                            "Following up on my previous message.",
                            "Thanks for your time, hope to connect."
                        ]

            # Validate and potentially regenerate each message if needed
            validated_outputs = []
            for i, text in enumerate(outputs):
                if len(text) > 200:
                    text = text[:197] + "..."

                # If API key is available, validate the tone of the generated message
                if config:
                    is_valid, violations = self.tone_validator.validate_message_tone(text, tone)

                    # If tone validation fails, regenerate the message
                    if not is_valid:
                        # Create a regeneration function that incorporates tone feedback
                        def regenerate_message(original_text, requested_tone):
                            regeneration_prompt = f"""
                            Original message: {original_text}

                            Tone validation violations: {', '.join(violations)}

                            Please regenerate the message to better align with the {requested_tone} tone.
                            """
                            regeneration_result = Runner.run(agent, input=regeneration_prompt, run_config=config)
                            regenerated_text = regeneration_result.final_output.strip()

                            if len(regenerated_text) > 200:
                                regenerated_text = regenerated_text[:197] + "..."

                            return regenerated_text

                        # Regenerate the message with tone considerations
                        text, was_regenerated, new_violations = self.tone_validator.validate_and_regenerate_if_needed(
                            text, tone, regenerate_message
                        )

                        # Log the regeneration if it happened
                        if was_regenerated:
                            from utils.logging import log_tone_validation_result
                            log_tone_validation_result(text, tone, True, True)

                validated_outputs.append(text)

            # Create sequence context (even if using fallback)
            sequence_id = f"temp_{profile.id or ''}_{int(time.time())}"
            sequence_context = SequenceContext(
                sequence_id=sequence_id,
                previous_messages=[
                    {"position": i + 1, "role": ["Connection Note", "DM 1", "Follow-up 1", "Follow-up 2"][i], "content": text, "timestamp": time.time()}
                    for i, text in enumerate(validated_outputs)
                ],
                context_summary="Generated outreach sequence",
                tone_consistency_log=[],
                temporary_storage=True
            )

            # Store the temporary context
            self._store_temporary_context(sequence_id, sequence_context)

            # Calculate predicted reply score based on profile context
            predicted_reply_score = self._calculate_predicted_reply_score(profile, tone)

            return OutreachSequence(
                user_id=profile.user_id or "",  # Pass the user_id from the profile
                profile_id=profile.id or "",
                connection_note=validated_outputs[0],
                dm_1=validated_outputs[1],
                follow_up_1=validated_outputs[2],
                follow_up_2=validated_outputs[3],
                tone=tone,
                predicted_reply_score=predicted_reply_score,
                sequence_context=sequence_context.dict()
            )

        except Exception as e:
            logging.error(
                f"Error generating outreach sequence for profile {profile.id}: {e}"
            )
            raise

    def _parse_sequence_response(self, response: str) -> List[str]:
        """
        Parse the LLM response to extract individual messages based on the defined format.
        """
        import re

        # Define the pattern to extract each message
        patterns = [
            r'\[CONNECTION_NOTE_START\](.*?)\[CONNECTION_NOTE_END\]',
            r'\[DM_1_START\](.*?)\[DM_1_END\]',
            r'\[FOLLOW_UP_1_START\](.*?)\[FOLLOW_UP_1_END\]',
            r'\[FOLLOW_UP_2_START\](.*?)\[FOLLOW_UP_2_END\]'
        ]

        outputs = []
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Clean up any extra whitespace or quotes
                content = content.strip().strip('"\'')
                outputs.append(content)
            else:
                # If we can't find the specific tag, try to extract the content differently
                outputs.append("I wanted to reach out and connect with you.")

        return outputs

    def _prepare_context_for_generation(
        self, profile: LinkedInProfile, tone: str
    ) -> Dict[str, Any]:
        """
        Prepare context for message generation
        """
        # Handle both object attributes and dictionary keys
        profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else '')
        profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else '')
        profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else '')
        profile_recent_activity = getattr(profile, 'recent_activity', None) or (profile.get('recent_activity') if isinstance(profile, dict) else '')
        profile_pain_point = getattr(profile, 'pain_point', None) or (profile.get('pain_point') if isinstance(profile, dict) else '')
        profile_url = getattr(profile, 'url', None) or (profile.get('url') if isinstance(profile, dict) else '')

        return {
            "role": profile_role,
            "company": profile_company,
            "industry": profile_industry,
            "recent_activity": profile_recent_activity or "",
            "pain_point": profile_pain_point or "",
            "tone_instruction": self.tone_instructions.get(
                tone, self.tone_instructions[TONE_FRIENDLY]
            ),
            "profile_url": profile_url,
        }

    def _calculate_predicted_reply_score(self, profile: LinkedInProfile, tone: str) -> float:
        """
        Calculate predicted reply score based on profile context completeness and tone
        """
        # Calculate context completeness score (0–4 points)
        completeness = 1  # role is always present
        if getattr(profile, 'company', None): completeness += 1
        if getattr(profile, 'industry', None): completeness += 1
        if getattr(profile, 'recent_activity', None): completeness += 1

        # Tone modifier
        tone_boost = {
            TONE_FRIENDLY: 0.06,
            TONE_DIRECT: 0.01,
            TONE_AUTHORITY: 0.03,
            TONE_CASUAL: 0.05,
        }.get(tone, 0)

        # Base: completeness maps to 0.60–0.82 range
        base = 0.60 + (completeness / 4) * 0.22 + tone_boost

        # Add small deterministic jitter from URL length
        profile_url = getattr(profile, 'url', '') or ''
        url_len = len(''.join(filter(str.isalpha, profile_url)))
        jitter = ((url_len % 17) / 17) * 0.08 - 0.04  # ±4%

        # Ensure score is within bounds
        score = max(0.55, min(0.95, round((base + jitter) * 100) / 100))

        return score

    async def refine_message(
        self,
        sequence: OutreachSequence,
        message_position: int,
        feedback: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> OutreachSequence:
        """
        Refine a specific message in an existing sequence based on feedback using OpenAI Agents
        """
        try:
            # Get the profile for context
            # Note: In a real implementation, you would fetch the profile from the database
            # For now, we'll use placeholder data

            db = get_db()
            profile_data = db.profiles.find_one({"_id": sequence.profile_id})
            profile = LinkedInProfile(
                id=sequence.profile_id,
                url=profile_data.get("url", ""),
                role=profile_data.get("role", ""),
                company=profile_data.get("company", ""),
                industry=profile_data.get("industry", ""),
                recent_activity=profile_data.get("recent_activity", ""),
                pain_point=profile_data.get("pain_point", ""),
            )

            # Prepare context
            context = self._prepare_context_for_generation(
                profile, tone or sequence.tone
            )

            # Add feedback to context if provided
            if feedback:
                context["feedback"] = feedback

            # Create an agent for refining messages
            agent = Agent(
                name="LinkedIn Outreach Refinement Specialist",
                instructions=f"Refine a LinkedIn outreach message with a {tone if tone else sequence.tone} tone based on feedback. You are an expert at refining LinkedIn outreach messages based on user feedback while maintaining consistency with the overall sequence.",
            )

            # Determine which message to refine
            message_types = {
                1: "connection_note",
                2: "dm_1",
                3: "follow_up_1",
                4: "follow_up_2",
            }

            if message_position not in message_types:
                raise ValueError(
                    f"Invalid message position: {message_position}. Must be 1-4."
                )

            message_type = message_types[message_position]

            # Include the entire sequence context to maintain consistency
            sequence_context = {
                "connection_note": sequence.connection_note,
                "dm_1": sequence.dm_1,
                "follow_up_1": sequence.follow_up_1,
                "follow_up_2": sequence.follow_up_2,
            }

            # Get the temporary context if it exists
            temp_context = None
            if sequence.id:
                temp_context = self._retrieve_temporary_context(sequence.id)

            # Create a description for refining the specific message
            description = f"""
            Refine this LinkedIn {message_type.replace('_', ' ')} based on the following context:
            {json.dumps(context)}

            Current message: {getattr(sequence, message_type)}

            Entire sequence for consistency reference:
            {json.dumps(sequence_context)}

            Previous messages in the sequence (for context and cohesion):
            {json.dumps(temp_context.previous_messages if temp_context else [], indent=2)}

            Tone: {self.tone_instructions[tone or sequence.tone]}

            Keep it under 200 characters.
            """

            # Execute
            result = await Runner.run(agent, input=description, run_config=config)
            refined_message = result.final_output.strip()

            # Ensure the message is under 200 characters
            if len(refined_message) > 200:
                refined_message = refined_message[:197] + "..."

            # Validate the tone of the refined message
            target_tone = tone if tone else sequence.tone
            is_valid, violations = self.tone_validator.validate_message_tone(refined_message, target_tone)

            # Update the specific message in the sequence
            setattr(sequence, message_type, refined_message)

            # Update the temporary context if it exists
            if temp_context:
                # Find the message in the previous_messages and update it
                for msg in temp_context.previous_messages:
                    if msg.get('position') == message_position:
                        msg['content'] = refined_message
                        msg['updated'] = True
                        break
                # Store the updated context
                self._store_temporary_context(sequence.id, temp_context)

                # Update the tone consistency log for the refined message
                for log_entry in temp_context.tone_consistency_log:
                    if log_entry.get('position') == message_position:
                        log_entry['violations'] = violations if not is_valid else []
                        log_entry['regenerated'] = not is_valid
                        break

            # Update the status to indicate refinement
            sequence.status = "REFINED"

            # Update the timestamp
            sequence.updated_at = type(sequence).updated_at(None)

            return sequence
        except Exception as e:
            logging.error(f"Error refining message in sequence {sequence.id}: {e}")
            raise

    def persist_sequence_context(self, sequence_id: str, sequence_data: Dict[str, Any]):
        """
        Persist valuable sequence context to the database
        """
        try:
            temp_context = self._retrieve_temporary_context(sequence_id)
            if temp_context:
                # Update the temporary storage flag
                temp_context.temporary_storage = False

                # Update the sequence in the database with the context
                db = get_db()
                db.sequences.update_one(
                    {"_id": sequence_data.get("_id")},
                    {"$set": {"sequence_context": temp_context.dict()}}
                )

                # Remove from temporary storage
                self._remove_temporary_context(sequence_id)

                return True
        except Exception as e:
            logging.error(f"Error persisting sequence context for sequence {sequence_id}: {e}")
            return False

    def get_sequence_context(self, sequence_id: str) -> Optional[SequenceContext]:
        """
        Get sequence context either from temporary storage or database
        """
        # First check temporary storage
        temp_context = self._retrieve_temporary_context(sequence_id)
        if temp_context:
            return temp_context

        # Then check database
        try:
            db = get_db()
            sequence_data = db.sequences.find_one({"_id": sequence_id})
            if sequence_data and sequence_data.get("sequence_context"):
                return SequenceContext(**sequence_data["sequence_context"])
        except Exception as e:
            logging.error(f"Error retrieving sequence context from database for {sequence_id}: {e}")

        return None
