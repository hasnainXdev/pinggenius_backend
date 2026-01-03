from models.profile import LinkedInProfile
from typing import Dict, Any
import logging


class ContextExtractor:
    """
    Extracts relevant context from LinkedIn profile data for message generation
    """

    def extract_context(self, profile: LinkedInProfile) -> Dict[str, Any]:
        """
        Extract context from a LinkedIn profile for message generation
        """
        try:
            context = {
                "profile_url": profile.url,
                "role": profile.role,
                "company": profile.company,
                "industry": profile.industry,
                "recent_activity": profile.recent_activity,
                "person_name": self._extract_name_from_url(profile.url),
            }

            return context
        except Exception as e:
            logging.error(f"Error extracting context from profile {profile.id}: {e}")
            raise

    def _extract_name_from_url(self, url: str) -> str:
        """
        Extract the person's name from the LinkedIn profile URL
        """
        try:
            # LinkedIn URLs are in the format: https://www.linkedin.com/in/{name}
            name_part = url.rstrip("/").split("/")[-1]
            # Replace hyphens with spaces and title case
            name = name_part.replace("-", " ").title()
            return name
        except Exception:
            # If URL parsing fails, return a generic name
            return "LinkedIn User"

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate that the extracted context has the required fields for message generation
        """
        required_fields = ["role", "company", "industry"]
        for field in required_fields:
            if not context.get(field) or context[field] == "Unknown":
                return False
        return True
