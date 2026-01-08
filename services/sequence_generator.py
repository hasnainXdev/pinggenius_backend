from models.sequence import OutreachSequence, Message
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
from enum import Enum
import logging
import json
import os

set_tracing_disabled(True)

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


class Tone(str, Enum):
    FRIENDLY = "Friendly"
    DIRECT = "Direct"
    AUTHORITY = "Authority"
    CASUAL = "Casual"


class SequenceGeneratorService:
    """
    Service for generating LinkedIn outreach sequences using OpenAI Agents
    """

    def __init__(self):
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        self.tone_instructions = {
            Tone.FRIENDLY: "Write in a warm, conversational tone that feels approachable and friendly.",
            Tone.DIRECT: "Write in a clear, straightforward tone that gets to the point efficiently.",
            Tone.AUTHORITY: "Write in a confident, expert-led tone that demonstrates knowledge and credibility.",
            Tone.CASUAL: "Write in a relaxed, natural tone that feels informal and easy-going.",
        }

    @retry_with_backoff(
        stop_attempts=3, wait_min=1, wait_max=10, retryable_exceptions=(Exception,)
    )
    async def generate_sequence(
        self, profile: LinkedInProfile, tone: Tone = Tone.FRIENDLY
    ) -> OutreachSequence:
        """
        Generate a pain-first LinkedIn outreach sequence.
        Focus: relevance, curiosity, and human tone.
        """

        try:
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
                    f"- Tone: {tone.value}\n"
                ),
            )

            if (profile.role is None) or (profile.company is None) or (profile.industry is None):
                raise ValueError(
                    "Profile must have role, company, and industry for generation."
                )

            context = self._prepare_context_for_generation(profile, tone)

            prompts = [
                {
                    "role": "Connection Note",
                    "instruction": (
                        "Write a LinkedIn connection request.\n"
                        "- One sentence\n"
                        "- Light curiosity\n"
                        "- NO pitch\n"
                        "- Mention role or work only once\n"
                        "- Under 180 characters"
                    ),
                },
                {
                    "role": "DM 1",
                    "instruction": (
                        "Write the first DM after connecting.\n"
                        "- Acknowledge a likely pain or challenge related to their role\n"
                        "- Ask ONE thoughtful question\n"
                        "- No selling, no links\n"
                        "- Under 200 characters"
                    ),
                },
                {
                    "role": "Follow-up 1",
                    "instruction": (
                        "Write the first follow-up.\n"
                        "- Polite nudge\n"
                        "- Reframe the pain or curiosity\n"
                        "- Assume they are busy, not ignoring\n"
                        "- Under 180 characters"
                    ),
                },
                {
                    "role": "Follow-up 2",
                    "instruction": (
                        "Write the final follow-up.\n"
                        "- Graceful exit\n"
                        "- No pressure\n"
                        "- Leave door open for later\n"
                        "- Under 180 characters"
                    ),
                },
            ]

            outputs: List[str] = []

            for step in prompts:
                prompt = f"""
            Context:
                {json.dumps(context)}

                Task: {step['role']}
                Instructions:
                {step['instruction']}

            Write the message now.
            """

                result = await Runner.run(agent, input=prompt, run_config=config)
                text = result.final_output.strip()

                if len(text) > 200:
                    text = text[:197] + "..."

                outputs.append(text)

            return OutreachSequence(
                profile_id=profile.id or "",
                connection_note=outputs[0],
                dm_1=outputs[1],
                follow_up_1=outputs[2],
                follow_up_2=outputs[3],
                tone=tone.value,
            )

        except Exception as e:
            logging.error(
                f"Error generating outreach sequence for profile {profile.id}: {e}"
            )
            raise

    def _prepare_context_for_generation(
        self, profile: LinkedInProfile, tone: Tone
    ) -> Dict[str, Any]:
        """
        Prepare context for message generation
        """
        return {
            "role": profile.role,
            "company": profile.company,
            "industry": profile.industry,
            "recent_activity": profile.recent_activity or "",
            "tone_instruction": self.tone_instructions.get(
                tone, self.tone_instructions[Tone.FRIENDLY]
            ),
            "profile_url": profile.url,
        }

    async def refine_message(
        self,
        sequence: OutreachSequence,
        message_position: int,
        feedback: Optional[str] = None,
        tone: Optional[Tone] = None,
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
            )

            # Prepare context
            context = self._prepare_context_for_generation(
                profile, tone or Tone(sequence.tone)
            )

            # Add feedback to context if provided
            if feedback:
                context["feedback"] = feedback

            # Create an agent for refining messages
            agent = Agent(
                name="LinkedIn Outreach Refinement Specialist",
                instructions=f"Refine a LinkedIn outreach message with a {tone.value if tone else sequence.tone} tone based on feedback. You are an expert at refining LinkedIn outreach messages based on user feedback while maintaining consistency with the overall sequence.",
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

            # Create a description for refining the specific message
            description = f"""
            Refine this LinkedIn {message_type.replace('_', ' ')} based on the following context:
            {json.dumps(context)}

            Current message: {getattr(sequence, message_type)}

            Entire sequence for consistency reference:
            {json.dumps(sequence_context)}

            Tone: {self.tone_instructions[tone or Tone(sequence.tone)]}

            Keep it under 200 characters.
            """

            # Execute
            result = await Runner.run(agent, input=description, run_config=config)
            refined_message = result.final_output.strip()

            # Ensure the message is under 200 characters
            if len(refined_message) > 200:
                refined_message = refined_message[:197] + "..."

            # Update the specific message in the sequence
            setattr(sequence, message_type, refined_message)

            # Update the status to indicate refinement
            sequence.status = "REFINED"

            # Update the timestamp
            sequence.updated_at = type(sequence).updated_at(None)

            return sequence
        except Exception as e:
            logging.error(f"Error refining message in sequence {sequence.id}: {e}")
            raise
