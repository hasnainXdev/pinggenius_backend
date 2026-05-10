from models.sequence import OutreachSequence
from models.profile import LinkedInProfile
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
import logging
import json
import os
import time

from services.tone_validator import ToneValidatorService
from utils.timeout_manager import llm_timeout_manager

set_tracing_disabled(True)

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
    config = RunConfig(model=model, model_provider=gemini_client)
else:
    logging.warning("Gemini API key not configured. Using fallback responses.")


TONE_FRIENDLY = "Friendly"
TONE_DIRECT = "Direct"
TONE_AUTHORITY = "Authority"
TONE_CASUAL = "Casual"

VALID_TONES = [TONE_FRIENDLY, TONE_DIRECT, TONE_AUTHORITY, TONE_CASUAL]


class SequenceGeneratorService:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        self.tone_instructions = {
            TONE_FRIENDLY: "Write in a warm, conversational tone that feels approachable and friendly.",
            TONE_DIRECT: "Write in a clear, straightforward tone that gets to the point efficiently.",
            TONE_AUTHORITY: "Write in a confident, expert-led tone that demonstrates knowledge and credibility.",
            TONE_CASUAL: "Write in a relaxed, natural tone that feels informal and easy-going.",
        }
        self.tone_validator = ToneValidatorService()

    @retry_with_backoff(
        stop_attempts=3, wait_min=1, wait_max=10, retryable_exceptions=(Exception,)
    )
    async def generate_sequence(
        self, profile: LinkedInProfile, tone: str = TONE_FRIENDLY
    ) -> OutreachSequence:
        try:
            if not config:
                logging.warning("No API key configured, returning fallback messages")
                outputs = [
                    "Hi, I noticed your profile and thought we might have some common interests in this field.",
                    "I'm reaching out because I found your recent work interesting and would love to connect.",
                    "Following up on my previous message - would appreciate your thoughts on this topic.",
                    "Thanks for your time. Feel free to reach out if you'd like to discuss further."
                ]
            else:
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

                profile_role = getattr(profile, 'role', None) or (profile.get('role') if isinstance(profile, dict) else None)
                profile_company = getattr(profile, 'company', None) or (profile.get('company') if isinstance(profile, dict) else None)
                profile_industry = getattr(profile, 'industry', None) or (profile.get('industry') if isinstance(profile, dict) else None)

                if (
                    (profile_role is None or not profile_role.strip())
                    or ((profile_company is None or not profile_company.strip())
                        and (profile_industry is None or not profile_industry.strip()))
                ):
                    raise ValueError("Profile must have role, and either company or industry for generation.")

                context = self._prepare_context_for_generation(profile, tone)

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

                try:
                    result = await llm_timeout_manager.run_with_timeout(
                        Runner.run(agent, input=prompt, run_config=config),
                        timeout=15
                    )
                except Exception:
                    logging.warning("Timeout occurred while generating outreach sequence")
                    outputs = [
                        "I wanted to connect with you.",
                        "Hi, I noticed your work in this field.",
                        "Following up on my previous message.",
                        "Thanks for your time, hope to connect."
                    ]
                else:
                    outputs = self._parse_sequence_response(result.final_output.strip())
                    if len(outputs) != 4:
                        logging.warning("Failed to parse sequence response, using fallback messages.")
                        outputs = [
                            "I wanted to connect with you.",
                            "Hi, I noticed your work in this field.",
                            "Following up on my previous message.",
                            "Thanks for your time, hope to connect."
                        ]

            validated_outputs = []
            for text in outputs:
                if len(text) > 200:
                    text = text[:197] + "..."
                if config:
                    is_valid, violations = self.tone_validator.validate_message_tone(text, tone)
                    if not is_valid:
                        def regenerate_message(original_text, requested_tone):
                            regen_prompt = f"Original message: {original_text}\nTone violations: {', '.join(violations)}\nRegenerate to better align with {requested_tone} tone."
                            regen_result = Runner.run(agent, input=regen_prompt, run_config=config)
                            regenerated = regen_result.final_output.strip()
                            return regenerated[:197] + "..." if len(regenerated) > 200 else regenerated

                        text, was_regenerated, _ = self.tone_validator.validate_and_regenerate_if_needed(
                            text, tone, regenerate_message
                        )
                        if was_regenerated:
                            from utils.logging import log_tone_validation_result
                            log_tone_validation_result(text, tone, True, True)
                validated_outputs.append(text)

            return OutreachSequence(
                user_id=profile.user_id or "",
                profile_id=profile.id or "",
                connection_note=validated_outputs[0],
                dm_1=validated_outputs[1],
                follow_up_1=validated_outputs[2],
                follow_up_2=validated_outputs[3],
                tone=tone,
                predicted_reply_score=self._calculate_predicted_reply_score(profile, tone),
            )

        except Exception as e:
            logging.error(f"Error generating outreach sequence for profile {profile.id}: {e}")
            raise

    def _parse_sequence_response(self, response: str) -> List[str]:
        import re
        patterns = [
            r'\[CONNECTION_NOTE_START\](.*?)\[CONNECTION_NOTE_END\]',
            r'\[DM_1_START\](.*?)\[DM_1_END\]',
            r'\[FOLLOW_UP_1_START\](.*?)\[FOLLOW_UP_1_END\]',
            r'\[FOLLOW_UP_2_START\](.*?)\[FOLLOW_UP_2_END\]'
        ]
        outputs = []
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            outputs.append(match.group(1).strip().strip('"\'') if match else "I wanted to reach out and connect with you.")
        return outputs

    def _prepare_context_for_generation(self, profile: LinkedInProfile, tone: str) -> Dict[str, Any]:
        def _get(attr):
            return getattr(profile, attr, None) or (profile.get(attr) if isinstance(profile, dict) else '') or ''

        return {
            "role": _get('role'),
            "company": _get('company'),
            "industry": _get('industry'),
            "recent_activity": _get('recent_activity'),
            "pain_point": _get('pain_point'),
            "tone_instruction": self.tone_instructions.get(tone, self.tone_instructions[TONE_FRIENDLY]),
            "profile_url": _get('url'),
        }

    def _calculate_predicted_reply_score(self, profile: LinkedInProfile, tone: str) -> float:
        completeness = 1
        if getattr(profile, 'company', None): completeness += 1
        if getattr(profile, 'industry', None): completeness += 1
        if getattr(profile, 'recent_activity', None): completeness += 1

        tone_boost = {TONE_FRIENDLY: 0.06, TONE_DIRECT: 0.01, TONE_AUTHORITY: 0.03, TONE_CASUAL: 0.05}.get(tone, 0)
        base = 0.60 + (completeness / 4) * 0.22 + tone_boost

        profile_url = getattr(profile, 'url', '') or ''
        url_len = len(''.join(filter(str.isalpha, profile_url)))
        jitter = ((url_len % 17) / 17) * 0.08 - 0.04

        return max(0.55, min(0.95, round((base + jitter) * 100) / 100))

    async def refine_message(
        self,
        sequence: OutreachSequence,
        message_position: int,
        feedback: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> OutreachSequence:
        try:
            db = await get_db()
            profile_data = await db.profiles.find_one({"_id": sequence.profile_id})
            profile = LinkedInProfile(
                id=sequence.profile_id,
                url=profile_data.get("url", ""),
                role=profile_data.get("role", ""),
                company=profile_data.get("company", ""),
                industry=profile_data.get("industry", ""),
                recent_activity=profile_data.get("recent_activity", ""),
                pain_point=profile_data.get("pain_point", ""),
            )

            context = self._prepare_context_for_generation(profile, tone or sequence.tone)
            if feedback:
                context["feedback"] = feedback

            agent = Agent(
                name="LinkedIn Outreach Refinement Specialist",
                instructions=f"Refine a LinkedIn outreach message with a {tone if tone else sequence.tone} tone based on feedback.",
            )

            message_types = {1: "connection_note", 2: "dm_1", 3: "follow_up_1", 4: "follow_up_2"}
            if message_position not in message_types:
                raise ValueError(f"Invalid message position: {message_position}. Must be 1-4.")

            message_type = message_types[message_position]
            sequence_context = {
                "connection_note": sequence.connection_note,
                "dm_1": sequence.dm_1,
                "follow_up_1": sequence.follow_up_1,
                "follow_up_2": sequence.follow_up_2,
            }

            description = f"""
            Refine this LinkedIn {message_type.replace('_', ' ')} based on the following context:
            {json.dumps(context)}

            Current message: {getattr(sequence, message_type)}

            Entire sequence for consistency reference:
            {json.dumps(sequence_context)}

            Tone: {self.tone_instructions[tone or sequence.tone]}

            Keep it under 200 characters.
            """

            result = await Runner.run(agent, input=description, run_config=config)
            refined_message = result.final_output.strip()
            if len(refined_message) > 200:
                refined_message = refined_message[:197] + "..."

            setattr(sequence, message_type, refined_message)
            sequence.status = "REFINED"
            sequence.updated_at = type(sequence).updated_at(None)

            return sequence
        except Exception as e:
            logging.error(f"Error refining message in sequence {sequence.id}: {e}")
            raise
