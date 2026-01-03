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
from database.mongo import mongodb
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
        Generate a complete LinkedIn outreach sequence based on profile context using OpenAI Agents
        """
        try:
            # Create an agent for generating outreach sequences
            agent = Agent(
                name="LinkedIn Outreach Specialist",
                instructions=f"Generate a complete LinkedIn outreach sequence with a {tone.value} tone. You are an expert at crafting personalized LinkedIn outreach messages that are effective and appropriate for the platform.",
            )

            # Prepare context for the agent
            context = self._prepare_context_for_generation(profile, tone)

            # Define descriptions for each message in the sequence
            descriptions = [
                f"Generate a connection request message based on: {json.dumps(context)}. Tone: {self.tone_instructions[tone]}. Keep it under 200 characters.",
                f"Generate the first direct message based on: {json.dumps(context)}. Tone: {self.tone_instructions[tone]}. Keep it under 200 characters.",
                f"Generate the first follow-up message based on: {json.dumps(context)}. Tone: {self.tone_instructions[tone]}. Keep it under 200 characters.",
                f"Generate the second follow-up message based on: {json.dumps(context)}. Tone: {self.tone_instructions[tone]}. Keep it under 200 characters.",
            ]

            # Execute the descriptions using the agent
            results = []
            for desc in descriptions:
                result = await Runner.run(agent, input=desc, run_config=config)
                message_content = result.final_output.strip()
                # Ensure the message is under 200 characters
                if len(message_content) > 200:
                    message_content = message_content[:197] + "..."
                results.append(message_content)

            # Create the outreach sequence
            sequence = OutreachSequence(
                profile_id=profile.id or "",
                connection_note=results[0],
                dm_1=results[1],
                follow_up_1=results[2],
                follow_up_2=results[3],
                tone=tone.value,
            )

            return sequence
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

            db = mongodb.get_database()
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
