from models.profile import LinkedInProfile
from typing import Optional
import logging


class ProfileService:
    def __init__(self):
        pass

    async def analyze_profile(self, profile_data: dict) -> Optional[LinkedInProfile]:
        return self._create_profile_from_data(profile_data)

    def _create_profile_from_data(self, profile_data: dict) -> LinkedInProfile:
        try:
            url = profile_data.get('url', '')
            if not url.startswith("https://www.linkedin.com/in/"):
                raise ValueError("Invalid LinkedIn profile URL")
            return LinkedInProfile(
                url=url,
                role=profile_data.get('role', ''),
                company=profile_data.get('company', ''),
                industry=profile_data.get('industry', ''),
                recent_activity=profile_data.get('recent_activity'),
                tone=profile_data.get('tone', 'Friendly')
            )
        except Exception as e:
            logging.error(f"Error creating profile from data: {e}")
            raise

    def validate_profile_url(self, url: str) -> bool:
        return url.startswith("https://www.linkedin.com/in/")
